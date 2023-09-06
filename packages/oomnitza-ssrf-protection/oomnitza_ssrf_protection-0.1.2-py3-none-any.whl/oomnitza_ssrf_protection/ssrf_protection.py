import asyncio
import logging
import socket
from urllib.parse import urlparse
from ipaddress import ip_address, IPv4Address, IPv6Address
from typing import Optional, Union, List

import aiodns
from pycares import ares_host_result


logger = logging.getLogger(__name__)


AnyAddress = Union[IPv4Address, IPv6Address]


class SSRFProtectionError(Exception):
    pass


missed = None


class SecuritySSRFProtection:
    class Error:
        UNABLE_TO_RESOLVE_IP_ADDRESS = "Unable to resolve IP address for host '{host}'"
        URL_IS_NOT_ALLOWED = "URL {url} is not allowed because it resolves to a private IP address: {addr}"

    def __init__(
        self,
        allowed_urls: Optional[List[str]] = None,
    ):
        self.allowed_hosts = (
            {self._get_host_from_url(url) for url in allowed_urls}
            if allowed_urls
            else {}
        )

    async def check_url(self, url: str) -> None:
        """
        Ensure the provided url is not resolved to the private IP address.
        Raises `SecurityError` in case SSRF or when we're unable to resolve
        the IP address of the target host.
        """
        host = self._get_host_from_url(url)
        if host in self.allowed_hosts:
            return

        addr = await self._get_ip_addr_from_host(host)
        if self._is_internal_addr(addr):
            raise SSRFProtectionError(
                self.Error.URL_IS_NOT_ALLOWED.format(url=url, addr=str(addr))
            )

    def sync_check_url(self, url):
        return asyncio.run(self.check_url(url))

    async def _get_ip_addr_from_host(
        self,
        ip_addr_or_host: Optional[str],
    ) -> AnyAddress:
        try:
            return ip_address(ip_addr_or_host)
        except ValueError:
            try:
                ip_addr = await self._resolve_ip_addr_of_the_host(ip_addr_or_host)
                return ip_address(ip_addr)
            except (ValueError, TypeError, aiodns.error.DNSError):
                raise SSRFProtectionError(
                    self.Error.UNABLE_TO_RESOLVE_IP_ADDRESS.format(host=ip_addr_or_host)
                )

    @staticmethod
    async def _resolve_ip_addr_of_the_host(host: Optional[str]) -> Optional[str]:
        dns_resolver = aiodns.DNSResolver()
        host_result: ares_host_result = await dns_resolver.gethostbyname(
            host,
            family=socket.AF_INET,
        )
        return host_result.addresses[0] if host_result.addresses else missed

    @staticmethod
    def _get_host_from_url(url: str) -> Optional[str]:
        return urlparse(url).hostname

    @staticmethod
    def _is_internal_addr(addr: AnyAddress) -> bool:
        return any(
            [
                addr.is_private,
                addr.is_reserved,
                addr.is_link_local,
                addr.is_loopback,
                addr.is_multicast,
            ]
        )

