# Copyright (c) 2026 kraynux - Licence MIT
"""Orchestration pure du bounded context 'architecture' :
`reconstruct_architecture` (OMEGA-DEEP_SPECIFICATIONS.md §5.2/§6.2).

Reconstruit le graphe uniquement a partir de la provenance de decouverte
deja portee par chaque Host (`discovered_from`/`discovery_source`/
`discovery_confidence`, domain/targets/models.py — remplis quand une
DiscoveredTarget est acceptee puis scannee, voir D-003) : pas besoin de
re-parcourir les DiscoveredTarget bruts, cette fonction ne prend que la
liste des hosts deja scannes, exactement la signature du spec."""
from __future__ import annotations

from omega_deep.domain.architecture.models import ArchitectureEdge, ArchitectureGraph
from omega_deep.domain.architecture.policies import relation_type_for_source
from omega_deep.domain.targets.models import Host
from omega_deep.shared.i18n import _


def reconstruct_architecture(hosts: list[Host]) -> ArchitectureGraph:
    """`root_node` est le premier host de `depth_level == 0` trouve (la
    cible initiale, jamais decouverte) — chaine vide si aucun (liste
    vide, ou aucun host racine present)."""
    nodes = [host.ip for host in hosts]

    edges: list[ArchitectureEdge] = []
    for host in hosts:
        if host.discovered_from is None:
            continue
        edges.append(
            ArchitectureEdge(
                source_ip=host.discovered_from,
                target_ip=host.ip,
                relation_type=relation_type_for_source(host.discovery_source),
                confidence=host.discovery_confidence,
                evidence=[_("découvert via {discovery_source}").format(discovery_source=host.discovery_source)] if host.discovery_source else [],
            )
        )

    root_candidates = [host.ip for host in hosts if host.depth_level == 0]
    root_node = root_candidates[0] if root_candidates else ""

    return ArchitectureGraph(nodes=nodes, edges=edges, root_node=root_node)
