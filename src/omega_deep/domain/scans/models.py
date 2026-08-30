# Copyright (c) 2026 kraynux - Licence MIT
"""Bounded context 'scans' : l'agregat Scan, cycle de vie d'un scan.

Etend le Scan d'omega-check (champs de base identiques) avec les champs
multi-cibles de DEEP (OMEGA-DEEP_SPECIFICATIONS.md §2.2) : cible initiale
+ garde-fous de decouverte, pas encore les cibles decouvertes elles-memes
(domain/discovery/models.py::DiscoveredTarget, phase ulterieure) — DEEP
garde ici seulement leurs adresses une fois acceptees/scannees."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_deep.core.enums import AnalysisMode, ScanMode, ScanStatus


@dataclass
class Scan:
    id: str | None = None  # UUID (omega_lib.shared.ids.new_id), voir D-006
    created_at: str = ""
    target: str = ""
    target_ip: str = ""
    profile_name: str | None = None
    profile_origin: str | None = None
    ports_scanned: list[int] = field(default_factory=list)
    scan_mode: ScanMode = ScanMode.PROFILE
    status: ScanStatus = ScanStatus.RUNNING

    # Champs specifiques a DEEP (analyse multi-cibles)
    analysis_mode: AnalysisMode = AnalysisMode.FIXED
    root_target_ip: str = ""
    discovered_targets: list[str] = field(default_factory=list)
    max_depth: int = 3
    max_additional_targets: int = 10
    allowed_subnet: str | None = None
