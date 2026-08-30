# Copyright (c) 2026 kraynux - Licence MIT
"""Orchestration pure du bounded context 'discovery' : applique le
garde-fou de perimetre (policies.py::is_within_allowed_scope) aux
candidats bruts renvoyes par un DiscoveryProber. Le filtrage vit ici
(domaine), jamais dans l'adaptateur d'infrastructure lui-meme — voir
ports/discovery_prober.py."""
from __future__ import annotations

from omega_deep.domain.discovery.models import DiscoveredTarget
from omega_deep.domain.discovery.policies import is_within_allowed_scope


def filter_discovered_targets(
    candidates: list[DiscoveredTarget], root_ip: str, allowed_subnet: str | None = None
) -> list[DiscoveredTarget]:
    """Ne conserve que les candidats dans le perimetre autorise (voir
    policies.py::is_within_allowed_scope pour la regle exacte, y compris
    le fail-safe sur un hostname non resolu)."""
    return [
        candidate
        for candidate in candidates
        if is_within_allowed_scope(candidate.host, root_ip, allowed_subnet)
    ]
