from concurrent.futures import Future, wait
from typing import Any, Callable, Dict, List, TYPE_CHECKING, Tuple

from ._chain_records import ChainRecords
from ._display_template import disp_tmpl_to_num_summary_links
from ....delivery._stream import OMMStreamListener, StreamEvent, StreamStateManager

if TYPE_CHECKING:
    from ...._types import ExtendedParams, OptBool, OptInt, OptStr
    from ....delivery._stream import _OMMStream
    from ...._core.session import Session


class StreamingChainEvent:
    ADD = "streaming_chain_add_event"
    REMOVE = "streaming_chain_remove_event"


class StreamingChain(StreamStateManager, OMMStreamListener["StreamingChain"]):
    def __init__(
        self,
        name: str,
        session: "Session",
        service: "OptStr" = None,
        skip_summary_links: "OptBool" = True,
        skip_empty: "OptBool" = True,
        override_summary_links: "OptInt" = None,
        api: "OptStr" = None,
        extended_params: "ExtendedParams" = None,
    ):
        self._session = session

        StreamStateManager.__init__(self, logger=self._session.logger())
        OMMStreamListener.__init__(self, logger=self._session.logger(), add_originator=False)

        self.name: str = name
        self._service = service
        self._skip_summary_links = skip_summary_links
        self._skip_empty = skip_empty
        self._override_summary_links = override_summary_links
        self._api = api

        self._chain_records: ChainRecords = ChainRecords(
            self._session, service=service, api=api, extended_params=extended_params
        )
        self._constituents = None
        self._complete_future: Future = Future()
        self._chain_record_name_to_offset: Dict[str, int] = {self.name: 0}
        self._update_messages: List[Tuple[str, dict]] = []

    @property
    def is_chain(self) -> bool:
        wait([self._complete_future])
        is_chain = self._chain_records.has(self.name)
        return is_chain

    @property
    def num_summary_links(self) -> int:
        if self._override_summary_links:
            return self._override_summary_links
        else:
            disp_tmpl = self._chain_records.display_template
            return disp_tmpl_to_num_summary_links.get(disp_tmpl, None)

    @property
    def summary_links(self) -> List[str]:
        if not self.is_chain:
            return []

        summary_links = self._constituents[: self.num_summary_links]
        return [summary_link for summary_link in summary_links if not self._skip_empty or summary_link is not None]

    @property
    def display_name(self) -> str:
        if not self.is_chain:
            return ""

        return self._chain_records.get_display_name(self.name)

    @property
    def session(self) -> "Session":
        return self._session

    @session.setter
    def session(self, session: "Session"):
        if self._session != session and not self.is_open:
            self._session = session
            OMMStreamListener.init_logger(self, self._session.logger())
            self._chain_records.session = self._session

    def get_constituents(self) -> List[str]:
        if not self.is_chain:
            return []

        num_summary_links = self.num_summary_links
        if self._skip_summary_links:
            constituents = self._constituents[num_summary_links:]
        else:
            constituents = self._constituents[:]

        return [constituent for constituent in constituents if not self._skip_empty or constituent is not None]

    def _do_open(self, *args, with_updates=True):
        self.subscribe()

        self._chain_records.subscribe()
        self._chain_records.on_refresh(self._on_stream_refresh)
        self._chain_records.on_status(self._on_stream_status)
        self._chain_records.on_update(self._on_stream_update)
        self._chain_records.on_error(self._on_stream_error)

        self._chain_records.open(with_updates=with_updates)
        self._constituents = []
        offset = 0
        name = self.name
        while name:
            if not self._chain_records.has_stream(name):
                self._chain_records.add(name)
                self._chain_records.open_stream(name, with_updates)

            self._chain_records.wait_refresh(name)

            if self._chain_records.is_stream_close(name):
                self._complete_future.set_result(True)
                break

            chain_record = self._chain_records.get_record(name)
            name = chain_record
            if chain_record:
                name = chain_record.next_chain_record_name

                for i, constituent in enumerate(chain_record.constituents):
                    self._append_constituent(offset + i, constituent)

                offset += chain_record.num_constituents or 0

                if name:
                    self._chain_record_name_to_offset[name] = offset

        if not self._complete_future.done():
            self._complete_future.set_result(True)

        self.dispatch_complete(self, self.get_constituents())
        self._process_remaining_update_messages()

    def _do_close(self, *args, **kwargs):
        self._chain_records.close()
        self._chain_records.off_refresh(self._on_stream_refresh)
        self._chain_records.off_status(self._on_stream_status)
        self._chain_records.off_update(self._on_stream_update)
        self._chain_records.off_error(self._on_stream_error)
        self._chain_records.unsubscribe()
        self.unsubscribe()

    def _append_constituent(self, index: int, constituent: str):
        self._constituents.append(constituent)
        self.dispatch_add(constituent, index)

    def _remove_constituent(self, index: int, constituent: str):
        self._constituents.pop(index)
        self.dispatch_remove(constituent, index)

    def _update_constituent(self, index: int, old_constituent: str, new_constituent: str):
        self._constituents[index] = new_constituent
        self.dispatch_update(self, new_constituent, old_constituent, index)

    def _do_on_stream_status(self, originator: ChainRecords, message: dict, *_) -> Any:
        state = message.get("State", {})
        stream_state = state.get("Stream")
        if stream_state == "Closed":
            self._chain_records.close()

        return message

    def _on_stream_update(self, originator: ChainRecords, stream: "_OMMStream", message: dict, *args) -> Any:
        if not self._complete_future.done():
            self._update_messages.append((stream.name, message))
            self._warning("StreamingChain :: waiting to update because chain decode does not completed.")
            return

        self._process_remaining_update_messages()
        self._update_chain_record(stream.name, message)

    def _process_remaining_update_messages(self):
        self._debug(f"{self._classname} starts process remaining update messages")
        while True:
            try:
                (name, message) = self._update_messages.pop(0)
            except IndexError:
                break

            self._update_chain_record(name, message)

    def _update_chain_record(self, name: str, message: dict):
        self._debug(f"{self._classname} updates chain record, name={name}")
        fields = message.get("Fields", [])
        chain_record = self._chain_records.get_record(name)

        if not chain_record:
            self._warning(f"StreamingChain :: Skipping to update an invalid chain record = {name}.")
            return

        index_to_old_and_new_constituent = chain_record.update(fields)

        offset = self._chain_record_name_to_offset[name]
        for i, (old_c, new_c) in index_to_old_and_new_constituent.items():
            i = offset + i

            if old_c and new_c:
                self._update_constituent(i, old_c, new_c)

            elif not old_c and new_c:
                self._append_constituent(i, new_c)

            elif old_c and not new_c:
                self._remove_constituent(i, old_c)

    def dispatch_update(self, originator: "StreamingChain", *args):
        self._debug(f"{self._classname} dispatch_update {args}")
        self._emitter.emit(StreamEvent.UPDATE, *args)

    def dispatch_add(self, constituent, index):
        self._debug(f"{self._classname} dispatch_add {index, constituent}")
        self._emitter.emit(StreamingChainEvent.ADD, index, constituent)

    def dispatch_remove(self, constituent, index):
        self._debug(f"{self._classname} dispatch_remove {index, constituent}")
        self._emitter.emit(StreamingChainEvent.REMOVE, index, constituent)

    def on_add(self, func: Callable):
        self._on_event(StreamingChainEvent.ADD, func, halt_if_none=True)

    def on_remove(self, func):
        self._on_event(StreamingChainEvent.REMOVE, func, halt_if_none=True)
