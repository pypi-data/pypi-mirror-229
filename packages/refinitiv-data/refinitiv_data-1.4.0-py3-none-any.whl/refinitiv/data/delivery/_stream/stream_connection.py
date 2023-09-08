import os
import queue
import threading
import traceback
from collections import defaultdict, Counter
from typing import Callable, Dict, List, Optional, TYPE_CHECKING, Union, Tuple

import websocket

from .event import StreamCxnEvent
from .rwf.socket import RwfSocketClient
from .stream_cxn_state import StreamCxnState
from .ws.ws_client import WebSocketClient
from ..._core.log_reporter import LogReporter
from ..._core.session.tools import is_desktop_session
from ..._tools import DEBUG, CallbackHandler, lazy_dump, lazy_formatting, get_delays
from ...usage_collection import LogRecord, RecordData, FilterType, get_usage_logger

if TYPE_CHECKING:
    from ._stream_cxn_config_data import StreamCxnConfig
    from ..._core.session import Session

LOGIN_STREAM_ID = 2


class StreamConnection(threading.Thread, LogReporter):
    _listener: Optional[Union[WebSocketClient, RwfSocketClient]] = None
    _num_attempt = 0

    def __init__(
        self,
        connection_id: int,
        name: str,
        session: "Session",
        config: "StreamCxnConfig",
    ) -> None:
        self._id: int = connection_id
        self._session: "Session" = session
        self._config: "StreamCxnConfig" = config

        LogReporter.__init__(self, logger=session.logger())
        threading.Thread.__init__(self, name=f"Thread{name}", daemon=True)

        self._state: StreamCxnState = StreamCxnState.Initial
        self._is_emit_reconnected: bool = False
        self._is_auto_reconnect: bool = self._session.stream_auto_reconnection
        self._start_connecting = threading.Event()
        self._connection_result_ready = threading.Event()
        self._listener_created = threading.Event()
        self._timer = threading.Event()

        self.usage_counter = defaultdict(Counter)
        self._usage_close_event = threading.Event()
        self._usage_report_thread = threading.Thread(target=self._usage_callback, args=(10,))
        self._usage_lock = threading.Lock()
        self._dispose_lock = threading.Lock()

        self._emitter = CallbackHandler()
        self._msg_queue: Optional[queue.Queue] = None
        self._msg_processor: Optional[threading.Thread] = None
        self._delays = get_delays()

        self._classname: str = f"[{name}]"

    @property
    def session(self) -> "Session":
        return self._session

    @property
    def id(self) -> int:
        return self._id

    @property
    def api_cfg_key(self) -> str:
        return self._config.api_cfg_key

    @property
    def subprotocol(self) -> str:
        return ""

    @property
    def state(self) -> StreamCxnState:
        return self._state

    @property
    def is_connecting(self) -> bool:
        return self.state is StreamCxnState.Connecting

    @property
    def is_message_processing(self) -> bool:
        return self.state is StreamCxnState.MessageProcessing

    @property
    def is_disconnecting(self) -> bool:
        return self.state is StreamCxnState.Disconnecting

    @property
    def is_disconnected(self) -> bool:
        return self.state is StreamCxnState.Disconnected

    @property
    def is_disposed(self) -> bool:
        return self.state is StreamCxnState.Disposed

    @property
    def can_reconnect(self) -> bool:
        return self._is_auto_reconnect and self._config.has_available_info()

    def wait_start_connecting(self):
        msg = "clear start_connecting event"
        if self.is_disposed:
            self.debug(f"{self._classname} cannot {msg}, {self.state}")
            return

        self.debug(f"{self._classname} {msg}")
        self._start_connecting.clear()

    def start_connecting(self):
        msg = "set start_connecting event"
        if self.is_disposed:
            self.debug(f"{self._classname} cannot {msg}, {self.state}")
            return

        self.debug(f"{self._classname} {msg}")
        self._start_connecting.set()

    def wait_start(self):
        if self.is_disposed:
            self.debug(f"{self._classname} cannot wait start, {self.state}")
            return

        self.start()
        self._listener_created.wait()

    def wait_connection_result(self):
        if self.is_disposed:
            self.debug(f"{self._classname} cannot wait connection result, {self.state}")
            return

        self._connection_result_ready.wait()

    def run(self) -> None:
        self._msg_queue = queue.Queue()
        self._msg_processor = threading.Thread(target=self._process_messages, name=f"Msg-Proc-{self.name}", daemon=True)
        self._usage_report_thread.start()
        self._msg_processor.start()

        once = False
        self._start_connecting.set()
        while not once or self.can_reconnect:
            once = True

            if self.is_disposed:
                break

            self.debug(f"{self._classname} wait start connecting")
            self._start_connecting.wait()

            self.debug(f"{self._classname} is connecting")
            self._state = StreamCxnState.Connecting
            self._emitter.emit(StreamCxnEvent.CONNECTING, self)

            if self._config.transport == "tcp":
                self._run_tcp_listener()
            else:
                self._run_websocket_listener()

            if self.is_disposed:
                break

            self._state = StreamCxnState.Disconnected
            self._listener_created.clear()
            not self.can_reconnect and self._connection_result_ready.set()

            if self.can_reconnect:
                self._connection_result_ready.clear()
                self._emitter.emit(StreamCxnEvent.RECONNECTING, self)
                self._start_connecting.wait()
                self._is_emit_reconnected = True

                try:
                    self._config.next_available_info()
                except StopIteration:
                    delay = self._delays.next()
                    self.debug(f"{self._classname} tried all infos, waiting time {delay} secs until the next attempt.")
                    self._timer.wait(delay)
                    self._num_attempt += 1

                url = self._config.url
                self.debug(f"{self._classname} try to reconnect over url {url}")

        self.dispose()

    def _run_tcp_listener(self):
        def on_open(app):
            self._on_ws_open(app)
            self._state = StreamCxnState.MessageProcessing
            self._connection_result_ready.set()

        host, port = self._config.url.split(":")
        port = int(port) if port else None

        cfg = self._session.config
        cfg_prefix = "apis.streaming.pricing"
        field_dict_path = cfg.get(f"{cfg_prefix}.field_dict_path")
        enumtype_path = cfg.get(f"{cfg_prefix}.enumtype_path")

        self.debug(
            f"{self._classname} connect\n"
            f"\tnum_attempt = {self._num_attempt}\n"
            f"\turl = {self._config.url}\n"
            f"\ttransport   = {self._config.transport}\n"
        )

        self._listener = RwfSocketClient(
            host=host,
            port=port,
            field_dict_path=field_dict_path,
            enumtype_path=enumtype_path,
            on_open=on_open,
            on_message=self._on_message,
            on_close=self._on_ws_close,
            session=self._session,
        )
        self._listener_created.set()
        self._listener.run_forever()

    def _run_websocket_listener(self):
        DEBUG and websocket.enableTrace(True)

        cookie = None
        user_id = os.getenv("REFINITIV_AAA_USER_ID")
        if is_desktop_session(self._session) and user_id:
            cookie = f"user-uuid={user_id}"

        headers = ["User-Agent: Python"] + self._config.headers
        subprotocols = [self.subprotocol]

        self.debug(
            f"{self._classname} connect\n"
            f"\tnum_attempt : {self._num_attempt}\n"
            f"\turl         : {self._config.url}\n"
            f"\theaders     : {headers}\n"
            f"\tcookies     : {cookie}\n"
            f"\ttransport   : {self._config.transport}\n"
            f"\tsubprotocols: {subprotocols}"
        )

        self._listener = WebSocketClient(
            url=self._config.url,
            header=headers,
            cookie=cookie,
            on_open=self._on_ws_open,
            on_message=self._on_message,
            on_error=self._on_ws_error,
            on_close=self._on_ws_close,
            on_ping=self._on_ws_ping,
            on_pong=self._on_ws_pong,
            subprotocols=subprotocols,
        )
        self._listener_created.set()
        proxy_config = self._config.proxy_config
        http_proxy_host = None
        http_proxy_port = None
        http_proxy_auth = None
        proxy_type = None
        if proxy_config:
            http_proxy_host = proxy_config.host
            http_proxy_port = proxy_config.port
            http_proxy_auth = proxy_config.auth
            proxy_type = proxy_config.type

        no_proxy = self._config.no_proxy

        self._listener.run_forever(
            http_proxy_host=http_proxy_host,
            http_proxy_port=http_proxy_port,
            http_proxy_auth=http_proxy_auth,
            http_no_proxy=no_proxy,
            proxy_type=proxy_type,
            skip_utf8_validation=True,
        )

    def start_disconnecting(self) -> None:
        if not self.is_message_processing:
            self.debug(f"{self._classname} cannot start disconnecting, {self.state}")
            return

        self.debug(f"{self._classname} is start disconnecting [dis]")
        self._state = StreamCxnState.Disconnecting
        self._connection_result_ready.clear()
        self._start_connecting.clear()
        self._emitter.emit(StreamCxnEvent.DISCONNECTING, self)

    def end_disconnecting(self):
        if self.is_disposed:
            self.debug(f"{self._classname} cannot end disconnecting, {self.state}")
            return

        if self.is_disconnecting:
            self._state = StreamCxnState.Disconnected
            self._start_connecting.clear()
        else:
            self.debug(f"{self._classname} cannot end disconnecting, {self.state}")

    def dispose(self) -> None:
        if self.is_disposed or self.is_message_processing:
            self.debug(f"{self._classname} cannot dispose, {self.state}")
            return

        with self._dispose_lock:
            self.debug(f"{self._classname} is disposing [d], {self.state}")
            self._state = StreamCxnState.Disposed

            close_message = self.get_close_message()
            if close_message and not self.is_connecting:
                self.send_message(close_message)

            self._listener_created.set()
            self._listener_created = None
            self._listener.close()
            self._listener = None

            self._usage_close_event.set()
            self._usage_report_thread.join(5)
            self._msg_queue.put("__dispose__")
            self._msg_processor = None
            self._start_connecting = None
            self._connection_result_ready.set()
            self._connection_result_ready = None
            self._emitter.emit(StreamCxnEvent.DISPOSED, self)
            self._emitter = None
            self.debug(f"{self._classname} disposed [D]")

    def get_login_message(self) -> dict:
        # for override
        pass

    def get_close_message(self) -> dict:
        # for override
        pass

    def send_login_message(self) -> bool:
        if self.is_message_processing:
            self.send_message(self.get_login_message())
            return True
        else:
            self.debug(f"{self._classname} cannot send login message, state={self.state}")
            return False

    def send_message(self, message: dict) -> bool:
        if self.is_message_processing:
            self.debug(f"{self._classname} send %s", lazy_dump(message))
            self._listener.send(message)
            return True
        else:
            self.debug(f"{self._classname} cannot send message: state={self.state}, message=%s", lazy_dump(message))
            return False

    def on(self, event: str, listener: Callable) -> None:
        if self.is_disposed:
            self.debug(f"{self._classname} cannot on, {self.state}")
            return

        self._emitter.on(event, listener)

    def remove_listener(self, event: str, listener: Callable) -> None:
        if self.is_disposed:
            self.debug(f"{self._classname} {self.state}, can not remove listener {event}, {listener}")
            return

        self._emitter.remove_listener(event, listener)

    def _on_ws_open(self, ws: websocket.WebSocketApp) -> None:
        self.debug(f"{self._classname} on_ws_open")
        self._delays.reset()
        self._emitter.emit(StreamCxnEvent.CONNECTED, self)
        message = self.get_login_message()
        self.debug(f"{self._classname} send login message {message}")
        self._listener.send(message)

    def _on_message(self, messages: List[Dict]) -> None:
        self.debug(f"{self._classname} on_ws_message %s", lazy_dump(messages))

        if self.is_connecting:
            if len(messages) > 1:
                raise ValueError(f"Cannot process messages more then one, num={len(messages)}")

            message = messages[0]
            self._handle_login_message(message)

            if self._is_emit_reconnected:
                self.debug("Reconnecting is over, emit event Reconnected.")
                self._is_emit_reconnected = False
                self._emitter.emit(StreamCxnEvent.RECONNECTED, self)

        elif self.is_message_processing:
            self._msg_queue.put(messages)

        elif self.is_disconnecting:
            # do nothing and wait for all streams to close
            pass

        else:
            debug_msg = lazy_formatting(
                f"{self._classname}._on_ws_message() | don't know what to do state={self.state}, message=%s",
                lazy_dump(messages),
            )

            if DEBUG:
                raise ValueError(debug_msg)

            else:
                self.debug(debug_msg)

    def _handle_login_message(self, message: dict):
        # for override
        pass

    def _process_messages(self) -> None:
        while not self.is_disposed:
            messages: List[Dict] = self._msg_queue.get()

            if messages == "__dispose__" and self.is_disposed:
                break

            for message in messages:
                self._process_message(message)

            self._msg_queue.task_done()

    def _process_message(self, message: dict) -> None:
        # for override
        pass

    def _on_ws_close(self, ws: websocket.WebSocketApp, close_status_code: str, close_msg: str) -> None:
        self.debug(
            f"{self._classname} on_ws_close: "
            f"close_status_code={close_status_code}, close_msg={close_msg}, "
            f"state={self.state}"
        )
        self._emitter and self._emitter.emit(StreamCxnEvent.DISCONNECTED, self)
        if not self.is_disposed:
            self._listener_created.clear()

    def _on_ws_error(self, ws: websocket.WebSocketApp, exc: Exception) -> None:
        self.error(f"{self._classname} on_ws_error: Exception: {exc}")
        DEBUG and self.debug(f"{traceback.format_exc()}")
        if not self.session.server_mode and isinstance(exc, websocket.WebSocketAddressException):
            self._config.info_not_available()

    def _on_ws_ping(self, message: dict) -> None:
        self.debug(f"{self._classname} ping {message}")

    def _on_ws_pong(self, ws, message: dict) -> None:
        self.debug(f"{self._classname} pong {message}")

    def _get_socket_info(self) -> Tuple[str, str]:
        return self._listener.get_socket_info()

    def _dump_usage_data(self) -> None:
        if self.usage_counter:
            with self._usage_lock:
                data_to_log = self.usage_counter
                self.usage_counter = defaultdict(Counter)
            get_usage_logger().log(
                LogRecord(
                    name="stream_usage",
                    func_path="stream_usage",
                    data=RecordData(result=data_to_log),
                    filter={FilterType.STREAM},
                )
            )

    def _usage_callback(self, interval: int) -> None:
        while not self._usage_close_event.wait(interval):
            self._dump_usage_data()
        self._dump_usage_data()

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}\n"
            f"\t\tname             : {self.name}\n"
            f"\t\tstate            : {self.state}\n"
            f"\t\tsubprotocol      : {self.subprotocol}\n"
            f"\t\tis_auto_reconnect: {self._is_auto_reconnect}\n"
            f"\t\tcan_reconnect    : {self.can_reconnect}\n"
            f"\t\tnum_attempt      : {self._num_attempt}"
        )
