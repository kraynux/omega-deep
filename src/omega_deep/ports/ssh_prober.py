# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de la sonde SSH (banner grabbing). Identique a omega-check."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.services.models import Service


class SshProber(Protocol):
    """Implemente par infrastructure/network/socket_ssh_prober.py."""

    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        """Remplit protocol_name/software/version depuis le banner SSH.
        `auth_types` reste vide (UNKNOWN) : l'enumeration reelle des
        methodes d'authentification demande un echange de cles SSH
        partiel, hors-scope. Ne leve jamais pour un echec de connexion
        previsible."""
        ...
