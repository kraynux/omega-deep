# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : lancer un scan sur une cible unique (resolution DNS incluse),
cree et persiste son propre Scan. Fine enveloppe autour de scan_host.py
(resolution DNS + creation/sauvegarde du Scan seulement — le detail du
scan de ports/services est dans scan_host.py, partage avec l'orchestration
multi-host de DEEP).

Reste utile tel quel pour un scan FIXED simple (une cible, pas de
decouverte) ; l'analyse DEEP complete (racine -> decouverte -> validation
-> cibles acceptees -> reconstruction) est orchestree par
interfaces/cli/commands/analyze_command.py, qui appelle scan_host()
directement pour chaque host afin que TOUTE l'analyse partage un seul
scan_id (voir ports/scan_repository.py::save_hosts)."""
from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime

from omega_lib.shared.typing import IdFactory

from omega_deep.application.commands.scan_host import scan_host
from omega_deep.application.exceptions import TargetResolutionError
from omega_deep.core.enums import AnalysisMode, ConfidenceLevel, ScanMode, ScanStatus
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host
from omega_deep.domain.targets.validation import normalize_target_input
from omega_deep.ports.dns_resolver import DnsResolver
from omega_deep.ports.generic_banner_prober import GenericBannerProber
from omega_deep.ports.http_prober import HttpProber
from omega_deep.ports.port_prober import PortProber
from omega_deep.ports.scan_repository import ScanRepository
from omega_deep.ports.ssh_prober import SshProber
from omega_deep.ports.tls_prober import TlsProber
from omega_deep.ports.vnc_prober import VncProber
from omega_deep.shared.i18n import N_

_logger = logging.getLogger("omega_deep.scan")


def run_scan(
    *,
    target: str,
    ports: list[int],
    scan_mode: ScanMode,
    dns_resolver: DnsResolver,
    port_prober: PortProber,
    scan_repository: ScanRepository,
    http_prober: HttpProber,
    tls_prober: TlsProber,
    ssh_prober: SshProber,
    vnc_prober: VncProber,
    generic_prober: GenericBannerProber,
    id_factory: IdFactory,
    now: Callable[[], datetime],
    profile_name: str | None = None,
    profile_origin: str | None = None,
    protocol: str = "tcp",
    timeout: float = 1.0,
    retries: int = 1,
    analysis_mode: AnalysisMode = AnalysisMode.FIXED,
    root_target_ip: str = "",
    max_depth: int = 3,
    max_additional_targets: int = 10,
    allowed_subnet: str | None = None,
    depth_level: int = 0,
    discovered_from: str | None = None,
    discovery_source: str | None = None,
    discovery_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN,
) -> tuple[Scan, Host | None]:
    target = normalize_target_input(target)
    scan = Scan(
        id=id_factory(),
        created_at=now().isoformat(),
        target=target,
        target_ip="",
        profile_name=profile_name,
        profile_origin=profile_origin,
        ports_scanned=list(ports),
        scan_mode=scan_mode,
        status=ScanStatus.RUNNING,
        analysis_mode=analysis_mode,
        root_target_ip=root_target_ip,
        max_depth=max_depth,
        max_additional_targets=max_additional_targets,
        allowed_subnet=allowed_subnet,
    )

    _logger.info(N_("Résolution DNS de %r..."), target)
    try:
        target_ip = dns_resolver.resolve(target)
    except TargetResolutionError as exc:
        _logger.error(N_("Résolution DNS échouée pour %r : %s"), target, exc.reason or exc)
        scan.status = ScanStatus.FAILED
        scan_repository.save(scan)
        return scan, None

    _logger.info(N_("Cible résolue : %s -> %s"), target, target_ip)
    scan.target_ip = target_ip
    if not scan.root_target_ip:
        scan.root_target_ip = target_ip

    host = scan_host(
        target_ip=target_ip,
        ports=ports,
        host_header=target,
        port_prober=port_prober,
        http_prober=http_prober,
        tls_prober=tls_prober,
        ssh_prober=ssh_prober,
        vnc_prober=vnc_prober,
        generic_prober=generic_prober,
        protocol=protocol,
        timeout=timeout,
        retries=retries,
        depth_level=depth_level,
        discovered_from=discovered_from,
        discovery_source=discovery_source,
        discovery_confidence=discovery_confidence,
    )

    scan.status = ScanStatus.COMPLETED
    scan_repository.save(scan)
    assert scan.id is not None  # toujours fixe par id_factory() ci-dessus, jamais None en pratique
    scan_repository.save_hosts(scan.id, [host])
    return scan, host
