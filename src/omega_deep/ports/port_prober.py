# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat du scan d'un port TCP/UDP unique. Identique a omega-check.

Un seul port par appel, pas une liste : la boucle sur plusieurs ports est
la responsabilite de application/commands/run_scan.py, pas de
l'adaptateur reseau lui-meme."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.services.models import Port


class PortProber(Protocol):
    """Implemente par infrastructure/network/tcp_port_prober.py."""

    def probe(
        self,
        target_ip: str,
        port: int,
        protocol: str,
        timeout: float,
        retries: int,
    ) -> Port:
        """Retourne un Port avec son etat (open/closed/filtered) et le
        niveau de confiance associe. Ne leve jamais pour un resultat de
        scan attendu (echec de connexion == resultat, pas erreur)."""
        ...
