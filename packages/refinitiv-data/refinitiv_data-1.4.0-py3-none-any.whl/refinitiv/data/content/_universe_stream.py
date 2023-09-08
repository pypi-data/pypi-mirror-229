import itertools
import re

from typing import Any, Optional, Union, TYPE_CHECKING

from .._tools import cached_property, DEBUG
from ..delivery._stream import StreamStateManager, OMMStreamListener, _OMMStream, StreamStateEvent
from ..delivery._stream._stream_factory import create_omm_stream
from ..delivery._stream.stream_cache import StreamCache


if TYPE_CHECKING:
    from ..delivery.omm_stream import ContribType, ContribResponse
    from .._core.session import Session

_id_iterator = itertools.count()

# regular expression pattern for intra-field position sequence
_partial_update_intra_field_positioning_sequence_regular_expression_pattern = re.compile(
    r"[\x1b\x5b|\x9b]([0-9]+)\x60([^\x1b^\x5b|\x9b]+)"
)


def _decode_intra_field_position_sequence(cached_value: str, new_value: str):
    # find all partial update in the value
    tokens = _partial_update_intra_field_positioning_sequence_regular_expression_pattern.findall(
        new_value,
    )

    # check this value contains a partial update or not?
    if len(tokens) == 0:
        # no partial update required, so done
        return new_value

    # do a partial update
    updated_value = cached_value
    for offset, replace in tokens:
        # convert offset from str to int
        offset = int(offset)
        assert offset < len(updated_value)

        # replace the value in the string
        updated_value = updated_value[:offset] + replace + updated_value[offset + len(replace) :]

    # done, return
    return updated_value


class _UniverseStream(StreamCache, StreamStateManager, OMMStreamListener["_UniverseStream"]):
    def __init__(
        self,
        content_type,
        name,
        session=None,
        fields=None,
        service=None,
        api=None,
        extended_params=None,
        on_refresh=None,
        on_status=None,
        on_update=None,
        on_complete=None,
        on_error=None,
        on_ack=None,
        parent_id=None,
    ):
        if name is None:
            raise AttributeError("Instrument name must be defined.")

        self._session = session

        StreamCache.__init__(self, name=name, fields=fields, service=service)
        StreamStateManager.__init__(self, logger=self._session.logger())
        OMMStreamListener.__init__(
            self,
            logger=self._session.logger(),
            on_refresh=on_refresh,
            on_status=on_status,
            on_update=on_update,
            on_complete=on_complete,
            on_error=on_error,
            on_ack=on_ack,
        )

        self._id = next(_id_iterator)
        if parent_id is not None:
            id_ = f"{parent_id}.{self._id}"
        else:
            id_ = f"{self._id}"

        self._classname: str = f"[{self.__class__.__name__}_{id_} name='{name}']"
        self._api = api
        self._extended_params = extended_params
        self._record = {}
        self._content_type = content_type
        self._post_id = None
        self._post_user_info = None

    @cached_property
    def _stream(self) -> _OMMStream:
        return create_omm_stream(
            self._content_type,
            session=self._session,
            name=self._name,
            api=self._api,
            domain="MarketPrice",
            service=self._service,
            fields=self._fields,
            extended_params=self._extended_params,
            on_refresh=self._on_stream_refresh,
            on_status=self._on_stream_status,
            on_update=self._on_stream_update,
            on_complete=self._on_stream_complete,
            on_error=self._on_stream_error,
            on_ack=self._on_stream_ack,
        )

    @property
    def id(self) -> int:
        return self._stream.id

    @property
    def code(self):
        return self._stream.stream_state

    @property
    def message(self):
        return self._stream.message_state

    @property
    def session(self) -> "Session":
        return self._session

    @session.setter
    def session(self, session: "Session"):
        self._session = session
        OMMStreamListener.init_logger(self, self._session.logger())

        self._stream.session = self._session

    @property
    def domain(self) -> str:
        return self._stream.domain

    def contribute(
        self,
        fields: dict,
        contrib_type: Union[str, "ContribType", None] = None,
        post_user_info: Optional[dict] = None,
    ) -> "ContribResponse":
        self._debug(f"{self._classname} contribute on {self.name}")
        return self._stream.contribute(fields, contrib_type, post_user_info)

    async def contribute_async(
        self,
        fields: dict,
        contrib_type: Union[str, "ContribType", None] = None,
        post_user_info: Optional[dict] = None,
    ) -> "ContribResponse":
        self._debug(f"{self._classname} contribute on {self.name}")
        return await self._stream.contribute_async(fields, contrib_type, post_user_info)

    def _do_close(self, *args, **kwargs):
        self._debug(f"{self._classname} Stop subscription {self.id} to {self.name}")
        self._stream.close(*args, **kwargs)
        self._stream.off(StreamStateEvent.CLOSED, self.close)
        self.unsubscribe()

    def _do_open(self, *args, with_updates=True):
        self._debug(f"{self._classname} Open async {self.id} to {self.name}")
        self.subscribe()
        self._stream.on(StreamStateEvent.CLOSED, self.close)
        self._stream.open(*args, with_updates=with_updates)

    def _decode_partial_update_field(self, key, value):
        """
        This legacy is used to process the partial update
        RETURNS the processed partial update data
        """

        fields = self._record.get("Fields")
        if key not in fields:
            fields[key] = value
            self._warning(f"key {key} not in self._record['Fields']")
            return value

        # process infra-field positioning sequence
        cached_value = fields[key]

        # done
        return _decode_intra_field_position_sequence(cached_value, value)

    def _filter_fields(self, fields):
        return fields

    def _write_to_record(self, message: dict):
        for message_key, message_value in message.items():
            if message_key == "Fields":
                fields = message_value
                if self._fields:
                    fields = self._filter_fields(fields)

                # fields data
                # loop over all update items
                for key, value in fields.items():
                    # only string value need to check for a partial update
                    if isinstance(value, str):
                        # value is a string, so check for partial update string
                        # process partial update and update the callback
                        # with processed partial update
                        fields[key] = self._decode_partial_update_field(key, value)

                # update the field data
                self._record.setdefault(message_key, {})
                self._record[message_key].update(fields)
            else:
                # not a "Fields" data
                self._record[message_key] = message_value

    def _do_on_stream_refresh(self, stream: "_OMMStream", message: dict, *args) -> dict:
        if self._fields:
            fields = message.get("Fields")
            fields = self._filter_fields(fields)
            message["Fields"] = fields
        self._record = message

        if DEBUG:
            fields = self._record.get("Fields", [])
            num_fields = len(fields)
            self._debug(f"|>|>|>|>|>|>{self._classname} has fields in record {num_fields} after refresh")

        return message.get("Fields")

    def _do_on_stream_status(self, stream: "_OMMStream", message: dict, *_) -> Any:
        self._status = message
        return message

    def _do_on_stream_update(self, stream: "_OMMStream", message: dict, *args) -> Any:
        if DEBUG:
            fields = self._record.get("Fields", [])
            num_fields = len(fields)
            self._debug(f"|>|>|>|>|>|> {self._classname} has fields in record {num_fields} after update")

        self._write_to_record(message)
        return message.get("Fields")

    def send_open_message(self):
        self._stream.send_open_message()

    def remove_fields_from_record(self, fields):
        for field in fields:
            if self._record.get("Fields"):
                self._record["Fields"].pop(field, None)
