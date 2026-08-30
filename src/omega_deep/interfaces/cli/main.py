# Copyright (c) 2026 kraynux - Licence MIT
"""Dispatch CLI (analyze/history/show/compare/profile — voir
OMEGA-DEEP_ARBORESCENCE.md §2, `analyze_command.py` au lieu de
`scan_command.py`).

Ne demarre pas l'application lui-meme : __main__.py appelle bootstrap()
puis run(container, argv)."""
from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

from omega_deep.interfaces.cli.commands import (
    analyze_command,
    compare_command,
    history_command,
    profile_command,
    show_command,
)
from omega_deep.interfaces.cli.formatters.text_formatter import format_error

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omega-deep", description="Analyse d'architecture multi-cibles (decouverte + garde-fous)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_command.register(subparsers)
    history_command.register(subparsers)
    show_command.register(subparsers)
    compare_command.register(subparsers)
    profile_command.register(subparsers)
    return parser


def run(container: DependencyContainer, argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = args.handler(args, container)
    except Exception as exc:  # noqa: BLE001 — filet de securite generique (meme choix qu'omega-check)
        print(format_error(str(exc)), file=sys.stderr)
        return 1

    print(result)
    return 0
