from typing import Dict

from .._content_type import ContentType
from .._tools import cached_property
from ..content._universe_stream import _UniverseStream
from ..content._universe_streams import _UniverseStreams
from ..content.custom_instruments._custom_instruments_data_provider import get_user_id, symbol_with_user_id
from ..content.pricing._stream_facade import Stream as _Stream, PricingStream
from ..delivery._stream import StreamStateEvent


class MixedStreams(_UniverseStreams):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, content_type=ContentType.NONE)
        self._uuid = None

    def _get_symbol(self, universe):
        if not symbol_with_user_id.match(universe):
            if not self._uuid:
                self._uuid = get_user_id(self._session)
            symbol = f"{universe}.{self._uuid}"
        else:
            symbol = universe
        return symbol

    def _get_pricing_stream(self, name):
        return _UniverseStream(
            content_type=ContentType.STREAMING_PRICING,
            session=self._session,
            name=name,
            fields=self.fields,
            service=self._service,
            on_refresh=self._on_stream_refresh,
            on_status=self._on_stream_status,
            on_update=self._on_stream_update,
            on_complete=self._on_stream_complete,
            on_error=self._on_stream_error,
            extended_params=self._extended_params,
            parent_id=self._id,
        )

    def _get_custom_instruments_stream(self, name):
        return _UniverseStream(
            content_type=ContentType.STREAMING_CUSTOM_INSTRUMENTS,
            session=self._session,
            name=self._get_symbol(name),
            fields=self.fields,
            service=self._service,
            on_refresh=self._on_stream_refresh,
            on_status=self._on_stream_status,
            on_update=self._on_stream_update,
            on_complete=self._on_stream_complete,
            on_error=self._on_stream_error,
            extended_params=self._extended_params,
            parent_id=self._id,
        )

    def _create_stream_by_name(self, name):
        if name.startswith("S)"):
            stream = self._get_custom_instruments_stream(name)
        else:
            stream = self._get_pricing_stream(name)
        return stream

    @cached_property
    def _stream_by_name(self) -> Dict[str, _UniverseStream]:
        return {name: self._create_stream_by_name(name) for name in self.universe}

    def _do_open(self, *args, with_updates=True) -> None:
        for stream in self._stream_by_name.values():
            stream.on(StreamStateEvent.CLOSED, self._on_stream_close)
        super()._do_open(*args, with_updates=with_updates)

    def _do_close(self, *args, **kwargs) -> None:
        super()._do_close(*args, **kwargs)
        for stream in self._stream_by_name.values():
            stream.off(StreamStateEvent.CLOSED, self._on_stream_close)

    def add_instruments(self, *instruments):
        super().add_instruments(*[self._get_symbol(name) if name.startswith("S)") else name for name in instruments])

    def remove_instruments(self, *instruments):
        super().remove_instruments(*[self._get_symbol(name) if name.startswith("S)") else name for name in instruments])


class Stream(_Stream):
    @cached_property
    def _stream(self) -> MixedStreams:
        return MixedStreams(
            item_facade_class=PricingStream,
            universe=self._universe,
            session=self._session,
            fields=self._fields,
            service=self._service,
            extended_params=self._extended_params,
        )
