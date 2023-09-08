from typing import Union, Optional, Callable, TYPE_CHECKING

from ._type import contrib_type_enum_arg_parser
from ..event import StreamCxnEvent
from ..stream_connection import LOGIN_STREAM_ID
from ..stream_log_id import StreamLogID
from ..._stream import _OMMStream

if TYPE_CHECKING:
    from ._type import ContribType
    from .._stream_factory import StreamDetails
    from ...._core.session import Session


class _OffStreamContrib(_OMMStream):
    _stream_log_id = StreamLogID.OMMStream

    def __init__(
        self,
        post_id: int,
        session: "Session",
        name: str,
        details: "StreamDetails",
        service: str,
        domain: str,
        on_ack: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ) -> None:
        super().__init__(
            stream_id=post_id,
            session=session,
            name=name,
            details=details,
            domain=domain,
            service=service,
            on_error=on_error,
            on_ack=on_ack,
        )
        self._post_id = post_id

    def _get_post_id(self):
        return self._post_id

    def get_contrib_message(self, fields: dict, contrib_type: Union[str, "ContribType", None]) -> dict:
        return {
            "Ack": True,
            "ID": LOGIN_STREAM_ID,
            "Message": {
                "Fields": fields,
                "ID": 0,
                "Type": contrib_type_enum_arg_parser.get_str(contrib_type if contrib_type else "Update"),
                "Domain": self.domain,
            },
            "PostID": self.post_id,
            "Type": "Post",
            "Key": {"Name": self.name, "Service": self.service},
            "Domain": self.domain,
        }

    def _do_open(self, *args, **kwargs):
        self.subscribe()
        self._initialize_cxn()
        self._cxn.on(self._ack_event_id, self._on_stream_ack)
        self._cxn.on(self._error_event_id, self._on_stream_error)
        self._cxn.on(StreamCxnEvent.RECONNECTING, self.halt)

    def _do_close(self, *args, **kwargs):
        self.unsubscribe()
        self._dispose()

    def _dispose(self):
        self._debug(f"{self._classname} disposing [d]")
        if self._cxn is not None:
            self._cxn.remove_listener(self._ack_event_id, self._on_stream_ack)
            self._cxn.remove_listener(self._error_event_id, self._on_stream_error)
            self._cxn.remove_listener(StreamCxnEvent.RECONNECTING, self.halt)
            self._release_cxn()
        self._was_contribute and self._contributed.set()
        self._debug(f"{self._classname} disposed [D]")
