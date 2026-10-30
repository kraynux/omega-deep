# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : scanner les ports d'UNE IP deja resolue et identifier les
services (extrait de run_scan.py — voir sa docstring pour le raisonnement
de decoupage). Ne cree ni ne sauvegarde aucun Scan : c'est la brique
reutilisee a la fois par run_scan() (scan FIXED, un seul host) et par
l'orchestration multi-host d'une analyse DEEP (interfaces/cli/commands/
analyze_command.py, qui gere elle-meme UN SEUL Scan pour toute
l'analyse — racine + cibles acceptees, voir ports/scan_repository.py::
save_hosts pour le raisonnement "un scan_id, plusieurs hosts")."""
from __future__ import annotations

import logging

from omega_deep.application.commands.probe_service import probe_service
from omega_deep.core.enums import ConfidenceLevel, PortState
from omega_deep.domain.services.models import Port
from omega_deep.domain.targets.models import Host
from omega_deep.ports.generic_banner_prober import GenericBannerProber
from omega_deep.ports.http_prober import HttpProber
from omega_deep.ports.port_prober import PortProber
from omega_deep.ports.ssh_prober import SshProber
from omega_deep.ports.tls_prober import TlsProber
from omega_deep.ports.vnc_prober import VncProber
from omega_deep.shared.i18n import N_

_logger = logging.getLogger("omega_deep.scan")


def scan_host(
    *,
    target_ip: str,
    ports: list[int],
    host_header: str,
    port_prober: PortProber,
    http_prober: HttpProber,
    tls_prober: TlsProber,
    ssh_prober: SshProber,
    vnc_prober: VncProber,
    generic_prober: GenericBannerProber,
    protocol: str = "tcp",
    timeout: float = 1.0,
    retries: int = 1,
    depth_level: int = 0,
    discovered_from: str | None = None,
    discovery_source: str | None = None,
    discovery_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN,
) -> Host:
    probed_ports: list[Port] = []
    for port in ports:
        _logger.info(N_("Scan du port %s/%s..."), port, protocol)
        probed_port = port_prober.probe(target_ip, port, protocol, timeout, retries)
        probed_ports.append(probed_port)
        _logger.info(N_("Port %s/%s : %s"), port, protocol, probed_port.state.value)

        if probed_port.state == PortState.OPEN:
            _logger.info(N_("Identification du service sur le port %s..."), port)
            probed_port.service = probe_service(
                target_ip=target_ip,
                port=probed_port.port_number,
                host_header=host_header,
                http_prober=http_prober,
                tls_prober=tls_prober,
                ssh_prober=ssh_prober,
                vnc_prober=vnc_prober,
                generic_prober=generic_prober,
                timeout=timeout,
            )

    _logger.info(N_("Host %s : %d port(s) analysé(s)."), target_ip, len(probed_ports))
    return Host(
        ip=target_ip,
        ports=probed_ports,
        depth_level=depth_level,
        discovered_from=discovered_from,
        discovery_source=discovery_source,
        discovery_confidence=discovery_confidence,
    )
