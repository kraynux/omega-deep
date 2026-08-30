# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commande `omega-deep history`. Identique a omega-check."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_deep.application.queries.get_scan_history import get_scan_history

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("history", help="Lister les analyses precedentes")
    parser.add_argument("--target", default=None, help="Filtrer par cible")
    parser.add_argument("--limit", type=int, default=50)
    parser.set_defaults(handler=handle_history)


def handle_history(args: argparse.Namespace, container: DependencyContainer) -> str:
    scans = get_scan_history(container.scan_repository, target=args.target, limit=args.limit)
    if not scans:
        return "Aucune analyse enregistree."

    lines = [
        f"{s.id}  {s.created_at}  {s.target} ({s.target_ip})  mode={s.analysis_mode.value}  {s.status.value}"
        for s in scans
    ]
    return "\n".join(lines)
