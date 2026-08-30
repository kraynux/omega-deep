# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : recuperer un scan detaille (Scan + tous ses hosts + son
graphe d'architecture, sans recalcul). Difference cle avec omega-check :
`hosts` est un tuple (pluriel — un scan DEEP a potentiellement plusieurs
hosts) et le graphe est inclus (OMEGA-DEEP_SPECIFICATIONS.md §6.2 :
"recuperer les details d'un scan (avec graphe)")."""
from __future__ import annotations

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.exceptions import ScanNotFoundError
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host
from omega_deep.ports.scan_repository import ScanRepository


def get_scan_details(
    repo: ScanRepository, scan_id: str
) -> tuple[Scan, tuple[Host, ...], ArchitectureGraph | None]:
    scan = repo.get(scan_id)
    if scan is None:
        raise ScanNotFoundError(scan_id)
    return scan, repo.get_hosts(scan_id), repo.get_graph(scan_id)
