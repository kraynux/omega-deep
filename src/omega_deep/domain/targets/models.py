# Copyright (c) 2026 kraynux - Licence MIT
"""Bounded context 'targets' : un host scanne (cible initiale ou cible
decouverte et acceptee).

Etend le Host d'omega-check (champs de base identiques) avec les champs
de tracabilite de decouverte de DEEP (OMEGA-DEEP_SPECIFICATIONS.md §2.3) :
a quelle profondeur ce host a ete atteint, depuis quel host parent, par
quelle source d'indice, avec quelle confiance. `depth_level=0` pour la
cible initiale (jamais decouverte, pas de parent)."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.services.models import Port


@dataclass
class Host:
    ip: str
    hostname: str | None = None
    os_guess: str | None = None
    os_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    firewall_network_present: bool | None = None
    firewall_network_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    waf_present: bool | None = None
    waf_name_guess: str | None = None
    waf_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    exposure: str | None = None  # "public", "internal", "mixed", "unknown"
    exposure_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    ports: list[Port] = field(default_factory=list)

    # Champs specifiques a DEEP (tracabilite de decouverte)
    depth_level: int = 0  # 0 = cible initiale, 1 = decouverte directe, etc.
    discovered_from: str | None = None  # IP du host qui a permis la decouverte
    discovery_source: str | None = None  # "header", "certificate", "redirection", "html_link"
    discovery_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
