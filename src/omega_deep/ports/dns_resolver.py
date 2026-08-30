# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de resolution DNS (cible initiale -> IP, une seule fois, avant
le scan — voir domain/targets/validation.py). Identique a omega-check."""
from __future__ import annotations

from typing import Protocol


class DnsResolver(Protocol):
    """Implemente par infrastructure/network/socket_dns_resolver.py."""

    def resolve(self, target: str) -> str:
        """Retourne l'IP resolue de `target` (deja une IP -> retournee
        telle quelle). Leve TargetResolutionError (application/exceptions.py
        — pas infrastructure/, voir la Dependency Rule) si la resolution
        echoue."""
        ...
