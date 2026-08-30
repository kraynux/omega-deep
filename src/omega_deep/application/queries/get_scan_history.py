# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : recuperer la liste des scans precedents. Identique a
omega-check."""
from __future__ import annotations

from omega_deep.domain.scans.models import Scan
from omega_deep.ports.scan_repository import ScanRepository


def get_scan_history(
    repo: ScanRepository, *, target: str | None = None, limit: int = 50
) -> tuple[Scan, ...]:
    return repo.list_history(target=target, limit=limit)
