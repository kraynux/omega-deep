# Copyright (c) 2026 kraynux - Licence MIT
"""Cablage des adaptateurs concrets derriere les ports — consomme
uniquement par app/bootstrap.py (racine de composition) et par
interfaces/ (sous TYPE_CHECKING uniquement, jamais a l'execution).

Contient `discovery_prober`, absent d'omega-check (nouveau port DEEP,
Phase 3)."""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from omega_lib.shared.typing import IdFactory

from omega_deep.ports.discovery_prober import DiscoveryProber
from omega_deep.ports.dns_resolver import DnsResolver
from omega_deep.ports.generic_banner_prober import GenericBannerProber
from omega_deep.ports.http_prober import HttpProber
from omega_deep.ports.port_prober import PortProber
from omega_deep.ports.profile_repository import ProfileRepository
from omega_deep.ports.report_exporter import ReportExporter
from omega_deep.ports.scan_repository import ScanRepository
from omega_deep.ports.settings_store import SettingsStore
from omega_deep.ports.ssh_prober import SshProber
from omega_deep.ports.terminal_detector import TerminalDetector
from omega_deep.ports.tls_prober import TlsProber
from omega_deep.ports.vnc_prober import VncProber


@dataclass
class DependencyContainer:
    dns_resolver: DnsResolver
    port_prober: PortProber
    http_prober: HttpProber
    tls_prober: TlsProber
    ssh_prober: SshProber
    vnc_prober: VncProber
    generic_prober: GenericBannerProber
    discovery_prober: DiscoveryProber
    scan_repository: ScanRepository
    profile_repository: ProfileRepository
    report_exporter: ReportExporter
    settings_store: SettingsStore
    terminal_detector: TerminalDetector
    default_exports_dir: Path
    default_screenshots_dir: Path
    id_factory: IdFactory
    clock: Callable[[], datetime]
    connection: sqlite3.Connection

    def close(self) -> None:
        self.connection.close()
