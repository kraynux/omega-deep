# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation stdlib du port DnsResolver (ports/dns_resolver.py).
Identique a omega-check."""
from __future__ import annotations

import ipaddress
import socket

from omega_deep.application.exceptions import TargetResolutionError


class SocketDnsResolver:
    """Implemente ports/dns_resolver.py::DnsResolver."""

    def resolve(self, target: str) -> str:
        try:
            ipaddress.ip_address(target)
            return target  # deja une IP, rien a resoudre
        except ValueError:
            pass

        try:
            return socket.gethostbyname(target)
        except OSError as exc:
            raise TargetResolutionError(target, reason=str(exc)) from exc
