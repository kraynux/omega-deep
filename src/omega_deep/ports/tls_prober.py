# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de la sonde TLS (handshake, cipher, certificat). Identique a
omega-check."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.services.models import Service


class TlsProber(Protocol):
    """Implemente par infrastructure/network/ssl_tls_prober.py."""

    def probe(self, target_ip: str, port: int, sni_hostname: str, timeout: float) -> Service:
        """Remplit UNIQUEMENT les champs tls_* d'un Service (a fusionner
        avec le resultat de HttpProber par domain/services/service.py::
        merge_probes pour les ports HTTPS). Ne leve jamais pour un echec de
        handshake previsible."""
        ...
