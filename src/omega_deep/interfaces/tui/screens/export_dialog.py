# Copyright (c) 2026 kraynux - Licence MIT
"""Dialogue d'export : format, theme (HTML uniquement), chemin de
destination. Porte depuis interfaces/tui/screens/export_dialog.py
d'omega-check (D-007/D-008/D-009 : memes 5 themes d'export Jinja2 que le
reste de la suite, y compris pour le diagramme HTML du graphe
d'architecture — voir infrastructure/exporters/html_exporter.py)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Select, Static

from omega_deep.application.commands.export_scan_report import export_scan_report
from omega_deep.application.queries.build_export_filename import build_export_filename
from omega_deep.application.queries.configured_directory import (
    EXPORTS_DIR_KEY,
    configured_directory,
)
from omega_deep.domain.scans.models import Scan
from omega_deep.shared.i18n import LANGUAGE, _, translating_as

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer

_FORMATS = (("JSON", "json"), (_("Texte"), "text"), ("HTML", "html"))


class ExportDialogScreen(ModalScreen[None]):
    """Retourne toujours None (pas de valeur a rapporter a l'appelant)."""

    def __init__(self, *, container: DependencyContainer, scan: Scan, active_theme: str) -> None:
        super().__init__()
        self._container = container
        self._scan = scan
        default_theme = active_theme if active_theme in EXPORT_PALETTES else DEFAULT_EXPORT_THEME
        self._default_theme = default_theme

    def compose(self) -> ComposeResult:
        with Vertical(classes="omega-modal"):
            yield Static(_("EXPORTER L'ANALYSE"), classes="omega-title")

            yield Static(_("Format"), classes="omega-subtitle")
            yield Select(list(_FORMATS), value="html", id="format-select")

            yield Static(_("Thème (HTML uniquement)"), classes="omega-subtitle")
            yield Select([(name, name) for name in EXPORT_PALETTES], value=self._default_theme, id="theme-select")

            yield Static(_("Destination"), classes="omega-subtitle")
            yield Input(value=self._default_path("html"), id="path-input")

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Exporter"), id="export", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Annuler"), id="cancel")

    def _default_path(self, fmt: str) -> str:
        filename = build_export_filename(self._scan, fmt)
        exports_dir = configured_directory(
            self._container.settings_store, EXPORTS_DIR_KEY, self._container.default_exports_dir
        )
        return str(exports_dir / filename)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "format-select":
            self.query_one("#path-input", Input).value = self._default_path(str(event.value))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
            return
        if event.button.id != "export":
            return

        fmt = str(self.query_one("#format-select", Select).value)
        theme_name = str(self.query_one("#theme-select", Select).value)
        path_str = self.query_one("#path-input", Input).value.strip()
        if not path_str:
            self.app.notify(_("Saisissez un chemin de destination."), severity="warning")
            return

        assert self._scan.id is not None
        # Lot N (Q5) : rapport ecrit dans la langue des exports (reglage ; dans la suite, le sien).
        with translating_as(LANGUAGE.export_state(self._container.settings_store)):
            content = export_scan_report(
                self._container.scan_repository, self._container.report_exporter, self._scan.id, fmt, theme_name
            )

        output_path = Path(path_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        self.app.notify(str(output_path), title=_("Export {fmt} terminé").format(fmt=fmt))
        self.dismiss()

