# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commande `omega-deep show <scan_id> [--format text|json|html]
[--theme NOM] [--output FICHIER]`. Identique a omega-check."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES

from omega_deep.application.commands.export_scan_report import export_scan_report

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("show", help="Afficher les details d'une analyse")
    parser.add_argument("scan_id")
    parser.add_argument("--format", choices=["text", "json", "html"], default="text")
    parser.add_argument(
        "--theme", choices=sorted(EXPORT_PALETTES), default=DEFAULT_EXPORT_THEME,
        help="Theme d'export HTML (ignore pour text/json)",
    )
    parser.add_argument("--output", default=None, help="Ecrire dans ce fichier plutot que stdout")
    parser.set_defaults(handler=handle_show)


def handle_show(args: argparse.Namespace, container: DependencyContainer) -> str:
    content = export_scan_report(
        container.scan_repository, container.report_exporter, args.scan_id, args.format, args.theme
    )

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        return f"Rapport ({args.format}) ecrit dans {args.output}"

    return content
