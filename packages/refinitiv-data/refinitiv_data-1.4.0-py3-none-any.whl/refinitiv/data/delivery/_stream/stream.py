from threading import Event
from typing import Optional, Any
from typing import TYPE_CHECKING

from ._protocol_type import ProtocolType
from ._stream_cxn_cache import stream_cxn_cache
from .event import StreamCxnEvent
from .stream_log_id import StreamLogID
from .stream_state import StreamState
from .stream_state_manager import StreamStateManager
from ..._core.session.tools import is_closed
from ..._errors import ScopeError
from ..._tools import lazy_dump, cached_property

if TYPE_CHECKING:
    from ..._content_type import ContentType
    from .._stream import StreamConnection
    from ..._core.session import Session
    from ._stream_factory import StreamDetails


class Stream(StreamStateManager):
    _cxn: Optional["StreamConnection"] = None
    _stream_log_id: Optional[StreamLogID] = None

    def __init__(
        self,
        stream_id: int,
        session: "Session",
        details: "StreamDetails",
    ) -> None:
        StreamStateManager.__init__(self, logger=session.logger())
        self.details = details
        self._id: int = stream_id
        self._session: "Session" = session
        self._classname = self._stream_log_id + self.id

    @cached_property
    def _opened(self) -> Event:
        return Event()

    @property
    def classname(self):
        return self._classname

    @property
    def id(self) -> int:
        return self._id

    @property
    def session(self) -> "Session":
        return self._session

    @session.setter
    def session(self, session: "Session"):
        if self._session != session and not self.is_open:
            self._session = session
            StreamStateManager.__init__(self, logger=self._session.logger())

    @property
    def name(self) -> str:
        return ""

    @property
    def content_type(self) -> "ContentType":
        return self.details.content_type

    @property
    def protocol_type(self) -> ProtocolType:
        return ProtocolType.NONE

    @property
    def close_message(self) -> dict:
        return {}

    @property
    def open_message(self) -> dict:
        return {}

    def open(self, *args, with_updates: bool = True) -> StreamState:
        if is_closed(self._session):
            raise AssertionError("Session must be open")

        return super().open(with_updates=with_updates)

    def send(self, message: dict) -> bool:
        if self._cxn:
            self._debug(f"{self.classname} send %s", lazy_dump(message))
            return self._cxn.send_message(message)
        else:
            self._debug(
                f"{self.classname} cannot send %s, cxn is {self._cxn}, state is {self.state}",
                lazy_dump(message),
            )
            return False

    def _initialize_cxn(self):
        try:
            self._cxn = stream_cxn_cache.get_cxn(self.session, self.details)
        except ScopeError as e:
            self.halt()
            raise e
        self._cxn.on(StreamCxnEvent.DISCONNECTING, self.close)
        self._cxn.on(StreamCxnEvent.RECONNECTED, self._on_reconnected)
        self._cxn.on(StreamCxnEvent.DISPOSED, self.halt)

    def _release_cxn(self):
        self._cxn.remove_listener(StreamCxnEvent.DISCONNECTING, self.close)
        self._cxn.remove_listener(StreamCxnEvent.RECONNECTED, self._on_reconnected)
        self._cxn.remove_listener(StreamCxnEvent.DISPOSED, self.halt)
        self._debug(f"{self.classname} release cxn={self._cxn}")
        if stream_cxn_cache.has_cxn(self.session, self.details):
            stream_cxn_cache.release(self.session, self.details)
        self._cxn = None

    def _do_open(self, *args, **kwargs) -> None:
        self._opened.clear()
        self.send(self.open_message)
        if not self._cxn.is_disposed:
            self._opened.wait()

    def _do_close(self, *args, **kwargs):
        self.send(self.close_message)
        self._dispose()

    def _on_reconnected(self, *args, **kwargs):
        if self.is_open:
            self.send(self.open_message)

    def _do_on_stream_error(self, originator, *args) -> Any:
        if self.is_opening:
            self._opened.set()

        return args


def update_message_with_extended_params(message: dict, extended_params: dict) -> dict:
    return update_key_in_dict(message, extended_params)


def update_key_in_dict(message: dict, extended_params: dict) -> dict:
    for param, extended_val in extended_params.items():
        if param in message:
            prev_value = message[param]
            if isinstance(prev_value, dict) and isinstance(extended_val, dict):
                update_key_in_dict(prev_value, extended_val)
            else:
                message[param] = extended_val
        else:
            message[param] = extended_val

    return message
