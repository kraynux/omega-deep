# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de progression : orchestre le flux d'analyse multi-cibles complet
(racine -> decouverte -> validation utilisateur -> cibles acceptees ->
reconstruction), sans bloquer l'UI. Equivalent TUI de
interfaces/cli/commands/analyze_command.py::handle_analyze — meme boucle
BFS, mais chaque lot de cibles proposees est valide via un ecran modal
(TargetValidationScreen, pousse avec `app.push_screen_wait(...)` pour
attendre la decision avant de reprendre la boucle) plutot que des prompts
`input()`. Pas de mode `--auto-validate` ici (CLI seulement, deconseille) :
le TUI rend la validation explicite et interactive par construction.

Le spinner indetermine (ProgressPanel) est complete par un relai des
lignes de journal emises par application/commands/scan_host.py (logger
'omega_deep.scan') vers le RichLog du panneau, meme mecanisme
qu'omega-check/screens/scan_progress.py — chaque appel bloquant (E/S
reseau, disque) passe par `asyncio.to_thread`, le connecteur SQLite est
ouvert avec `check_same_thread=False` (infrastructure/storage/sqlite/
connection.py) donc son usage a travers plusieurs appels `to_thread`
successifs (potentiellement des threads differents) est sans danger."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.screen import Screen

from omega_deep.application.commands.discover_targets import discover_targets
from omega_deep.application.commands.reconstruct_architecture import reconstruct_architecture
from omega_deep.application.commands.scan_host import scan_host
from omega_deep.application.commands.validate_targets import validate_targets
from omega_deep.application.exceptions import TargetResolutionError
from omega_deep.application.queries.list_profiles import get_profile
from omega_deep.core.enums import AnalysisMode, ScanMode, ScanStatus
from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.discovery.models import DiscoveredTarget, DiscoveryState
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host
from omega_deep.interfaces.tui.screens.show_detail import ShowDetailScreen
from omega_deep.interfaces.tui.screens.target_validation import TargetValidationScreen
from omega_deep.interfaces.tui.widgets.progress_panel import ProgressPanel

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


class _RelayHandler(logging.Handler):
    """Relaie chaque record du logger 'omega_deep.scan' vers un callback
    (voir _on_log_record ci-dessous) — pas de formattage, juste le message."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        self._callback(record.getMessage())


class AnalyzeProgressScreen(Screen[None]):
    """Ecran transitoire : disparait des que l'analyse se termine (succes
    -> ShowDetailScreen remplace cet ecran)."""

    def __init__(
        self,
        *,
        container: DependencyContainer,
        target: str,
        profile_name: str,
        max_depth: int = 3,
        max_additional_targets: int = 10,
        allowed_subnet: str | None = None,
    ) -> None:
        super().__init__()
        self._container = container
        self._target = target
        self._profile_name = profile_name
        self._max_depth = max_depth
        self._max_additional_targets = max_additional_targets
        self._allowed_subnet = allowed_subnet

    def compose(self) -> ComposeResult:
        yield ProgressPanel(message=f"Analyse de {self._target} en cours...")

    def on_mount(self) -> None:
        self.run_worker(self._run_analyze(), exclusive=True)

    async def _run_analyze(self) -> None:
        container = self._container
        logger = logging.getLogger("omega_deep.scan")
        handler = _RelayHandler(self._on_log_record)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            profile = await asyncio.to_thread(get_profile, container.profile_repository, self._profile_name)

            try:
                root_ip = await asyncio.to_thread(container.dns_resolver.resolve, self._target)
            except TargetResolutionError:
                failed_scan = Scan(
                    id=container.id_factory(),
                    created_at=container.clock().isoformat(),
                    target=self._target,
                    profile_name=profile.name,
                    profile_origin=profile.origin,
                    ports_scanned=list(profile.ports),
                    scan_mode=ScanMode.PROFILE,
                    status=ScanStatus.FAILED,
                    analysis_mode=AnalysisMode.DEEP,
                )
                await asyncio.to_thread(container.scan_repository.save, failed_scan)
                self.app.notify(
                    f"Resolution DNS impossible pour '{self._target}'.", title="Analyse echouee", severity="error"
                )
                self.dismiss()
                return

            scan = Scan(
                id=container.id_factory(),
                created_at=container.clock().isoformat(),
                target=self._target,
                target_ip=root_ip,
                profile_name=profile.name,
                profile_origin=profile.origin,
                ports_scanned=list(profile.ports),
                scan_mode=ScanMode.PROFILE,
                status=ScanStatus.RUNNING,
                analysis_mode=AnalysisMode.DEEP,
                root_target_ip=root_ip,
                max_depth=self._max_depth,
                max_additional_targets=self._max_additional_targets,
                allowed_subnet=self._allowed_subnet,
            )

            def _scan_root() -> Host:
                return scan_host(
                    target_ip=root_ip,
                    ports=profile.ports,
                    host_header=self._target,
                    port_prober=container.port_prober,
                    http_prober=container.http_prober,
                    tls_prober=container.tls_prober,
                    ssh_prober=container.ssh_prober,
                    vnc_prober=container.vnc_prober,
                    generic_prober=container.generic_prober,
                    depth_level=0,
                )

            root_host = await asyncio.to_thread(_scan_root)

            all_hosts: list[Host] = [root_host]
            queue: list[Host] = [root_host]
            additional_count = 0

            while queue:
                current = queue.pop(0)
                if current.depth_level >= self._max_depth:
                    continue

                def _discover(host: Host = current, count: int = additional_count) -> list[DiscoveredTarget]:
                    return discover_targets(
                        host=host,
                        discovery_prober=container.discovery_prober,
                        root_ip=root_ip,
                        allowed_subnet=self._allowed_subnet,
                        current_additional_target_count=count,
                        max_additional_targets=self._max_additional_targets,
                    )

                proposed = await asyncio.to_thread(_discover)
                if not proposed:
                    continue

                decisions = await self.app.push_screen_wait(
                    TargetValidationScreen(targets=proposed, parent_ip=current.ip)
                )
                validated = validate_targets(proposed, decisions)

                for candidate in validated:
                    if candidate.state != DiscoveryState.ACCEPTED:
                        continue
                    try:
                        child_ip = await asyncio.to_thread(container.dns_resolver.resolve, candidate.host)
                    except TargetResolutionError:
                        continue  # acceptee mais non resolvable : ignoree, pas bloquant pour le reste

                    def _scan_child(
                        parent: Host = current, target: DiscoveredTarget = candidate, target_ip: str = child_ip
                    ) -> Host:
                        return scan_host(
                            target_ip=target_ip,
                            ports=profile.ports,
                            host_header=target.host,
                            port_prober=container.port_prober,
                            http_prober=container.http_prober,
                            tls_prober=container.tls_prober,
                            ssh_prober=container.ssh_prober,
                            vnc_prober=container.vnc_prober,
                            generic_prober=container.generic_prober,
                            depth_level=parent.depth_level + 1,
                            discovered_from=target.discovered_from,
                            discovery_source=target.source,
                            discovery_confidence=target.confidence,
                        )

                    child_host = await asyncio.to_thread(_scan_child)
                    all_hosts.append(child_host)
                    queue.append(child_host)
                    additional_count += 1

            scan.status = ScanStatus.COMPLETED
            scan.discovered_targets = [h.ip for h in all_hosts if h is not root_host]

            def _persist() -> ArchitectureGraph:
                container.scan_repository.save(scan)
                assert scan.id is not None
                container.scan_repository.save_hosts(scan.id, all_hosts)
                graph = reconstruct_architecture(all_hosts)
                container.scan_repository.save_graph(scan.id, graph)
                return graph

            graph = await asyncio.to_thread(_persist)
        finally:
            logger.removeHandler(handler)

        self.app.switch_screen(
            ShowDetailScreen(container=container, scan=scan, hosts=tuple(all_hosts), graph=graph)
        )

    def _on_log_record(self, message: str) -> None:
        self.app.call_from_thread(self._write_log_line, message)

    def _write_log_line(self, message: str) -> None:
        if self.is_mounted:
            self.query_one(ProgressPanel).write_line(message)
