# Copyright (c) 2026 kraynux - Licence MIT
"""Erreurs du bounded context 'scans'. Identique a omega-check."""
from __future__ import annotations

from omega_deep.domain.errors import DomainError
from omega_deep.shared.i18n import _


class ScanNotFoundError(DomainError):
    def __init__(self, scan_id: str) -> None:
        super().__init__(_("Scan introuvable : '{scan_id}'").format(scan_id=scan_id))
        self.scan_id = scan_id
