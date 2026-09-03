"""Idle-connection eviction for the requests/urllib3 connection pool.

``requests.Session`` keeps pooled connections indefinitely, so a connection that
a proxy has already dropped can still be handed out, failing the request with
``ConnectionResetError``. This module discards any connection that has been idle
longer than the configured limit and lets urllib3 reconnect transparently.

Configure it through ``FireblocksSDK``::

    FireblocksSDK(private_key, api_key, connection_idle_timeout_sec=60)

Leave it unset for :data:`DEFAULT_IDLE_TIMEOUT_SECONDS`, use ``0`` to open a fresh
connection for every request, or ``-1`` for no limit.
"""

import logging
import time

import urllib3
from requests.adapters import DEFAULT_POOLBLOCK, HTTPAdapter

log = logging.getLogger(__name__)

DEFAULT_IDLE_TIMEOUT_SECONDS = 30
"""Seconds a pooled connection may sit idle. Matches the Fireblocks Java SDK."""

_IDLE_SINCE_ATTR = "_fireblocks_idle_since"


def normalize_idle_timeout_sec(value):
    """Resolve a configured idle timeout to seconds, or ``None`` for no limit.

    ``None`` means "not configured" and yields :data:`DEFAULT_IDLE_TIMEOUT_SECONDS`.
    A negative value means no limit. ``0`` is a real value: it makes every pooled
    connection stale on release.
    """
    if value is None:
        return DEFAULT_IDLE_TIMEOUT_SECONDS

    try:
        seconds = float(value)
    except (TypeError, ValueError):
        log.warning(
            "Ignoring invalid connection_idle_timeout_sec=%r; using default of %ss",
            value,
            DEFAULT_IDLE_TIMEOUT_SECONDS,
        )
        return DEFAULT_IDLE_TIMEOUT_SECONDS

    if seconds < 0:
        return None

    return seconds


class _IdleAwarePoolMixin:
    """Discards pooled connections that have been idle for too long.

    urllib3 may gain this natively as ``idle_timeout`` (PR #3275); if it does,
    these classes can be dropped in favour of it.
    """

    def __init__(self, *args, **kwargs):
        # Consumed here so urllib3 never sees an unknown keyword.
        idle_timeout_sec = kwargs.pop("idle_timeout_sec", None)
        super().__init__(*args, **kwargs)
        self.idle_timeout_sec = normalize_idle_timeout_sec(idle_timeout_sec)

    def _put_conn(self, conn):
        # conn is None when urllib3 discarded a failed connection.
        if conn is not None:
            setattr(conn, _IDLE_SINCE_ATTR, time.monotonic())
        super()._put_conn(conn)

    def _get_conn(self, timeout=None):
        conn = super()._get_conn(timeout=timeout)

        # Tested against the sentinel: a configured 0 is falsy but is a real limit.
        if conn is None or self.idle_timeout_sec is None:
            return conn

        idle_since = getattr(conn, _IDLE_SINCE_ATTR, None)
        if idle_since is None:
            # Never pooled, so not idle.
            return conn

        idle_for = time.monotonic() - idle_since
        if idle_for > self.idle_timeout_sec:
            log.debug(
                "Discarding connection to %s:%s idle for %.1fs (limit %ss)",
                self.host,
                self.port,
                idle_for,
                self.idle_timeout_sec,
            )
            # _validate_conn reconnects before the request is sent.
            conn.close()

        return conn


class IdleAwareHTTPConnectionPool(_IdleAwarePoolMixin, urllib3.HTTPConnectionPool):
    """``urllib3.HTTPConnectionPool`` that evicts connections idle too long."""


class IdleAwareHTTPSConnectionPool(_IdleAwarePoolMixin, urllib3.HTTPSConnectionPool):
    """``urllib3.HTTPSConnectionPool`` that evicts connections idle too long."""


class _IdleAwareManagerMixin:
    """Makes a pool manager hand out the idle-aware pools above."""

    def __init__(self, *args, **kwargs):
        # Kept off connection_pool_kw, which urllib3 turns into PoolKey fields.
        idle_timeout_sec = kwargs.pop("idle_timeout_sec", None)
        super().__init__(*args, **kwargs)
        self._idle_timeout_sec = idle_timeout_sec
        # PoolManager.__init__ assigns urllib3's shared mapping, so replace it here
        # with a fresh dict of our own.
        self.pool_classes_by_scheme = {
            "http": IdleAwareHTTPConnectionPool,
            "https": IdleAwareHTTPSConnectionPool,
        }

    def _new_pool(self, scheme, host, port, request_context=None):
        if request_context is None:
            request_context = self.connection_pool_kw
        request_context = dict(request_context, idle_timeout_sec=self._idle_timeout_sec)
        return super()._new_pool(scheme, host, port, request_context)


class IdleAwarePoolManager(_IdleAwareManagerMixin, urllib3.PoolManager):
    """``urllib3.PoolManager`` whose pools evict connections idle too long."""


class IdleAwareProxyManager(_IdleAwareManagerMixin, urllib3.ProxyManager):
    """``urllib3.ProxyManager`` whose pools evict connections idle too long."""


class IdleAwareHTTPAdapter(HTTPAdapter):
    """``requests`` adapter whose connection pools evict idle connections.

    Mount it on a session to apply the limit::

        session.mount("https://", IdleAwareHTTPAdapter(idle_timeout_sec=30))
    """

    # requests restores only these when unpickling or deep-copying an adapter, and
    # then calls init_poolmanager -- so the limit has to be listed here or it is
    # lost and init_poolmanager raises AttributeError.
    __attrs__ = HTTPAdapter.__attrs__ + ["_idle_timeout_sec"]

    def __init__(self, *args, **kwargs):
        # Set before super().__init__, which calls init_poolmanager.
        self._idle_timeout_sec = kwargs.pop("idle_timeout_sec", None)
        super().__init__(*args, **kwargs)

    def init_poolmanager(
        self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs
    ):
        # Delegate first so the attributes requests needs for pickling are set,
        # then swap in an idle-aware manager.
        super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)
        self.poolmanager = IdleAwarePoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            idle_timeout_sec=self._idle_timeout_sec,
            **pool_kwargs,
        )

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        if proxy in self.proxy_manager:
            return self.proxy_manager[proxy]

        # SOCKSProxyManager installs its own pool classes.
        if proxy.lower().startswith("socks"):
            return super().proxy_manager_for(proxy, **proxy_kwargs)

        manager = self.proxy_manager[proxy] = IdleAwareProxyManager(
            proxy,
            proxy_headers=self.proxy_headers(proxy),
            num_pools=self._pool_connections,
            maxsize=self._pool_maxsize,
            block=self._pool_block,
            idle_timeout_sec=self._idle_timeout_sec,
            **proxy_kwargs,
        )
        return manager


def mount_idle_aware_adapter(session, idle_timeout_sec=None):
    """Replace a requests session's HTTP adapters with idle-aware ones.

    Mounts on both schemes, as requests' own ``Session.__init__`` does.

    :param session: the ``requests.Session`` to upgrade.
    :param idle_timeout_sec: seconds a pooled connection may sit idle; see
        :func:`normalize_idle_timeout_sec` for how the value is interpreted.
    :return: the mounted adapter.
    """
    adapter = IdleAwareHTTPAdapter(idle_timeout_sec=idle_timeout_sec)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return adapter
