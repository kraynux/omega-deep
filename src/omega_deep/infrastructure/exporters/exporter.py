# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation composite du port ReportExporter, delegue aux modules
specifiques par format — seul point d'entree expose a app/bootstrap.py."""
from __future__ import annotations

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host
from omega_deep.infrastructure.exporters.html_exporter import export_html
from omega_deep.infrastructure.exporters.json_exporter import export_json
from omega_deep.infrastructure.exporters.text_exporter import export_text


class CompositeReportExporter:
    """Implemente ports/report_exporter.py::ReportExporter."""

    def export_json(self, scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None) -> str:
        return export_json(scan, hosts, graph)

    def export_text(self, scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None) -> str:
        return export_text(scan, hosts, graph)

    def export_html(
        self,
        scan: Scan,
        hosts: tuple[Host, ...],
        graph: ArchitectureGraph | None,
        theme_name: str = DEFAULT_EXPORT_THEME,
    ) -> str:
        return export_html(scan, hosts, graph, theme_name)
