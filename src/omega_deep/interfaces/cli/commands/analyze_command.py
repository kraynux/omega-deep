# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commande `omega-deep analyze <cible> --profile <nom> [--max-depth N]
[--max-targets N] [--subnet CIDR] [--auto-validate]`
(OMEGA-DEEP_SPECIFICATIONS.md §8 — au lieu de scan_command.py, voir
OMEGA-DEEP_ARBORESCENCE.md §2).

Seul point du projet qui orchestre le flux multi-cibles complet (racine ->
decouverte -> validation utilisateur -> cibles acceptees -> reconstruction) :
`validate_targets` exige une confirmation par cible (D-003), donc cette
boucle ne peut PAS vivre dans un use case application pur (voir
application/commands/run_scan.py). Un seul Scan pour toute l'analyse (voir
ports/scan_repository.py::save_hosts) — pas un par host."""
from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

from omega_deep.application.commands.discover_targets import discover_targets
from omega_deep.application.commands.reconstruct_architecture import reconstruct_architecture
from omega_deep.application.commands.scan_host import scan_host
from omega_deep.application.commands.validate_targets import validate_targets
from omega_deep.application.exceptions import TargetResolutionError
from omega_deep.application.queries.list_profiles import get_profile
from omega_deep.core.enums import AnalysisMode, ScanMode, ScanStatus
from omega_deep.domain.discovery.models import DiscoveredTarget, DiscoveryState
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host
from omega_deep.domain.targets.validation import normalize_target_input
from omega_deep.interfaces.cli.formatters.text_formatter import format_scan_result

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("analyze", help="Analyser une cible (scan + decouverte multi-cibles)")
    parser.add_argument("target", help="IP ou hostname de la cible initiale")
    parser.add_argument("--profile", default="minimal", help="Profil de ports (defaut: minimal)")
    parser.add_argument("--max-depth", type=int, default=3, help="Profondeur max de decouverte (defaut: 3)")
    parser.add_argument(
        "--max-targets", type=int, default=10, help="Nombre max de cibles supplementaires (defaut: 10)"
    )
    parser.add_argument("--subnet", default=None, help="Subnet autorise pour la decouverte (ex: 192.168.1.0/24)")
    parser.add_argument(
        "--auto-validate", action="store_true",
        help="Valider automatiquement toutes les cibles decouvertes (DECONSEILLE)",
    )
    parser.set_defaults(handler=handle_analyze)


def handle_analyze(args: argparse.Namespace, container: DependencyContainer) -> str:
    profile = get_profile(container.profile_repository, args.profile)
    target = normalize_target_input(args.target)

    if args.auto_validate:
        print(
            "ATTENTION : --auto-validate accepte automatiquement TOUTES les cibles "
            "decouvertes, sans revue. Deconseille.",
            file=sys.stderr,
        )

    try:
        root_ip = container.dns_resolver.resolve(target)
    except TargetResolutionError:
        scan = Scan(
            id=container.id_factory(), created_at=container.clock().isoformat(), target=target,
            profile_name=profile.name, profile_origin=profile.origin, ports_scanned=list(profile.ports),
            scan_mode=ScanMode.PROFILE, status=ScanStatus.FAILED, analysis_mode=AnalysisMode.DEEP,
        )
        container.scan_repository.save(scan)
        return format_scan_result(scan, ())

    scan = Scan(
        id=container.id_factory(),
        created_at=container.clock().isoformat(),
        target=target,
        target_ip=root_ip,
        profile_name=profile.name,
        profile_origin=profile.origin,
        ports_scanned=list(profile.ports),
        scan_mode=ScanMode.PROFILE,
        status=ScanStatus.RUNNING,
        analysis_mode=AnalysisMode.DEEP,
        root_target_ip=root_ip,
        max_depth=args.max_depth,
        max_additional_targets=args.max_targets,
        allowed_subnet=args.subnet,
    )

    root_host = scan_host(
        target_ip=root_ip, ports=profile.ports, host_header=target,
        port_prober=container.port_prober, http_prober=container.http_prober,
        tls_prober=container.tls_prober, ssh_prober=container.ssh_prober,
        vnc_prober=container.vnc_prober, generic_prober=container.generic_prober,
        depth_level=0,
    )

    all_hosts: list[Host] = [root_host]
    queue: list[Host] = [root_host]
    additional_count = 0
    interactive = sys.stdin.isatty()

    while queue:
        current = queue.pop(0)
        if current.depth_level >= args.max_depth:
            continue

        proposed = discover_targets(
            host=current, discovery_prober=container.discovery_prober, root_ip=root_ip,
            allowed_subnet=args.subnet, current_additional_target_count=additional_count,
            max_additional_targets=args.max_targets,
        )
        if not proposed:
            continue

        decisions = _decide(proposed, current, auto_validate=args.auto_validate, interactive=interactive)
        validated = validate_targets(proposed, decisions)

        for candidate in validated:
            if candidate.state != DiscoveryState.ACCEPTED:
                continue
            try:
                child_ip = container.dns_resolver.resolve(candidate.host)
            except TargetResolutionError:
                continue  # acceptee mais non resolvable : ignoree, pas bloquant pour le reste

            child_host = scan_host(
                target_ip=child_ip, ports=profile.ports, host_header=candidate.host,
                port_prober=container.port_prober, http_prober=container.http_prober,
                tls_prober=container.tls_prober, ssh_prober=container.ssh_prober,
                vnc_prober=container.vnc_prober, generic_prober=container.generic_prober,
                depth_level=current.depth_level + 1, discovered_from=candidate.discovered_from,
                discovery_source=candidate.source, discovery_confidence=candidate.confidence,
            )
            all_hosts.append(child_host)
            queue.append(child_host)
            additional_count += 1

    scan.status = ScanStatus.COMPLETED
    scan.discovered_targets = [h.ip for h in all_hosts if h is not root_host]
    container.scan_repository.save(scan)
    assert scan.id is not None
    container.scan_repository.save_hosts(scan.id, all_hosts)

    graph = reconstruct_architecture(all_hosts)
    container.scan_repository.save_graph(scan.id, graph)

    return format_scan_result(scan, tuple(all_hosts), graph)


def _decide(
    proposed: list[DiscoveredTarget], parent: Host, *, auto_validate: bool, interactive: bool
) -> dict[str, bool]:
    """OMEGA-DEEP_SPECIFICATIONS.md §6.2 : `--auto-validate` accepte tout
    (avertissement deja affiche par l'appelant). Sans lui, en mode
    non-interactif (pas de TTY), ne rien scanner — la decouverte reste
    rapportee (les DiscoveredTarget existent, juste REJECTED faute de
    decision), mais aucun scan actif n'est lance sans validation
    explicite. En interactif, une question par cible."""
    if auto_validate:
        return {target.host: True for target in proposed}

    if not interactive:
        return {}

    decisions: dict[str, bool] = {}
    print(f"\n{len(proposed)} cible(s) decouverte(s) depuis {parent.ip} :", file=sys.stderr)
    for target in proposed:
        print(f"  {target.host} — source: {target.source}, confiance: {target.confidence.value}", file=sys.stderr)
        for evidence in target.evidence:
            print(f"    {evidence}", file=sys.stderr)
        answer = input(f"  Scanner {target.host} ? [o/N] ").strip().lower()
        decisions[target.host] = answer in ("o", "oui", "y", "yes")
    return decisions
