import random
import ipaddress
import itertools

import pytest
from pytest_lazyfixture import lazy_fixture

from oomnitza_ssrf_protection.ssrf_protection import SSRFProtectionError
from oomnitza_ssrf_protection.oom_async.ssrf_protection import AsyncSecuritySSRFProtection
from oomnitza_ssrf_protection.oom_sync.ssrf_protection import SyncSecuritySSRFProtection


# NOTE: Copied from ipaddress module
_linklocal_networks = (
    "169.254.0.0/16",
    "fe80::/10",
)
_loopback_networks = (
    "127.0.0.0/8",
    "fec0::/10",
)
_multicast_networks = ("224.0.0.0/4", "ff00::/8")
_private_networks = (
    "0.0.0.0/8",
    "10.0.0.0/8",
    "127.0.0.0/8",
    "169.254.0.0/16",
    "172.16.0.0/12",
    "192.0.0.0/29",
    "192.0.0.170/31",
    "192.0.2.0/24",
    "192.168.0.0/16",
    "198.18.0.0/15",
    "198.51.100.0/24",
    "203.0.113.0/24",
    "240.0.0.0/4",
    "::ffff:0:0/96",
    "100::/64",
    "2001::/23",
    "2001:2::/48",
    "2001:db8::/32",
    "2001:10::/28",
    "fc00::/7",
    "fe80::/10",
)
_reserved_networks = (
    "240.0.0.0/4",
    "::/8",
    "100::/8",
    "200::/7",
    "400::/6",
    "800::/5",
    "1000::/4",
    "4000::/3",
    "6000::/3",
    "8000::/3",
    "A000::/3",
    "C000::/3",
    "E000::/4",
    "F000::/5",
    "F800::/6",
    "FE00::/9",
)


@pytest.fixture(
    params=[
        *_linklocal_networks,
        *_loopback_networks,
        *_multicast_networks,
        *_private_networks,
        *_reserved_networks,
    ]
)
def network_to_check(request):
    return request.param


@pytest.fixture(params=["http", "https"])
def url_scheme(request):
    return request.param


def _get_random_ip_addr_from_network(network: str) -> str:
    ip_network = ipaddress.ip_network(network)
    return random.choice(list(itertools.islice(ip_network.hosts(), 3)))


def _get_url_in_network(url_scheme: str, network: str) -> str:
    ipaddr = _get_random_ip_addr_from_network(network)
    return f"{url_scheme}://{ipaddr!s}/what/ever"


@pytest.fixture
def forbidden_url(url_scheme, network_to_check):
    return _get_url_in_network(url_scheme, network_to_check)


@pytest.mark.parametrize(
    "hacky_url",
    [
        "http://localhost/what/ever",
        lazy_fixture("forbidden_url"),
    ],
)
async def test_not_ok(hacky_url):
    with pytest.raises(SSRFProtectionError):
        await AsyncSecuritySSRFProtection().check_url(hacky_url)


@pytest.mark.parametrize(
    "hacky_url",
    [
        "https://oomnitza.com/ever",
        "http://example.com/what/ever",
    ],
)
async def test_ok(hacky_url):
    await AsyncSecuritySSRFProtection().check_url(hacky_url)


def test_ok_allowed_hosts():
    assert AsyncSecuritySSRFProtection(
        allowed_urls=[
            "http://127.0.0.1",
            "http://169.254.1.194",
            "https://localhost/what/ever",
        ]
    ).allowed_hosts == {"127.0.0.1", "169.254.1.194", "localhost"}


@pytest.mark.parametrize(
    "ip_addr",
    [
        "127.0.0.1",
        "169.254.1.194",
    ],
)
async def test_ok_bypass_allowed_hosts(ip_addr):
    to_check = f"http://{ip_addr}/what/ever"

    await AsyncSecuritySSRFProtection(
        allowed_urls=["http://127.0.0.1", "http://169.254.1.194"]
    ).check_url(to_check)


@pytest.mark.parametrize(
    "hacky_url",
    [
        "https://oomnitza.com/ever",
        "http://example.com/what/ever",
    ],
)
def test_ok_sync_call(hacky_url):
    SyncSecuritySSRFProtection().check_url(hacky_url)



@pytest.mark.parametrize(
    "hacky_url",
    [
        "http://localhost/what/ever",
        lazy_fixture("forbidden_url"),
    ],
)
def test_not_ok_sync_call(hacky_url):
    with pytest.raises(SSRFProtectionError):
        SyncSecuritySSRFProtection().check_url(hacky_url)
