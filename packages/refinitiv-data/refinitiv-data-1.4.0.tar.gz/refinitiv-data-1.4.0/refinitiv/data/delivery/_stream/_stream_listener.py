import traceback
from functools import partial
from typing import Callable, Tuple, TYPE_CHECKING, Any, Dict
from typing import TypeVar, Generic

from .event import StreamEvent
from ..._core.log_reporter import _LogReporter, LogReporter
from ..._tools import DEBUG, CallbackHandler

if TYPE_CHECKING:
    from logging import Logger

T = TypeVar("T")


def __on_listener_error(
    error: Callable,
    debug: Callable,
    self,
    event: "StreamEvent",
    listener: Callable,
    exc: Exception,
) -> None:
    error(f"{self._classname} on_{event} {listener} raised exception: {exc!r}")
    debug(f"{traceback.format_exc()}")

    if DEBUG:
        raise exc


def on_listener_error(self, event: "StreamEvent", listener: Callable, exc: Exception) -> None:
    __on_listener_error(self.error, self.debug, self, event, listener, exc)


def _on_listener_error(self, event: "StreamEvent", listener: Callable, exc: Exception) -> None:
    __on_listener_error(self._error, self._debug, self, event, listener, exc)


def make_on_listener_error(self):
    if isinstance(self, _LogReporter):
        func = partial(_on_listener_error, self)
    elif isinstance(self, LogReporter):
        func = partial(on_listener_error, self)
    else:
        raise ValueError(f"Don't know type of self={self}")
    return func


class StreamListener(_LogReporter):
    def __init__(
        self,
        logger: "Logger",
        on_update: Callable = None,
        on_ack: Callable = None,
        add_originator: bool = True,
    ) -> None:
        _LogReporter.__init__(self, logger)

        self._on_update = on_update
        self._on_ack = on_ack

        self._add_originator = add_originator
        self._emitter = CallbackHandler()

        if not hasattr(self, "_classname"):
            self._classname: str = self.__class__.__name__

        self._handler_by_event: Dict[str, Callable] = {}
        self._handler_by_event[StreamEvent.UPDATE] = self._do_on_stream_update
        self._handler_by_event[StreamEvent.ACK] = self._do_on_stream_ack

        self._is_subscribed = False

    def subscribe(self):
        if self._is_subscribed:
            return
        self._is_subscribed = True

        self._do_subscribe()
        self._on_event(StreamEvent.UPDATE, self._on_update)
        self._on_event(StreamEvent.ACK, self._on_ack)

    def _do_subscribe(self):
        raise NotImplementedError()

    def unsubscribe(self):
        if not self._is_subscribed:
            return
        self._is_subscribed = False

        self._do_unsubscribe()
        self.off_update(self._on_update)
        self.off_ack(self._on_ack)

    def _do_unsubscribe(self):
        raise NotImplementedError()

    def on_update(self, func: Callable) -> T:
        return self._on_event(StreamEvent.UPDATE, func, halt_if_none=True)

    def off_update(self, func: Callable) -> T:
        return self._off_event(StreamEvent.UPDATE, func)

    def on_ack(self, func: Callable) -> T:
        return self._on_event(StreamEvent.ACK, func, halt_if_none=True)

    def off_ack(self, func: Callable) -> T:
        return self._off_event(StreamEvent.ACK, func)

    def _on_event(self, event: str, func: Callable, halt_if_none: bool = False) -> T:
        if not func and halt_if_none:
            raise ValueError(f"Cannot subscribe to event {event} because no listener")

        if not func and not halt_if_none:
            return

        self._emitter.on(event, func)
        return self

    def _off_event(self, event: str, func: Callable):
        if not func:
            return

        self._emitter.remove_listener(event, func)

    def _validate_args(self, args) -> Tuple:
        if args is None:
            raise ValueError(f"{self._classname}: args cannot be None")

        if not isinstance(args, tuple):
            args = (args,)

        return args

    def dispatch_update(self, originator, *args):
        self._debug(f"{self._classname} dispatch_update {args}")
        self._on_stream_update(originator, *args)

    def _on_stream_update(self, originator, *args) -> None:
        self._propagate_event(StreamEvent.UPDATE, originator, *args)

    def _do_on_stream_update(self, originator, *args) -> Any:
        # for override
        return args

    def dispatch_ack(self, originator, *args):
        self._debug(f"{self._classname} dispatch_ack {args}")
        self._on_stream_ack(originator, *args)

    def _on_stream_ack(self, originator, *args) -> None:
        self._propagate_event(StreamEvent.ACK, originator, *args)

    def _do_on_stream_ack(self, originator, *args) -> Any:
        # for override
        return args

    def _propagate_event(self, event: str, originator, *args):
        self._debug(f"{self._classname} on_{event} {args}")
        handler = self._handler_by_event[event]
        args = handler(originator, *args)
        args = self._validate_args(args)
        if self._add_originator:
            args = (self,) + args
        self._emitter.emit(event, *args)


class OMMStreamListener(StreamListener, Generic[T]):
    def __init__(
        self,
        logger: "Logger",
        on_refresh: Callable = None,
        on_status: Callable = None,
        on_update: Callable = None,
        on_complete: Callable = None,
        on_error: Callable = None,
        on_ack: Callable = None,
        add_originator: bool = True,
    ) -> None:
        StreamListener.__init__(
            self,
            logger=logger,
            on_update=on_update,
            on_ack=on_ack,
            add_originator=add_originator,
        )
        self._on_refresh = on_refresh
        self._on_status = on_status
        self._on_complete = on_complete
        self._on_error = on_error

        self._handler_by_event[StreamEvent.REFRESH] = self._do_on_stream_refresh
        self._handler_by_event[StreamEvent.STATUS] = self._do_on_stream_status
        self._handler_by_event[StreamEvent.COMPLETE] = self._do_on_stream_complete
        self._handler_by_event[StreamEvent.ERROR] = self._do_on_stream_error

    def _do_subscribe(self):
        self._on_event(StreamEvent.REFRESH, self._on_refresh)
        self._on_event(StreamEvent.STATUS, self._on_status)
        self._on_event(StreamEvent.COMPLETE, self._on_complete)
        self._on_event(StreamEvent.ERROR, self._on_error)

    def _do_unsubscribe(self):
        self.off_refresh(self._on_refresh)
        self.off_status(self._on_status)
        self.off_complete(self._on_complete)
        self.off_error(self._on_error)

    def on_refresh(self, func: Callable) -> T:
        return self._on_event(StreamEvent.REFRESH, func, halt_if_none=True)

    def off_refresh(self, func: Callable) -> T:
        return self._off_event(StreamEvent.REFRESH, func)

    def on_status(self, func: Callable) -> T:
        return self._on_event(StreamEvent.STATUS, func, halt_if_none=True)

    def off_status(self, func: Callable) -> T:
        return self._off_event(StreamEvent.STATUS, func)

    def on_complete(self, func: Callable) -> T:
        return self._on_event(StreamEvent.COMPLETE, func, halt_if_none=True)

    def off_complete(self, func: Callable) -> T:
        return self._off_event(StreamEvent.COMPLETE, func)

    def on_error(self, func: Callable) -> T:
        return self._on_event(StreamEvent.ERROR, func, halt_if_none=True)

    def off_error(self, func: Callable) -> T:
        return self._off_event(StreamEvent.ERROR, func)

    def dispatch_refresh(self, originator, *args):
        self._debug(f"{self._classname} dispatch_refresh {args}")
        self._on_stream_refresh(originator, *args)

    def _on_stream_refresh(self, originator, *args) -> None:
        self._propagate_event(StreamEvent.REFRESH, originator, *args)

    def _do_on_stream_refresh(self, originator, *args) -> Any:
        # for override
        return args

    def dispatch_status(self, originator, *args):
        self._debug(f"{self._classname} dispatch_status {args}")
        self._on_stream_status(originator, *args)

    def _on_stream_status(self, originator, *args) -> None:
        self._propagate_event(StreamEvent.STATUS, originator, *args)

    def _do_on_stream_status(self, originator, message: dict, *args) -> Any:
        # for override
        pass

    def dispatch_complete(self, originator, *args):
        self._debug(f"{self._classname} dispatch_complete {args}")
        self._on_stream_complete(originator, *args)

    def _on_stream_complete(self, originator, *args) -> None:
        self._propagate_event(StreamEvent.COMPLETE, originator, *args)

    def _do_on_stream_complete(self, originator, *args) -> Any:
        # for override
        return args

    def dispatch_error(self, originator, *args):
        self._debug(f"{self._classname} dispatch_error {args}")
        self._on_stream_error(originator, *args)

    def _on_stream_error(self, originator, *args) -> None:
        self._propagate_event(StreamEvent.ERROR, originator, *args)

    def _do_on_stream_error(self, originator, *args) -> Any:
        # for override
        return args


class RDPStreamListener(StreamListener, Generic[T]):
    def __init__(
        self,
        logger: "Logger",
        on_ack: Callable = None,
        on_response: Callable = None,
        on_update: Callable = None,
        on_alarm: Callable = None,
    ) -> None:
        StreamListener.__init__(self, logger, on_update, on_ack)

        self._on_response = on_response
        self._on_alarm = on_alarm

        self._handler_by_event[StreamEvent.ACK] = self._do_on_stream_ack
        self._handler_by_event[StreamEvent.RESPONSE] = self._do_on_stream_response
        self._handler_by_event[StreamEvent.ALARM] = self._do_on_stream_alarm

    def _do_subscribe(self):
        self._on_event(StreamEvent.ACK, self._on_ack)
        self._on_event(StreamEvent.RESPONSE, self._on_response)
        self._on_event(StreamEvent.ALARM, self._on_alarm)

    def _do_unsubscribe(self):
        self.off_ack(self._on_ack)
        self.off_response(self._on_response)
        self.off_alarm(self._on_alarm)

    def on_response(self, func: Callable) -> T:
        return self._on_event(StreamEvent.RESPONSE, func, halt_if_none=True)

    def off_response(self, func: Callable) -> T:
        return self._off_event(StreamEvent.RESPONSE, func)

    def on_alarm(self, func: Callable) -> T:
        return self._on_event(StreamEvent.ALARM, func, halt_if_none=True)

    def off_alarm(self, func: Callable) -> T:
        return self._off_event(StreamEvent.ALARM, func)

    def dispatch_response(self, originator, *args):
        self._debug(f"{self._classname} dispatch_response {args}")
        self._on_stream_response(originator, *args)

    def _on_stream_response(self, originator, *args) -> None:
        self._propagate_event(StreamEvent.RESPONSE, originator, *args)

    def _do_on_stream_response(self, originator, *args) -> Any:
        # for override
        return args

    def dispatch_alarm(self, originator, *args):
        self._debug(f"{self._classname} dispatch_alarm {args}")
        self._on_stream_alarm(originator, *args)

    def _on_stream_alarm(self, originator, *args) -> None:
        self._propagate_event(StreamEvent.ALARM, originator, *args)

    def _do_on_stream_alarm(self, originator, *args) -> Any:
        # for override
        return args
