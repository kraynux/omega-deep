# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de comparaison de deux analyses. Porte depuis omega-check
(D-007/D-008) — compare uniquement les hosts RACINE des deux scans
(application/queries/compare_scans.py, identique a omega-check :
comparer les graphes de cibles decouvertes serait une extension possible
mais non demandee, voir OMEGA-DEEP_SPECIFICATIONS.md §6.1)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Static

from omega_deep.application.queries.compare_scans import compare_scans
from omega_deep.interfaces.tui.screens._base import OmegaScreen
from omega_deep.shared.i18n import _

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


class CompareScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer, scan_id_a: str, scan_id_b: str) -> None:
        super().__init__()
        self._container = container
        self._scan_id_a = scan_id_a
        self._scan_id_b = scan_id_b

    def compose(self) -> ComposeResult:
        comparison = compare_scans(self._container.scan_repository, self._scan_id_a, self._scan_id_b)

        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("COMPARAISON D'ANALYSES"), classes="omega-title")
            yield Static(_("{id} -> {id2}").format(id=comparison.scan_a.id, id2=comparison.scan_b.id), classes="omega-subtitle")

            if comparison.ports_only_in_a:
                yield Static(_("Ports présents seulement dans {id} :").format(id=comparison.scan_a.id))
                yield Static(", ".join(str(p) for p in comparison.ports_only_in_a))

            if comparison.ports_only_in_b:
                yield Static(_("Ports présents seulement dans {id} :").format(id=comparison.scan_b.id))
                yield Static(", ".join(str(p) for p in comparison.ports_only_in_b))

            if comparison.state_changes:
                yield Static(_("Changements d'état :"), classes="omega-subtitle")
                for change in comparison.state_changes:
                    yield Static(_("  port {port_number} : {value} -> {value2}").format(port_number=change.port_number, value=change.state_a.value, value2=change.state_b.value))

            if not (comparison.ports_only_in_a or comparison.ports_only_in_b or comparison.state_changes):
                yield Static(_("Aucune différence détectée."))

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
