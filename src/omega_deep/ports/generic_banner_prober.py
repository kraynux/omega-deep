# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de la sonde generique par banner (FTP, SMTP, IMAP, etc.).
Identique a omega-check."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.services.models import Service


class GenericBannerProber(Protocol):
    """Implemente par infrastructure/network/socket_generic_banner_prober.py."""

    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        """Lit le banner de bienvenue (la plupart des protocoles texte
        FTP/SMTP/IMAP l'envoient sans requete prealable). Extraction
        logiciel/version volontairement prudente (voir domain/services/
        policies.py::parse_generic_banner). Ne leve jamais pour un echec
        de connexion previsible."""
        ...
