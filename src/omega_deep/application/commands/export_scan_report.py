# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : exporter un scan dans un format donne. `theme_name` ne
s'applique qu'au HTML (JSON/texte n'ont pas de notion de theme visuel)."""
from __future__ import annotations

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME

from omega_deep.application.queries.get_scan_details import get_scan_details
from omega_deep.ports.report_exporter import ReportExporter
from omega_deep.ports.scan_repository import ScanRepository

_KNOWN_FORMATS = ("json", "text", "html")


def export_scan_report(
    repo: ScanRepository,
    exporter: ReportExporter,
    scan_id: str,
    fmt: str,
    theme_name: str = DEFAULT_EXPORT_THEME,
) -> str:
    if fmt not in _KNOWN_FORMATS:
        raise ValueError(f"format d'export inconnu : {fmt!r} (attendu: {_KNOWN_FORMATS})")

    scan, hosts, graph = get_scan_details(repo, scan_id)
    if fmt == "json":
        return exporter.export_json(scan, hosts, graph)
    if fmt == "text":
        return exporter.export_text(scan, hosts, graph)
    return exporter.export_html(scan, hosts, graph, theme_name)
