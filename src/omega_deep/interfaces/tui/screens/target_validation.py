# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran modal de validation des cibles decouvertes (D-003 : PROPOSED ->
PRESENTED -> ACCEPTED/REJECTED, une decision explicite par cible, jamais
de silence-vaut-acceptation). NOUVEAU pour DEEP, remplace les prompts
`input()` de interfaces/cli/commands/analyze_command.py::_decide.

Pousse par screens/scan_progress.py::AnalyzeProgressScreen via
`app.push_screen_wait(...)` (attend le dismiss() avant de reprendre la
boucle de decouverte) — retourne un `dict[str, bool]` (host -> accepte),
directement consommable par application/commands/validate_targets.py.
`action_back`/fermeture sans "Valider" renvoie un dict VIDE : toute cible
non explicitement decidee est alors traitee comme refusee par
validate_targets (regle fail-safe, meme comportement qu'une interruption
CLI)."""
from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

from omega_deep.domain.discovery.models import DiscoveredTarget
from omega_deep.interfaces.tui.widgets.discovery_table import DiscoveryTable


class TargetValidationScreen(ModalScreen[dict[str, bool]]):
    BINDINGS: ClassVar[list[BindingType]] = [Binding("escape", "back", "Tout rejeter", show=True)]

    def __init__(self, *, targets: list[DiscoveredTarget], parent_ip: str) -> None:
        super().__init__()
        self._targets = targets
        self._parent_ip = parent_ip
        self._decisions: dict[str, bool] = {target.host: False for target in targets}

    def compose(self) -> ComposeResult:
        with Vertical(classes="omega-modal"):
            yield Static("CIBLES DECOUVERTES", classes="omega-title")
            yield Static(
                f"{len(self._targets)} cible(s) decouverte(s) depuis {self._parent_ip}. "
                "Aucune n'est scannee sans acceptation explicite.",
                classes="omega-subtitle",
            )
            yield DiscoveryTable(id="discovery-table")
            with VerticalScroll(id="evidence-panel"):
                yield Static("", id="evidence-detail", classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Basculer", id="toggle")
                with Container(classes="omega-btn-frame"):
                    yield Button("Tout accepter", id="accept-all")
                with Container(classes="omega-btn-frame"):
                    yield Button("Tout rejeter", id="reject-all")
                with Container(classes="omega-btn-frame"):
                    yield Button("Valider", id="submit", variant="primary")

    def on_mount(self) -> None:
        self.query_one(DiscoveryTable).set_targets(self._targets, self._decisions)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        host = str(event.row_key.value)
        target = next((t for t in self._targets if t.host == host), None)
        detail = self.query_one("#evidence-detail", Static)
        if target is None or not target.evidence:
            detail.update("(aucune preuve associee)")
            return
        detail.update("\n".join(f"- {line}" for line in target.evidence))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        table = self.query_one(DiscoveryTable)
        if event.button.id == "toggle":
            self._toggle_current(table)
        elif event.button.id == "accept-all":
            self._set_all(table, True)
        elif event.button.id == "reject-all":
            self._set_all(table, False)
        elif event.button.id == "submit":
            self.dismiss(dict(self._decisions))

    def _toggle_current(self, table: DiscoveryTable) -> None:
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        host = str(row_key.value)
        accepted = not self._decisions.get(host, False)
        self._decisions[host] = accepted
        table.refresh_decision(host, accepted)

    def _set_all(self, table: DiscoveryTable, accepted: bool) -> None:
        for target in self._targets:
            self._decisions[target.host] = accepted
            table.refresh_decision(target.host, accepted)

    def action_back(self) -> None:
        self.dismiss({})
