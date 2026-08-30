# Copyright (c) 2026 kraynux - Licence MIT
"""Export HTML (Jinja2 + theme d'export choisi). Seul module autorise a
importer jinja2 directement — voir contrat import-linter 'jinja2 seulement
dans infrastructure.exporters.html_exporter' (a activer quand ce module
existe reellement, voir note dans pyproject.toml)."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from omega_lib.theme.policies import DEFAULT_EXPORT_THEME

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host
from omega_deep.infrastructure.exporters.graph_layout import render_architecture_svg
from omega_deep.infrastructure.exporters.html_theme_resolver import resolve_export_palette

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def export_html(
    scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None, theme_name: str = DEFAULT_EXPORT_THEME
) -> str:
    template = _env.get_template("scan_report.html.j2")
    palette = resolve_export_palette(theme_name)
    graph_svg = render_architecture_svg(graph, palette) if graph and graph.edges else ""
    return template.render(scan=scan, hosts=hosts, graph=graph, graph_svg=graph_svg, palette=palette)
