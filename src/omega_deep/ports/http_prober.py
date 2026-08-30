# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de la sonde HTTP. Identique a omega-check."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.services.models import Service


class HttpProber(Protocol):
    """Implemente par infrastructure/network/httpx_http_prober.py."""

    def probe(
        self, target_ip: str, port: int, host_header: str, timeout: float, use_tls: bool
    ) -> Service:
        """Remplit protocol_name/software/auth/waf. `use_tls` choisit
        http:// vs https:// (verification de certificat desactivee dans
        les deux cas — l'inspection du certificat lui-meme est le travail
        de ports/tls_prober.py, sonde separee). Ne remplit pas role/
        role_chain. Ne leve jamais pour un echec de connexion previsible :
        retourne un Service avec des champs UNKNOWN et l'erreur dans
        `evidence`."""
        ...
