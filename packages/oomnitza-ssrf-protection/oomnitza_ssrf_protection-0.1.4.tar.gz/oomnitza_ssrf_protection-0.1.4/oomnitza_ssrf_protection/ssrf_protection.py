from abc import ABC
from ipaddress import IPv4Address, IPv6Address
from typing import Union, Optional, List
from urllib.parse import urlparse


class SSRFProtectionError(Exception):
    pass


AnyAddress = Union[
    IPv4Address,
    IPv6Address,
]


def get_host_from_url(url: str) -> Optional[str]:
    return urlparse(url).hostname


def is_internal_addr(addr: AnyAddress) -> bool:
    return any(
        [
            addr.is_private,
            addr.is_reserved,
            addr.is_link_local,
            addr.is_loopback,
            addr.is_multicast,
        ]
    )


class AbstractSecuritySSRFProtection(ABC):
    class Error:
        UNABLE_TO_RESOLVE_IP_ADDRESS = (
            "Unable to resolve IP address for host '{host}'"
        )
        URL_IS_NOT_ALLOWED = (
            "URL {url} is not allowed because it resolves to a private IP address: {addr}"
        )

    def __init__(
            self,
            allowed_urls: Optional[List[str]] = None,
    ):
        self.allowed_hosts = (
            {get_host_from_url(url) for url in allowed_urls}
            if allowed_urls
            else {}
        )
