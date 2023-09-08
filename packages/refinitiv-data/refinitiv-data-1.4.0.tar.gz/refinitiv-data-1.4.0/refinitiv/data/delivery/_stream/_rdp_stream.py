from typing import TYPE_CHECKING, Callable, Any

from ._protocol_type import ProtocolType
from ._stream_listener import RDPStreamListener
from .event import StreamEventID
from .stream import Stream, update_message_with_extended_params
from .stream_log_id import StreamLogID
from ..._tools import cached_property

if TYPE_CHECKING:
    from ._stream_factory import StreamDetails
    from . import StreamConnection
    from ..._types import ExtendedParams
    from ..._core.session import Session


class _RDPStream(Stream, RDPStreamListener["_RDPStream"]):
    _stream_log_id = StreamLogID.OMMStream

    def __init__(
        self,
        stream_id: int,
        session: "Session",
        service: str,
        universe: list,
        view: list,
        parameters: dict,
        details: "StreamDetails",
        extended_params: "ExtendedParams" = None,
        on_ack: Callable = None,
        on_response: Callable = None,
        on_update: Callable = None,
        on_alarm: Callable = None,
    ):
        Stream.__init__(self, stream_id, session, details)
        RDPStreamListener.__init__(
            self,
            logger=session.logger(),
            on_ack=on_ack,
            on_response=on_response,
            on_update=on_update,
            on_alarm=on_alarm,
        )

        self._service = service
        self._universe = universe
        self._view = view
        self._parameters = parameters
        self._extended_params = extended_params

        self._ack_event_id = stream_id + StreamEventID.ACK
        self._update_event_id = stream_id + StreamEventID.UPDATE
        self._response_event_id = stream_id + StreamEventID.RESPONSE
        self._alarm_event_id = stream_id + StreamEventID.ALARM

    @property
    def service(self) -> str:
        return self._service

    @property
    def universe(self) -> list:
        return self._universe

    @property
    def view(self) -> list:
        return self._view

    @property
    def parameters(self) -> dict:
        return self._parameters

    @property
    def extended_params(self) -> "ExtendedParams":
        return self._extended_params

    @property
    def name(self) -> str:
        return str(self._universe)

    @property
    def protocol_type(self) -> ProtocolType:
        return ProtocolType.RDP

    @cached_property
    def close_message(self):
        return {"streamID": f"{self.id:d}", "method": "Close"}

    @cached_property
    def open_message(self) -> dict:
        message = {
            "streamID": f"{self.id:d}",
            "method": "Subscribe",
            "universe": self.universe,
        }

        if self.service is not None:
            message["service"] = self.service

        if self.view is not None:
            message["view"] = self.view

        if self.parameters is not None:
            message["parameters"] = self.parameters

        if self.extended_params:
            message = update_message_with_extended_params(message, self.extended_params)

        return message

    def _do_open(self, *args, **kwargs) -> None:
        self.subscribe()
        self._initialize_cxn()
        self._cxn.on(self._ack_event_id, self._on_stream_ack)
        self._cxn.on(self._update_event_id, self._on_stream_update)
        self._cxn.on(self._response_event_id, self._on_stream_response)
        self._cxn.on(self._alarm_event_id, self._on_stream_alarm)

        super()._do_open(*args, **kwargs)

    def _dispose(self):
        self._debug(f"{self._classname} disposing [d]")
        self.unsubscribe()
        if self._cxn is not None:
            self._cxn.remove_listener(self._ack_event_id, self._on_stream_ack)
            self._cxn.remove_listener(self._update_event_id, self._on_stream_update)
            self._cxn.remove_listener(self._response_event_id, self._on_stream_response)
            self._cxn.remove_listener(self._alarm_event_id, self._on_stream_alarm)

            self._release_cxn()

        self._debug(f"{self._classname} disposed [D]")

    def _do_on_stream_response(self, originator: "StreamConnection", *args) -> Any:
        if self.is_opening:
            self._opened.set()

        return args

    def _do_on_stream_ack(self, originator: "StreamConnection", *args) -> Any:
        message = args[0]
        message_state = message.get("state", {})
        stream_state = message_state.get("stream")

        if stream_state == "Closed":
            self._debug(
                f"{self._classname} received a closing message, message_state={message_state}, state={self.state}"
            )

            if self.is_opening:
                self._opened.set()

        return args

    def _do_on_stream_alarm(self, originator, *args) -> Any:
        """
        {
            "data": [],
            "state": {
                "id": "QPSValuation.ERROR_REQUEST_TIMEOUT",
                "code": 408,
                "status": "ERROR",
                "message": "The request could not be executed
                            within the service allocated time",
                "stream": "Open"
            },
            "type": "Alarm",
            "streamID": "3"
        }
        """
        message = args[0]
        self._error(f"{message}")

        if self.is_opening:
            self._opened.set()

        return args
