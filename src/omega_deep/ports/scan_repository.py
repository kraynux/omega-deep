# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance et d'historique des scans (voir
~/DEV/SUITE/DECISIONS_ARCHITECTURE.md D-006 : scan_id en UUID, colonne
`tool`, DB separee par outil pour l'instant).

Difference cle avec le port d'omega-check : `save_host`/`get_host`
(singulier) deviennent `save_hosts`/`get_hosts` (pluriel) — un scan DEEP
associe PLUSIEURS hosts au meme scan_id (racine + cibles decouvertes
acceptees, voir application/commands/run_scan.py::scan_host), alors qu'un
scan omega-check n'en a toujours qu'un seul (liste a 1 element cote
DEEP). Ajout de `save_graph`/`get_graph` (OMEGA-DEEP_SPECIFICATIONS.md §7.1,
table `architecture_graph`, un graphe par scan racine)."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host


class ScanRepository(Protocol):
    """Implemente par infrastructure/storage/sqlite/scan_repository.py."""

    def save(self, scan: Scan) -> None: ...

    def get(self, scan_id: str) -> Scan | None: ...

    def list_history(self, *, target: str | None = None, limit: int = 50) -> tuple[Scan, ...]: ...

    def clear(self) -> None: ...

    def save_hosts(self, scan_id: str, hosts: list[Host]) -> None:
        """Persiste l'agregat complet Host -> Port -> Service (cascade)
        pour chaque host, tous associes au meme `scan_id`. Remplace tout
        host deja associe a ce scan."""
        ...

    def get_hosts(self, scan_id: str) -> tuple[Host, ...]:
        """Tous les hosts associes a `scan_id`, tries par `depth_level`
        (racine, depth_level=0, en premier)."""
        ...

    def save_graph(self, scan_id: str, graph: ArchitectureGraph) -> None:
        """Remplace le graphe d'architecture associe a `scan_id`."""
        ...

    def get_graph(self, scan_id: str) -> ArchitectureGraph | None: ...
