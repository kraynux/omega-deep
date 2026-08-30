# Copyright (c) 2026 kraynux - Licence MIT
"""Comparaison pure de deux scans (`compare_scans`). Se limite au
changement d'etat des ports (open/closed/filtered) : le diff au niveau
service (logiciel/version) est un raffinement possible plus tard.
Identique a omega-check."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_deep.core.enums import PortState
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host


@dataclass
class PortStateChange:
    port_number: int
    state_a: PortState
    state_b: PortState


@dataclass
class ScanComparison:
    scan_a: Scan
    scan_b: Scan
    ports_only_in_a: list[int] = field(default_factory=list)
    ports_only_in_b: list[int] = field(default_factory=list)
    state_changes: list[PortStateChange] = field(default_factory=list)


def compare_hosts(scan_a: Scan, host_a: Host | None, scan_b: Scan, host_b: Host | None) -> ScanComparison:
    ports_a = {p.port_number: p for p in (host_a.ports if host_a else [])}
    ports_b = {p.port_number: p for p in (host_b.ports if host_b else [])}

    common = sorted(set(ports_a) & set(ports_b))
    changes = [
        PortStateChange(port_number=num, state_a=ports_a[num].state, state_b=ports_b[num].state)
        for num in common
        if ports_a[num].state != ports_b[num].state
    ]

    return ScanComparison(
        scan_a=scan_a,
        scan_b=scan_b,
        ports_only_in_a=sorted(set(ports_a) - set(ports_b)),
        ports_only_in_b=sorted(set(ports_b) - set(ports_a)),
        state_changes=changes,
    )
