# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'export de rapport (OMEGA-DEEP_SPECIFICATIONS.md §9).

Difference cle avec le port d'omega-check : prend `hosts: tuple[Host, ...]`
(pluriel — un scan DEEP a potentiellement plusieurs hosts) et
`graph: ArchitectureGraph | None` (absent/None pour un scan FIXED ou un
scan echoue). Trois formats en un seul port (les consommateurs choisissent
le format a l'execution, pas au moment de l'injection de dependance)."""
from __future__ import annotations

from typing import Protocol

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host


class ReportExporter(Protocol):
    """Implemente par infrastructure/exporters/exporter.py."""

    def export_json(self, scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None) -> str: ...

    def export_text(self, scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None) -> str: ...

    def export_html(
        self, scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None, theme_name: str
    ) -> str: ...
