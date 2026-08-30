# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation socket du port GenericBannerProber. Identique a
omega-check."""
from __future__ import annotations

import socket

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.services.models import Service
from omega_deep.domain.services.policies import parse_generic_banner


class SocketGenericBannerProber:
    """Implemente ports/generic_banner_prober.py::GenericBannerProber."""

    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        try:
            with socket.create_connection((target_ip, port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                raw = sock.recv(256)
        except OSError as exc:
            return Service(evidence=[f"echec de connexion : {exc}"])

        if not raw:
            return Service(evidence=["connexion etablie, aucun banner recu"])

        banner = raw.decode("ascii", errors="replace").strip()
        software, version = parse_generic_banner(banner)
        return Service(
            software=software,
            software_confidence=ConfidenceLevel.DECLARED if software else ConfidenceLevel.UNKNOWN,
            version=version,
            version_confidence=ConfidenceLevel.DECLARED if version else ConfidenceLevel.UNKNOWN,
            evidence=[f"banner : {banner}"],
        )
