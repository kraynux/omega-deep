# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation socket du port GenericBannerProber. Identique a
omega-check."""
from __future__ import annotations

import socket

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.services.models import Service
from omega_deep.domain.services.policies import parse_generic_banner
from omega_deep.shared.i18n import _


class SocketGenericBannerProber:
    """Implemente ports/generic_banner_prober.py::GenericBannerProber."""

    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        try:
            with socket.create_connection((target_ip, port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                raw = sock.recv(256)
        except OSError as exc:
            return Service(evidence=[_("échec de connexion : {exc}").format(exc=exc)])

        if not raw:
            return Service(evidence=[_("connexion établie, aucun banner reçu")])

        banner = raw.decode("ascii", errors="replace").strip()
        software, version = parse_generic_banner(banner)
        return Service(
            software=software,
            software_confidence=ConfidenceLevel.DECLARED if software else ConfidenceLevel.UNKNOWN,
            version=version,
            version_confidence=ConfidenceLevel.DECLARED if version else ConfidenceLevel.UNKNOWN,
            evidence=[_("banner : {banner}").format(banner=banner)],
        )
