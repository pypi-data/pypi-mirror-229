import asyncio
from functools import partial
from typing import TYPE_CHECKING

from .event import StreamStateEvent
from .stream_state import StreamState
from ..._core.log_reporter import _LogReporter
from ..._tools import CallbackHandler

if TYPE_CHECKING:
    from logging import Logger


class StreamStateManager(_LogReporter):
    def __init__(self, logger: "Logger") -> None:
        _LogReporter.__init__(self, logger=logger)

        if not hasattr(self, "_classname"):
            self._classname: str = self.__class__.__name__

        self._state = StreamState.Unopened
        self._emitter = CallbackHandler()

    @property
    def state(self) -> StreamState:
        return self._state

    def on(self, event, listener):
        return self._emitter.on(event, listener)

    def off(self, event, listener):
        return self._emitter.remove_listener(event, listener)

    @property
    def is_unopened(self) -> bool:
        return self.state is StreamState.Unopened

    @property
    def is_opened(self) -> bool:
        return self.state is StreamState.Opened

    @property
    def is_opening(self) -> bool:
        return self.state is StreamState.Opening

    @property
    def is_open(self) -> bool:
        return self.is_opened or self.is_opening

    @property
    def is_close(self) -> bool:
        return self.is_closed or self.is_closing

    @property
    def is_closing(self) -> bool:
        return self.state is StreamState.Closing

    @property
    def is_closed(self) -> bool:
        return self.state is StreamState.Closed

    def open(self, *args, **kwargs) -> StreamState:
        if self.is_open:
            return self.state

        self._debug(f"{self._classname} is opening [o]")
        self._state = StreamState.Opening
        self._emitter.emit(StreamStateEvent.OPENING, self)
        self._do_open(*args, **kwargs)
        self._state = StreamState.Opened
        self._emitter.emit(StreamStateEvent.OPENED, self)
        self._debug(f"{self._classname} opened [O]")
        return self.state

    async def open_async(self, *args, **kwargs) -> StreamState:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, partial(self.open, *args, **kwargs))
        return result

    def _do_open(self, *args, **kwargs):
        # for override
        pass

    def close(self, *args, **kwargs) -> StreamState:
        if self.is_close or self.is_unopened:
            return self.state

        self._debug(f"{self._classname} is closing [c]")
        self._state = StreamState.Closing
        self._emitter.emit(StreamStateEvent.CLOSING, self)
        self._do_close(*args, **kwargs)
        self._state = StreamState.Closed
        self._emitter.emit(StreamStateEvent.CLOSED, self)
        self._debug(f"{self._classname} closed [C]")
        return self.state

    async def close_async(self, *args, **kwargs) -> StreamState:
        return self.close(*args, **kwargs)

    def _do_close(self, *args, **kwargs):
        # for override
        pass

    def halt(self, *_) -> StreamState:
        if self.is_closing or self.is_closed:
            return self.state

        self._debug(f"{self._classname} halt")
        self._state = StreamState.Closing
        self._emitter.emit(StreamStateEvent.CLOSING, self)
        self._dispose()
        self._state = StreamState.Closed
        self._emitter.emit(StreamStateEvent.CLOSED, self)
        return self.state

    def _dispose(self):
        # for override
        pass
