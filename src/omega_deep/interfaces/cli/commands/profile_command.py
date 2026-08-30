# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commande `omega-deep profile list/create/edit/delete/pin/unpin`.
Identique a omega-check."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_deep.application.commands.create_profile import create_profile
from omega_deep.application.commands.delete_profile import delete_profile
from omega_deep.application.commands.pin_profile import pin_profile
from omega_deep.application.commands.unpin_profile import unpin_profile
from omega_deep.application.commands.update_profile import update_profile
from omega_deep.application.queries.list_profiles import list_profiles

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("profile", help="Gerer les profils de ports")
    sub = parser.add_subparsers(dest="profile_command", required=True)

    list_parser = sub.add_parser("list")
    list_parser.set_defaults(handler=handle_list)

    create_parser = sub.add_parser("create")
    create_parser.add_argument("name")
    create_parser.add_argument("--description", default="")
    create_parser.add_argument("--ports", required=True, help="Ports separes par des virgules, ex: 22,80,443")
    create_parser.add_argument("--pin", action="store_true")
    create_parser.set_defaults(handler=handle_create)

    edit_parser = sub.add_parser("edit")
    edit_parser.add_argument("name")
    edit_parser.add_argument("--description", default=None)
    edit_parser.add_argument("--ports", default=None, help="Ports separes par des virgules")
    edit_parser.set_defaults(handler=handle_edit)

    delete_parser = sub.add_parser("delete")
    delete_parser.add_argument("name")
    delete_parser.set_defaults(handler=handle_delete)

    pin_parser = sub.add_parser("pin")
    pin_parser.add_argument("name")
    pin_parser.set_defaults(handler=handle_pin)

    unpin_parser = sub.add_parser("unpin")
    unpin_parser.add_argument("name")
    unpin_parser.set_defaults(handler=handle_unpin)


def _parse_ports(raw: str) -> list[int]:
    return [int(p.strip()) for p in raw.split(",") if p.strip()]


def handle_list(args: argparse.Namespace, container: DependencyContainer) -> str:
    profiles = list_profiles(container.profile_repository)
    lines = []
    for profile in sorted(profiles.values(), key=lambda p: p.name):
        pin_marker = " (pinned)" if profile.pinned else ""
        lines.append(
            f"{profile.name:<12} [{profile.origin}]{pin_marker} — {len(profile.ports)} port(s) — {profile.description}"
        )
    return "\n".join(lines)


def handle_create(args: argparse.Namespace, container: DependencyContainer) -> str:
    profile = create_profile(
        container.profile_repository, args.name, args.description, _parse_ports(args.ports), args.pin
    )
    return f"Profil '{profile.name}' cree ({len(profile.ports)} port(s))."


def handle_edit(args: argparse.Namespace, container: DependencyContainer) -> str:
    ports = _parse_ports(args.ports) if args.ports is not None else None
    profile = update_profile(container.profile_repository, args.name, description=args.description, ports=ports)
    return f"Profil '{profile.name}' mis a jour."


def handle_delete(args: argparse.Namespace, container: DependencyContainer) -> str:
    delete_profile(container.profile_repository, args.name)
    return f"Profil '{args.name}' supprime."


def handle_pin(args: argparse.Namespace, container: DependencyContainer) -> str:
    pin_profile(container.profile_repository, args.name)
    return f"Profil '{args.name}' epingle."


def handle_unpin(args: argparse.Namespace, container: DependencyContainer) -> str:
    unpin_profile(container.profile_repository, args.name)
    return f"Profil '{args.name}' desepingle."
