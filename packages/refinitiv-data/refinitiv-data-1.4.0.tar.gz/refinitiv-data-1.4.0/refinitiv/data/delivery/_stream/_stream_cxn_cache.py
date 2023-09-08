import threading
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Dict, List

from .event import StreamCxnEvent
from ..._core.session.event_code import EventCode

if TYPE_CHECKING:
    from ..._content_type import ContentType
    from ._stream_factory import StreamDetails
    from .._stream import StreamConnection
    from ..._core.session import Session

StreamConnections = List["StreamConnection"]


def on_event_connecting(cxn: "StreamConnection", message: dict = None):
    on_event_listener(cxn, EventCode.StreamConnecting, message)


def on_event_connected(cxn: "StreamConnection", message: dict = None):
    on_event_listener(cxn, EventCode.StreamConnected, message)


def on_event_disconnected(cxn: "StreamConnection", message: dict = None):
    on_event_listener(cxn, EventCode.StreamDisconnected, message)


def on_event_reconnecting(cxn: "StreamConnection", message: dict = None):
    on_event_listener(cxn, EventCode.StreamReconnecting, message)


def on_event_authentication_success(cxn: "StreamConnection", message: dict = None):
    on_event_listener(cxn, EventCode.StreamAuthenticationSuccess, message)


def on_event_authentication_failed(cxn: "StreamConnection", message: dict = None):
    on_event_listener(cxn, EventCode.StreamAuthenticationFailed, message)


def on_event_listener(cxn: "StreamConnection", event: EventCode, message: dict):
    if message is None:
        message = {}
    message["url"] = cxn._config.url
    message["api_cfg"] = cxn._config.api_cfg_key
    cxn.session._call_on_event(event, message)


def add_listeners(cxn: "StreamConnection") -> None:
    cxn.on(StreamCxnEvent.CONNECTING, on_event_connecting)
    cxn.on(StreamCxnEvent.CONNECTED, on_event_connected)
    cxn.on(StreamCxnEvent.DISCONNECTED, on_event_disconnected)
    cxn.on(StreamCxnEvent.RECONNECTING, on_event_reconnecting)
    cxn.on(StreamCxnEvent.LOGIN_SUCCESS, on_event_authentication_success)
    cxn.on(StreamCxnEvent.LOGIN_FAIL, on_event_authentication_failed)


def remove_listeners(cxn: "StreamConnection") -> None:
    cxn.remove_listener(StreamCxnEvent.CONNECTING, on_event_connecting)
    cxn.remove_listener(StreamCxnEvent.CONNECTED, on_event_connected)
    cxn.remove_listener(StreamCxnEvent.DISCONNECTED, on_event_disconnected)
    cxn.remove_listener(StreamCxnEvent.RECONNECTING, on_event_reconnecting)
    cxn.remove_listener(StreamCxnEvent.LOGIN_SUCCESS, on_event_authentication_success)
    cxn.remove_listener(StreamCxnEvent.LOGIN_FAIL, on_event_authentication_failed)


class CacheItem:
    def __init__(self, cxn: "StreamConnection", details: "StreamDetails", owner: dict) -> None:
        self.api_config_key = details.api_config_key
        self.owner = owner
        self.cxn: "StreamConnection" = cxn
        self.number_in_use = 0

        add_listeners(self.cxn)

    @property
    def is_using(self):
        return self.number_in_use > 0

    def inc_use(self):
        self.number_in_use += 1

    def dec_use(self):
        if self.number_in_use == 0:
            raise ValueError(f"CacheItem: number_in_use cannot be less 0, cxn={self.cxn.state}")

        self.number_in_use -= 1

        if self.number_in_use == 0 and (self.cxn.is_disconnecting or self.cxn.is_disposed):
            self.dispose()

    def dispose(self):
        self.number_in_use = -1
        self.owner.pop(self.api_config_key, None)
        self.api_config_key = None
        self.owner = None

        remove_listeners(self.cxn)
        cxn = self.cxn
        cxn.dispose()
        try:
            cxn.join(5)
        except RuntimeError:
            # silently
            pass
        self.cxn = None

    def __str__(self) -> str:
        if self.cxn:
            name = self.cxn.name
        else:
            name = "disposed"
        return f"CacheItem(cxn={name}, number_in_use={self.number_in_use})"


class StreamCxnCache(object):
    def __init__(self) -> None:
        self._cache: Dict["Session", Dict[str, CacheItem]] = {}
        self._lock = threading.Lock()
        self.cxn_created = threading.Event()

    def has_cxn(self, session: "Session", details: "StreamDetails") -> bool:
        item = self._cache.get(session, {}).get(details.api_config_key)
        return bool(item)

    def get_cxn(self, session: "Session", details: "StreamDetails") -> "StreamConnection":
        with self._lock:
            content_type = details.content_type
            protocol_type = details.protocol_type

            if not self.has_cxn(session, details):
                from ._stream_factory import create_stream_cxn

                self.cxn_created.clear()

                cxn = create_stream_cxn(details, session)
                cxn.start()
                self._add_cxn(cxn, session, details)

                self.cxn_created.set()

                session.debug(
                    f" + StreamCxnCache created new connection: "
                    f"id={cxn.id}, daemon={cxn.daemon}, content_type={content_type}, "
                    f"protocol_type={protocol_type}"
                )

            item = self._get_cache_item(session, details)
            cxn = item.cxn

            session.debug(
                f"StreamCxnCache wait for connection: "
                f"id={cxn.id}, content_type={content_type}, "
                f"protocol_type={protocol_type}"
            )

            cxn.wait_connection_result()

            if cxn.is_disconnected or cxn.is_disposed:  # Connection failure for some reason
                session.debug("StreamCxnCache: Connection will be deleted, because failure")
                self.del_cxn(cxn, session, details)
                raise ConnectionError(f"Cannot prepare connection {cxn}")

            else:
                item.inc_use()
                session.debug(f" <=== StreamCxnCache connection id={cxn.id} is ready")

            return cxn

    def release(self, session: "Session", details: "StreamDetails") -> None:
        content_type = details.content_type
        if not self.has_cxn(session, details):
            raise ValueError(
                f"Cannot release stream connection, "
                f"because it’s not in the cache "
                f"(content_type={content_type}, session={session})"
            )

        item_by_api_type = self._cache[session]
        item = item_by_api_type[details.api_config_key]
        item.dec_use()
        session.debug(
            f" ===> StreamCxnCache release (item={item},\n"
            f"\t\tcontent_type={content_type},\n"
            f"\t\tsession={session})"
        )

    def del_cxn(self, cxn: "StreamConnection", session: "Session", details: "StreamDetails") -> None:
        content_type = details.content_type

        if not cxn:
            raise ValueError(
                f"Cannot delete stream connection, "
                f"because it is empty (content_type={content_type}, "
                f"cxn={cxn}, session={session})"
            )

        if not self.has_cxn(session, details):
            raise ValueError(
                f"Cannot delete stream connection, "
                f"because already deleted (content_type={content_type}, "
                f"cxn={cxn}, session={session})"
            )

        item_by_api_type = self._cache[session]
        item = item_by_api_type[details.api_config_key]
        if item.is_using:
            raise AssertionError(
                f"Cannot delete stream connection, "
                f"because it is using (content_type={content_type}, "
                f"cxn={cxn}, session={session})"
            )

        cached_cxn = item.cxn

        if cxn is not cached_cxn:
            raise ValueError(
                f"Cannot delete stream connection, "
                f"because cxn is not the same \n"
                f"(cxn={cxn} != cached_cxn={cached_cxn},"
                f"content_type={content_type}, session={session})"
            )

        item.dispose()

    def has_cxns(self, session: "Session") -> bool:
        item_by_content_type = self._cache.get(session, {})
        has_cxns = bool(item_by_content_type.values())
        return has_cxns

    def get_cxns(self, session: "Session") -> StreamConnections:
        item_by_content_type = self._cache.get(session, {})
        return [item.cxn for item in item_by_content_type.values()]

    def get_all_cxns(self) -> StreamConnections:
        cxns = []
        for session, item_by_content_type in self._cache.items():
            for cache_item in item_by_content_type.values():
                cxns.append(cache_item.cxn)
        return cxns

    def close_cxns(self, session: "Session") -> None:
        def _close_cxn(item):
            if item.is_using:
                item.cxn.start_disconnecting()

            else:
                item.cxn.start_disconnecting()
                item.cxn.end_disconnecting()
                item.dispose()

        with ThreadPoolExecutor(thread_name_prefix="CloseCxns-Thread") as pool:
            pool.map(_close_cxn, self._get_cache_items(session))

        self._cache.pop(session, None)

    def _add_cxn(self, cxn: "StreamConnection", session: "Session", details: "StreamDetails") -> CacheItem:
        content_type = details.content_type

        if not cxn:
            raise ValueError(
                f"Cannot add stream connection, "
                f"because it is empty: content_type={content_type}, "
                f"cxn={cxn}, session={session}"
            )

        if self.has_cxn(session, details):
            raise ValueError(
                f"Cannot add stream connection, "
                f"because already added: content_type={content_type}, "
                f"cxn={cxn}, session={session}"
            )

        owner = self._cache.setdefault(session, {})
        item = CacheItem(cxn, details, owner)
        owner[details.api_config_key] = item
        return item

    def _get_cache_items(self, session: "Session") -> List[CacheItem]:
        item_by_content_type = self._cache.get(session, {})
        return [item for item in item_by_content_type.values()]

    def _get_cache_item(self, session: "Session", details: "StreamDetails") -> CacheItem:
        cache_item = self._cache[session][details.api_config_key]
        return cache_item

    def is_cxn_alive(self, session: "Session", content_type: "ContentType") -> bool:
        from ._stream_factory import content_type_to_details

        details = content_type_to_details(content_type)
        is_alive = False
        if self.has_cxn(session, details):
            item = self._get_cache_item(session, details)
            is_alive = item.cxn.is_alive()

        return is_alive


stream_cxn_cache: StreamCxnCache = StreamCxnCache()
