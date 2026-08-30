# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de la sonde VNC/RFB (handshake, security types). Identique a
omega-check."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.services.models import Service


class VncProber(Protocol):
    """Implemente par infrastructure/network/socket_vnc_prober.py."""

    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        """Negocie la version RFB et lit les types de securite proposes,
        s'arrete AVANT toute authentification (pas d'identifiants a
        essayer — sonde passive). Ne leve jamais pour un echec de
        connexion previsible."""
        ...
