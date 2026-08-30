# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation socket du port SshProber (banner grabbing seul — voir
ports/ssh_prober.py pour la limite de perimetre assumee). Identique a
omega-check."""
from __future__ import annotations

import socket

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.services.models import Service
from omega_deep.domain.services.policies import parse_ssh_banner


class SocketSshProber:
    """Implemente ports/ssh_prober.py::SshProber."""

    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        try:
            with socket.create_connection((target_ip, port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                raw = sock.recv(256)
        except OSError as exc:
            return Service(evidence=[f"echec de connexion SSH : {exc}"])

        banner = raw.decode("ascii", errors="replace").strip()
        if not banner.startswith("SSH-"):
            return Service(
                protocol_confidence=ConfidenceLevel.UNKNOWN,
                evidence=[f"banner inattendu (pas SSH) : {banner!r}"],
            )

        software, version = parse_ssh_banner(banner)
        return Service(
            protocol_name="SSH",
            protocol_confidence=ConfidenceLevel.VERIFIED,
            software=software,
            software_confidence=ConfidenceLevel.DECLARED if software else ConfidenceLevel.UNKNOWN,
            version=version,
            version_confidence=ConfidenceLevel.DECLARED if version else ConfidenceLevel.UNKNOWN,
            evidence=[f"banner : {banner}"],
        )
