"""Outbound URL validation for registered provider endpoints."""

import ipaddress
import socket
from collections.abc import Callable, Iterable
from urllib.parse import urlsplit


class UnsafeOutboundUrl(ValueError):
    pass


def validate_outbound_url(
    url: str,
    *,
    allowed_hosts: Iterable[str],
    resolver: Callable[..., list[tuple]] = socket.getaddrinfo,
) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeOutboundUrl("Outbound URL is not allowed")

    hostname = parsed.hostname.rstrip(".").lower()
    allowlist = {host.rstrip(".").lower() for host in allowed_hosts}
    if hostname not in allowlist:
        raise UnsafeOutboundUrl("Outbound URL is not allowed")

    try:
        addresses = resolver(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise UnsafeOutboundUrl("Outbound host could not be resolved") from exc
    if not addresses:
        raise UnsafeOutboundUrl("Outbound host could not be resolved")

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise UnsafeOutboundUrl("Outbound URL is not allowed")
    return url
