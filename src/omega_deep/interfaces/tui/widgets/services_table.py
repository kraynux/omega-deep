# Copyright (c) 2026 kraynux - Licence MIT
"""Tableau des ports/services d'UN host (voir widgets/hosts_table.py pour
la selection du host, un scan DEEP en ayant potentiellement plusieurs).
Porte depuis omega-check (D-007/D-008), modele Port/Service identique."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_deep.domain.targets.models import Host
from omega_deep.shared.i18n import _


class ServicesTable(DataTable[str]):
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns(_("Port"), _("État"), _("Service"), _("Logiciel"), _("Rôle"))

    def set_host(self, host: Host | None) -> None:
        self.clear()
        if host is None:
            return
        for port in sorted(host.ports, key=lambda p: p.port_number):
            service = port.service
            software = f"{service.software} {service.version or ''}".strip() if service and service.software else "-"
            role = f"{service.role} [{service.role_confidence.value}]" if service and service.role else "-"
            protocol_name = service.protocol_name if service and service.protocol_name else "-"
            self.add_row(
                f"{port.port_number}/{port.protocol}",
                f"{port.state.value} [{port.state_confidence.value}]",
                protocol_name,
                software,
                role,
                key=str(port.port_number),
            )
