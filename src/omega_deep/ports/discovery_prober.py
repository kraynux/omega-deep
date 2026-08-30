# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'extraction d'indices de decouverte (headers, redirection,
certificat, liens HTML — OMEGA-DEEP_SPECIFICATIONS.md §4.2). NOUVEAU par
rapport a omega-check (D-002/D-005 : premiere fois que ce besoin existe
dans la suite)."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.discovery.models import DiscoveredTarget


class DiscoveryProber(Protocol):
    """Implemente par infrastructure/discovery/http_discovery_prober.py.

    Retourne les candidats bruts (etat PROPOSED, confiance deja assignee
    par source), SANS filtrage de perimetre — le filtrage (subnet/IP
    privee, garde-fou de securite) est une decision domaine, appliquee
    separement par domain/discovery/service.py::filter_discovered_targets,
    jamais baked dans l'adaptateur d'infrastructure lui-meme."""

    def probe(
        self,
        target_ip: str,
        port: int,
        host_header: str,
        timeout: float,
        use_tls: bool,
        tls_cert_san: list[str],
    ) -> list[DiscoveredTarget]:
        """`tls_cert_san` : deja collecte par ports/tls_prober.py (evite un
        second handshake TLS juste pour relire le certificat). Ne leve
        jamais pour un echec de connexion previsible : liste vide."""
        ...
