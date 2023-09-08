import logging
import socket
from ipaddress import ip_address
from typing import Optional, List

from oomnitza_ssrf_protection.ssrf_protection import (
    SSRFProtectionError,
    AnyAddress,
    get_host_from_url,
    is_internal_addr,
    AbstractSecuritySSRFProtection,
)

logger = logging.getLogger(__name__)


class SyncSecuritySSRFProtection(AbstractSecuritySSRFProtection):

    def check_url(self, url: str) -> None:
        """
        Ensure the provided url is not resolved to the private IP address.
        Raises `SSRFProtectionError` in case SSRF or when we're unable to resolve
        the IP address of the target host.
        """
        host = get_host_from_url(url)
        if host in self.allowed_hosts:
            return

        addr = self._get_ip_addr_from_host(host)
        if is_internal_addr(addr):
            raise SSRFProtectionError(
                self.Error.URL_IS_NOT_ALLOWED.format(url=url, addr=str(addr))
            )

    def _get_ip_addr_from_host(
        self,
        ip_addr_or_host: Optional[str],
    ) -> AnyAddress:
        try:
            return ip_address(ip_addr_or_host)
        except ValueError:

            try:
                ip_addr = socket.gethostbyname(ip_addr_or_host)
                return ip_address(ip_addr)

            except (ValueError, TypeError, socket.gaierror):
                raise SSRFProtectionError(
                    self.Error.UNABLE_TO_RESOLVE_IP_ADDRESS.format(host=ip_addr_or_host)
                )
