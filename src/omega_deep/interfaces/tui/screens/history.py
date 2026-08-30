# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Historique : liste des analyses passees, detail, comparaison,
relecture. Adapte du patron screens/history.py d'omega-check (D-007/D-008)
— `_push_details` recupere aussi les hosts (pluriel) et le graphe
(get_scan_details retourne un triplet cote DEEP, voir
application/queries/get_scan_details.py)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_deep.application.queries.get_scan_details import get_scan_details
from omega_deep.application.queries.get_scan_history import get_scan_history
from omega_deep.domain.scans.models import Scan
from omega_deep.interfaces.tui.screens._base import OmegaScreen
from omega_deep.interfaces.tui.screens.compare import CompareScreen
from omega_deep.interfaces.tui.widgets.history_table import HistoryTable

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


class HistoryScreen(OmegaScreen):
    """Une comparaison se fait en deux temps : marquer une ligne comme
    reference, puis comparer une autre ligne avec elle — pas de selection
    multiple native au DataTable de Textual."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_scan_id: str | None = None
        self._reference_scan_id: str | None = None
        self._scans_by_id: dict[str, Scan] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("HISTORIQUE", classes="omega-title")
            yield Input(placeholder="Filtrer par cible racine...", id="target-filter")
            yield HistoryTable(id="history-table")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir le detail", id="view")
                with Container(classes="omega-btn-frame"):
                    yield Button("Marquer comme reference", id="mark-reference")
                with Container(classes="omega-btn-frame"):
                    yield Button("Comparer avec la reference", id="compare")
                with Container(classes="omega-btn-frame"):
                    yield Button("Rejouer", id="replay")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh(None)

    def _refresh(self, target_filter: str | None) -> None:
        scans = get_scan_history(self._container.scan_repository, target=target_filter or None, limit=100)
        self._scans_by_id = {scan.id: scan for scan in scans if scan.id is not None}
        self.query_one(HistoryTable).set_scans(scans)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "target-filter":
            self._refresh(event.value.strip())

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._selected_scan_id = str(event.row_key.value)
        self._push_details(self._selected_scan_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if self._selected_scan_id is None:
            self.app.notify("Selectionnez d'abord une ligne.", severity="warning")
            return

        if event.button.id == "view":
            self._push_details(self._selected_scan_id)
        elif event.button.id == "mark-reference":
            self._reference_scan_id = self._selected_scan_id
            self.app.notify(f"Reference : {self._reference_scan_id}")
        elif event.button.id == "compare":
            if self._reference_scan_id is None:
                self.app.notify("Marquez d'abord une reference.", severity="warning")
                return
            self.app.push_screen(
                CompareScreen(
                    container=self._container,
                    scan_id_a=self._reference_scan_id,
                    scan_id_b=self._selected_scan_id,
                )
            )
        elif event.button.id == "replay":
            self._replay(self._selected_scan_id)

    def _push_details(self, scan_id: str) -> None:
        from omega_deep.interfaces.tui.screens.show_detail import ShowDetailScreen

        scan, hosts, graph = get_scan_details(self._container.scan_repository, scan_id)
        self.app.push_screen(ShowDetailScreen(container=self._container, scan=scan, hosts=hosts, graph=graph))

    def _replay(self, scan_id: str) -> None:
        from omega_deep.interfaces.tui.screens.scan_progress import AnalyzeProgressScreen

        scan = self._scans_by_id.get(scan_id)
        if scan is None or scan.profile_name is None:
            self.app.notify("Impossible de rejouer cette analyse (profil inconnu).", severity="error")
            return
        self.app.push_screen(
            AnalyzeProgressScreen(
                container=self._container,
                target=scan.target,
                profile_name=scan.profile_name,
                max_depth=scan.max_depth,
                max_additional_targets=scan.max_additional_targets,
                allowed_subnet=scan.allowed_subnet,
            )
        )
