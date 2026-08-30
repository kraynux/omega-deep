# Copyright (c) 2026 kraynux - Licence MIT
"""Bounded context 'architecture' : reconstruction du graphe de relations
entre hosts scannes (OMEGA-DEEP_SPECIFICATIONS.md §2.4/§5.2).

Phase 1 : modeles uniquement (formes de donnees pures, aucune logique).
La reconstruction (`reconstruct_architecture(hosts) -> ArchitectureGraph`,
les regles de relation proxy_to/redirect_to/backend_of/linked_to) vit
dans policies.py/service.py, pas encore ecrits — phase ulterieure, voir
OMEGA-DEEP_PLAN_DEV.md Phase 4. Pas de dependance a `networkx` ici : une
liste de noeuds (IPs) et d'aretes suffit tant qu'aucun algorithme de
graphe (parcours, plus court chemin) n'est requis."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_deep.core.enums import ConfidenceLevel


@dataclass
class ArchitectureEdge:
    source_ip: str
    target_ip: str
    relation_type: str  # "proxy_to", "redirect_to", "backend_of", "linked_to"
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    evidence: list[str] = field(default_factory=list)


@dataclass
class ArchitectureGraph:
    nodes: list[str] = field(default_factory=list)  # IPs des hosts
    edges: list[ArchitectureEdge] = field(default_factory=list)
    root_node: str = ""  # IP de la cible initiale
