# Copyright (c) 2026 kraynux - Licence MIT
"""Tableau des hosts d'une analyse (racine + cibles decouvertes acceptees).
NOUVEAU pour DEEP : screens/show_detail.py selectionne une ligne ici pour
peupler widgets/services_table.py avec les ports de ce host precis — un
scan omega-check n'a jamais qu'un seul host, DEEP potentiellement
plusieurs (ports/scan_repository.py::get_hosts, pluriel)."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_deep.domain.targets.models import Host


class HostsTable(DataTable[str]):
    """Une ligne par host de l'analyse, trie par profondeur (racine en
    premier — voir ports/scan_repository.py::get_hosts)."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("IP", "Hostname", "Profondeur", "Decouvert depuis", "Source")

    def set_hosts(self, hosts: tuple[Host, ...]) -> None:
        self.clear()
        for host in hosts:
            self.add_row(
                host.ip,
                host.hostname or "-",
                str(host.depth_level),
                host.discovered_from or "-",
                host.discovery_source or "-",
                key=host.ip,
            )
