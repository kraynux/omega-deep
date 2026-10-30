# Copyright (c) 2026 kraynux - Licence MIT
"""Tableau de l'historique des analyses (adapte du patron omega-check,
D-007/D-008) — colonne "Cibles" en plus (nombre de cibles decouvertes et
acceptees, `len(scan.discovered_targets)`), specifique a l'analyse
multi-cibles de DEEP."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_deep.domain.scans.models import Scan
from omega_deep.shared.i18n import _


class HistoryTable(DataTable[str]):
    """Une ligne par analyse passee, la plus recente en premier."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns(_("Cible racine"), _("Date"), _("Profil"), _("Cibles"), _("Statut"))

    def set_scans(self, scans: tuple[Scan, ...]) -> None:
        self.clear()
        for scan in scans:
            assert scan.id is not None
            self.add_row(
                f"{scan.target} ({scan.target_ip})" if scan.target_ip else scan.target,
                scan.created_at,
                scan.profile_name or "-",
                str(len(scan.discovered_targets)),
                scan.status.value,
                key=scan.id,
            )
