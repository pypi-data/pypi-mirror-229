import logging
import socket

from ipaddress import ip_address
from typing import Optional

import aiodns
from pycares import ares_host_result

from oomnitza_ssrf_protection.ssrf_protection import (
    SSRFProtectionError,
    AnyAddress,
    get_host_from_url,
    is_internal_addr,
    AbstractSecuritySSRFProtection,
)

logger = logging.getLogger(__name__)


missed = None


class AsyncSecuritySSRFProtection(AbstractSecuritySSRFProtection):

    async def check_url(self, url: str) -> None:
        """
        Ensure the provided url is not resolved to the private IP address.
        Raises `SecurityError` in case SSRF or when we're unable to resolve
        the IP address of the target host.
        """
        host = get_host_from_url(url)
        if host in self.allowed_hosts:
            return

        addr = await self._get_ip_addr_from_host(host)
        if is_internal_addr(addr):
            raise SSRFProtectionError(
                self.Error.URL_IS_NOT_ALLOWED.format(url=url, addr=str(addr))
            )

    async def _get_ip_addr_from_host(
        self,
        ip_addr_or_host: Optional[str],
    ) -> AnyAddress:
        try:
            return ip_address(ip_addr_or_host)
        except ValueError:
            try:
                ip_addr = await self._resolve_ip_addr_of_the_host(ip_addr_or_host)
                print(f"ADD: {ip_addr}")
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

