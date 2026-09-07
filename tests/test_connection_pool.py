import copy
import logging
import time

import pytest
import requests
import urllib3

from fireblocks_sdk import connection_pool
from fireblocks_sdk.connection_pool import (
    DEFAULT_IDLE_TIMEOUT_SECONDS,
    IdleAwareHTTPAdapter,
    IdleAwareHTTPConnectionPool,
    IdleAwareHTTPSConnectionPool,
    IdleAwarePoolManager,
    IdleAwareProxyManager,
    MAX_IDLE_TIMEOUT_SECONDS,
    mount_idle_aware_adapter,
    normalize_idle_timeout_sec,
)

IDLE_LIMIT = 30
IDLE_SINCE_ATTR = "_fireblocks_idle_since"


class FakeConnection:
    """Stand-in for a urllib3 connection.

    A real object rather than a MagicMock: a mock auto-creates every attribute
    read, which would defeat the cases asserting a connection carries no stamp.
    """

    def __init__(self):
        self.is_connected = True  # urllib3's own liveness check reads this
        self.close_calls = 0

    def close(self):
        self.close_calls += 1


def new_pool(pool_cls=IdleAwareHTTPSConnectionPool, **kwargs):
    """Build a pool with room to put connections into.

    urllib3 pre-fills the pool's LifoQueue with `maxsize` None placeholders, so a
    fresh pool is already "full" and _put_conn would discard the connection.
    """
    kwargs.setdefault("idle_timeout_sec", IDLE_LIMIT)
    pool = pool_cls("api.example.com", maxsize=4, **kwargs)
    while not pool.pool.empty():
        pool.pool.get_nowait()
    return pool


@pytest.fixture
def pool():
    return new_pool(port=443)


@pytest.fixture
def conn():
    return FakeConnection()


def age_by(connection, seconds):
    setattr(connection, IDLE_SINCE_ATTR, time.monotonic() - seconds)


# --- stamping -----------------------------------------------------------------

def test_put_conn_stamps_the_idle_moment(pool, conn):
    before = time.monotonic()
    pool._put_conn(conn)
    after = time.monotonic()

    assert before <= getattr(conn, IDLE_SINCE_ATTR) <= after


def test_put_conn_accepts_none_without_raising(pool):
    # urllib3 closes a failed connection and hands None to _put_conn; this is the
    # path taken when a request black-holes, so it must not raise.
    pool._put_conn(None)


def test_a_failed_connection_is_never_stamped(pool, conn):
    pool._put_conn(None)

    assert not hasattr(conn, IDLE_SINCE_ATTR)


# --- eviction on checkout -----------------------------------------------------

def test_connection_idle_under_the_limit_is_reused(pool, conn):
    pool._put_conn(conn)
    age_by(conn, IDLE_LIMIT - 1)

    assert pool._get_conn() is conn
    assert conn.close_calls == 0


def test_connection_idle_over_the_limit_is_closed(pool, conn):
    pool._put_conn(conn)
    age_by(conn, IDLE_LIMIT + 1)

    # Still handed back; urllib3's _validate_conn reconnects before sending.
    assert pool._get_conn() is conn
    assert conn.close_calls == 1


def test_unstamped_connection_is_never_closed(pool, conn):
    assert not hasattr(conn, IDLE_SINCE_ATTR)
    pool.pool.put_nowait(conn)

    assert pool._get_conn() is conn
    assert conn.close_calls == 0


def test_zero_discards_every_pooled_connection(conn):
    # 0 is a real limit, not a disable switch. Regression test for a falsy check.
    pool = new_pool(idle_timeout_sec=0)
    pool._put_conn(conn)

    pool._get_conn()

    assert conn.close_calls == 1


def test_no_limit_keeps_even_a_very_stale_connection(conn):
    pool = new_pool(idle_timeout_sec=-1)
    pool._put_conn(conn)
    age_by(conn, 86400)

    assert pool._get_conn() is conn
    assert conn.close_calls == 0


def test_http_pool_evicts_too(conn):
    http_pool = new_pool(IdleAwareHTTPConnectionPool, port=80)
    http_pool._put_conn(conn)
    age_by(conn, IDLE_LIMIT + 1)

    http_pool._get_conn()

    assert conn.close_calls == 1


def test_reusable_connection_is_re_stamped_on_release(pool, conn):
    pool._put_conn(conn)
    age_by(conn, IDLE_LIMIT - 1)
    pool._get_conn()
    pool._put_conn(conn)

    assert time.monotonic() - getattr(conn, IDLE_SINCE_ATTR) < 1
    assert conn.close_calls == 0


# --- pool managers ------------------------------------------------------------

def test_manager_registers_the_idle_aware_pool_classes():
    manager = IdleAwarePoolManager(idle_timeout_sec=IDLE_LIMIT)

    assert manager.pool_classes_by_scheme["https"] is IdleAwareHTTPSConnectionPool
    assert manager.pool_classes_by_scheme["http"] is IdleAwareHTTPConnectionPool


def test_manager_does_not_mutate_the_shared_module_level_mapping():
    IdleAwarePoolManager(idle_timeout_sec=IDLE_LIMIT)

    assert (
        urllib3.poolmanager.pool_classes_by_scheme["https"]
        is urllib3.HTTPSConnectionPool
    )


def test_manager_propagates_its_timeout_to_the_pools_it_creates():
    manager = IdleAwarePoolManager(idle_timeout_sec=12.5)

    assert manager.connection_from_url("https://x").idle_timeout_sec == 12.5


def test_manager_propagates_no_limit():
    manager = IdleAwarePoolManager(idle_timeout_sec=-1)

    assert manager.connection_from_url("https://x").idle_timeout_sec is None


def test_manager_propagates_zero():
    manager = IdleAwarePoolManager(idle_timeout_sec=0)

    assert manager.connection_from_url("https://x").idle_timeout_sec == 0


# --- the requests adapter -----------------------------------------------------

def test_adapter_installs_an_idle_aware_pool_manager():
    adapter = IdleAwareHTTPAdapter(idle_timeout_sec=17)

    assert isinstance(adapter.poolmanager, IdleAwarePoolManager)


def test_adapter_pools_carry_the_configured_limit():
    adapter = IdleAwareHTTPAdapter(idle_timeout_sec=17)
    pool = adapter.poolmanager.connection_from_url("https://api.example.com")

    assert isinstance(pool, IdleAwareHTTPSConnectionPool)
    assert pool.idle_timeout_sec == 17


def test_adapter_defaults_to_the_sdk_default():
    adapter = IdleAwareHTTPAdapter()
    pool = adapter.poolmanager.connection_from_url("https://api.example.com")

    assert pool.idle_timeout_sec == DEFAULT_IDLE_TIMEOUT_SECONDS


def test_adapter_keeps_requests_pool_sizing_kwargs():
    adapter = IdleAwareHTTPAdapter(pool_connections=3, pool_maxsize=7, idle_timeout_sec=5)
    pool = adapter.poolmanager.connection_from_url("https://api.example.com")

    assert pool.pool.maxsize == 7
    assert pool.idle_timeout_sec == 5


def test_adapter_is_usable_by_a_requests_session():
    session = requests.Session()
    session.mount("https://", IdleAwareHTTPAdapter(idle_timeout_sec=11))

    adapter = session.get_adapter("https://api.example.com")
    assert isinstance(adapter, IdleAwareHTTPAdapter)
    assert adapter.poolmanager.connection_from_url(
        "https://api.example.com"
    ).idle_timeout_sec == 11


def test_adapter_survives_deepcopy():
    # requests deep-copies adapters when copying a Session.
    adapter = copy.deepcopy(IdleAwareHTTPAdapter(idle_timeout_sec=9))

    assert isinstance(adapter.poolmanager, IdleAwarePoolManager)
    assert adapter.poolmanager.connection_from_url("https://x").idle_timeout_sec == 9


# --- mounting onto a session --------------------------------------------------

def test_mount_replaces_both_stock_adapters():
    session = requests.Session()

    mount_idle_aware_adapter(session, idle_timeout_sec=19)

    assert set(session.adapters) >= {"https://", "http://"}
    assert all(
        isinstance(a, IdleAwareHTTPAdapter) for a in session.adapters.values()
    ), "a stock HTTPAdapter was left mounted"


def test_mount_propagates_the_limit_to_both_schemes():
    session = requests.Session()
    mount_idle_aware_adapter(session, idle_timeout_sec=19)

    for url, expected_pool in (
        ("https://api.example.com", IdleAwareHTTPSConnectionPool),
        ("http://api.example.com", IdleAwareHTTPConnectionPool),
    ):
        pool = session.get_adapter(url).poolmanager.connection_from_url(url)
        assert isinstance(pool, expected_pool)
        assert pool.idle_timeout_sec == 19


def test_mount_returns_the_adapter_and_shares_one_instance():
    session = requests.Session()

    adapter = mount_idle_aware_adapter(session)

    assert session.get_adapter("https://x") is adapter
    assert session.get_adapter("http://x") is adapter


def test_mounted_session_survives_being_closed_twice():
    # The same adapter is mounted under two keys, so Session.close() reaches it
    # twice; poolmanager.clear() must tolerate that.
    session = requests.Session()
    mount_idle_aware_adapter(session)

    session.close()
    session.close()


def test_mount_defaults_to_the_sdk_default():
    session = requests.Session()
    mount_idle_aware_adapter(session)

    pool = session.get_adapter("https://x").poolmanager.connection_from_url("https://x")
    assert pool.idle_timeout_sec == DEFAULT_IDLE_TIMEOUT_SECONDS


# --- proxies ------------------------------------------------------------------

def test_http_proxy_manager_is_idle_aware():
    adapter = IdleAwareHTTPAdapter(idle_timeout_sec=13)
    manager = adapter.proxy_manager_for("http://proxy.example.com:3128")

    assert isinstance(manager, IdleAwareProxyManager)
    assert manager.connection_from_url("https://x").idle_timeout_sec == 13


def test_proxy_manager_is_cached():
    adapter = IdleAwareHTTPAdapter(idle_timeout_sec=13)
    first = adapter.proxy_manager_for("http://proxy.example.com:3128")

    assert adapter.proxy_manager_for("http://proxy.example.com:3128") is first


def test_socks_proxy_is_left_on_stock_urllib3():
    pytest.importorskip("socks", reason="PySocks not installed")
    adapter = IdleAwareHTTPAdapter(idle_timeout_sec=13)
    manager = adapter.proxy_manager_for("socks5://proxy.example.com:1080")

    # SOCKSProxyManager installs its own pool classes; we must not replace them.
    assert not isinstance(manager, IdleAwareProxyManager)


# --- configuration ------------------------------------------------------------

def test_default_matches_the_java_sdk():
    assert DEFAULT_IDLE_TIMEOUT_SECONDS == 30


@pytest.mark.parametrize("value,expected", [(60, 60.0), (12.5, 12.5), ("45", 45.0), (0, 0)])
def test_normalize_keeps_non_negative_values(value, expected):
    assert normalize_idle_timeout_sec(value) == expected


def test_normalize_treats_none_as_not_configured():
    assert normalize_idle_timeout_sec(None) == DEFAULT_IDLE_TIMEOUT_SECONDS


@pytest.mark.parametrize("value", [-1, -30])
def test_normalize_treats_negative_as_no_limit(value):
    assert normalize_idle_timeout_sec(value) is None


def test_normalize_keeps_the_maximum_itself():
    assert normalize_idle_timeout_sec(MAX_IDLE_TIMEOUT_SECONDS) == MAX_IDLE_TIMEOUT_SECONDS


def test_normalize_caps_values_above_the_maximum():
    # Only reachable when the pools are built directly; mount_idle_aware_adapter
    # rejects these before they get here.
    assert normalize_idle_timeout_sec(600) == MAX_IDLE_TIMEOUT_SECONDS


def test_normalize_warns_when_it_caps(caplog):
    with caplog.at_level(logging.WARNING, logger="fireblocks_sdk.connection_pool"):
        normalize_idle_timeout_sec(600)
    assert "Capping" in caplog.text


def test_capping_does_not_apply_to_no_limit():
    # -1 is not "a very small number", it is the disable switch, so the ceiling
    # must not turn it into MAX.
    assert normalize_idle_timeout_sec(-1) is None


def test_mount_rejects_a_limit_above_the_maximum():
    # Raised at construction so a bad setting is not discovered mid-request.
    with pytest.raises(ValueError, match="at most"):
        mount_idle_aware_adapter(requests.Session(), MAX_IDLE_TIMEOUT_SECONDS + 1)


def test_mount_accepts_the_maximum():
    adapter = mount_idle_aware_adapter(requests.Session(), MAX_IDLE_TIMEOUT_SECONDS)
    pool = adapter.poolmanager.connection_from_url("https://api.fireblocks.io")
    assert pool.idle_timeout_sec == MAX_IDLE_TIMEOUT_SECONDS


def test_mount_still_allows_disabling():
    adapter = mount_idle_aware_adapter(requests.Session(), -1)
    pool = adapter.poolmanager.connection_from_url("https://api.fireblocks.io")
    assert pool.idle_timeout_sec is None


def test_normalize_falls_back_to_the_default_on_garbage():
    assert normalize_idle_timeout_sec("not-a-number") == DEFAULT_IDLE_TIMEOUT_SECONDS


# --- end-to-end wiring through the SDK ----------------------------------------

def sdk(**kwargs):
    from fireblocks_sdk.sdk import FireblocksSDK

    return FireblocksSDK("dummy-private-key", "dummy-api-key", **kwargs)


def test_sdk_mounts_the_idle_aware_adapter():
    client = sdk()

    for prefix in ("https://api.fireblocks.io", "http://api.fireblocks.io"):
        assert isinstance(client.http_session.get_adapter(prefix), IdleAwareHTTPAdapter)


def test_sdk_applies_the_default_when_not_configured():
    pool = (
        sdk().http_session.get_adapter("https://api.fireblocks.io")
        .poolmanager.connection_from_url("https://api.fireblocks.io")
    )

    assert pool.idle_timeout_sec == DEFAULT_IDLE_TIMEOUT_SECONDS


@pytest.mark.parametrize("configured,expected", [(17, 17.0), (0, 0), (-1, None)])
def test_sdk_passes_the_configured_limit_through(configured, expected):
    pool = (
        sdk(connection_idle_timeout_sec=configured)
        .http_session.get_adapter("https://api.fireblocks.io")
        .poolmanager.connection_from_url("https://api.fireblocks.io")
    )

    assert pool.idle_timeout_sec == expected
