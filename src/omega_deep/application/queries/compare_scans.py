# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : comparer deux scans (recupere les deux agregats, delegue le
diff a domain/reports/comparison.py).

Compare les HOSTS RACINE (`depth_level == 0`, toujours en premiere
position — voir ports/scan_repository.py::get_hosts) des deux scans :
`compare_hosts` (domain, identique a omega-check) compare un host a un
autre, pas un graphe a un autre — comparer les cibles decouvertes une a
une (par IP correspondante) serait une extension possible mais non
demandee (OMEGA-DEEP_SPECIFICATIONS.md §6.1 : "compare_scans identique a
omega-check"), pas ajoutee ici pour eviter la sur-ingenierie."""
from __future__ import annotations

from omega_deep.application.queries.get_scan_details import get_scan_details
from omega_deep.domain.reports.comparison import ScanComparison, compare_hosts
from omega_deep.ports.scan_repository import ScanRepository


def compare_scans(repo: ScanRepository, scan_id_a: str, scan_id_b: str) -> ScanComparison:
    scan_a, hosts_a, _ = get_scan_details(repo, scan_id_a)
    scan_b, hosts_b, _ = get_scan_details(repo, scan_id_b)
    host_a = hosts_a[0] if hosts_a else None
    host_b = hosts_b[0] if hosts_b else None
    return compare_hosts(scan_a, host_a, scan_b, host_b)
