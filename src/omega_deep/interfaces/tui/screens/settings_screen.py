# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Reglages : theme, profil de rendu, chemins d'export/captures,
purge de l'historique. Adapte du patron screens/settings_screen.py
d'omega-check (D-007/D-008) — pas de purge de "cibles" (DEEP n'a pas de
concept de cible epinglee, contrairement a CHECK)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_lib.terminal.models import RenderProfile
from omega_lib.theme.policies import TUI_THEMES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_deep.application.commands.clear_exports import clear_exports
from omega_deep.application.commands.clear_scan_history import clear_scan_history
from omega_deep.application.commands.clear_screenshots import clear_screenshots
from omega_deep.application.commands.select_render_profile import select_render_profile
from omega_deep.application.commands.select_theme import select_theme
from omega_deep.application.exceptions import UnknownThemeError
from omega_deep.interfaces.tui.screens._base import OmegaScreen
from omega_deep.interfaces.tui.screens.confirm import ConfirmScreen

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer

_AUTO = "auto"
_EXPORTS_DIR_KEY = "exports_dir_override"
_SCREENSHOTS_DIR_KEY = "screenshots_dir_override"


class SettingsScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        store = self._container.settings_store
        yield Header()
        with Vertical(classes="omega-form-panel"):
            yield Static("REGLAGES", classes="omega-title")

            yield Static("Theme", classes="omega-subtitle")
            yield Select([(name, name) for name in TUI_THEMES], value=self.app.theme, id="theme-select")

            yield Static("Profil de rendu (redemarrage requis)", classes="omega-subtitle")
            current_override = store.get("render_profile_override", "")
            yield Select(
                [("Automatique", _AUTO)] + [(p.value, p.value) for p in RenderProfile],
                value=current_override or _AUTO,
                id="render-profile-select",
            )

            yield Static("Export", classes="omega-subtitle")
            yield Input(
                value=store.get(_EXPORTS_DIR_KEY, str(self._container.default_exports_dir)) or "",
                id="exports-dir-input",
            )

            yield Static("Captures d'ecran", classes="omega-subtitle")
            yield Input(
                value=store.get(_SCREENSHOTS_DIR_KEY, str(self._container.default_screenshots_dir)) or "",
                id="screenshots-dir-input",
            )

            yield Static("Purge", classes="omega-subtitle")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Vider l'historique", id="clear-history", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Supprimer les exports", id="clear-exports", variant="error")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Supprimer les screenshots", id="clear-screenshots", variant="error")

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "theme-select":
            if str(event.value) == self.app.theme:
                return
            self._apply_theme(str(event.value))
        elif event.select.id == "render-profile-select":
            current_override = self._container.settings_store.get("render_profile_override", "") or _AUTO
            if str(event.value) == current_override:
                return
            self._apply_render_profile(str(event.value))

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "exports-dir-input":
            self._container.settings_store.set(_EXPORTS_DIR_KEY, event.value)
        elif event.input.id == "screenshots-dir-input":
            self._container.settings_store.set(_SCREENSHOTS_DIR_KEY, event.value)

    def _apply_theme(self, theme_name: str) -> None:
        try:
            select_theme(settings_store=self._container.settings_store, theme_name=theme_name)
        except UnknownThemeError as exc:
            self.app.notify(str(exc), severity="error")
            return
        self.app.theme = theme_name

    def _apply_render_profile(self, value: str) -> None:
        profile = None if value == _AUTO else RenderProfile(value)
        select_render_profile(settings_store=self._container.settings_store, render_profile=profile)
        self.app.notify("Applique au prochain demarrage.", title="Profil de rendu")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "clear-history":
            self.app.push_screen(
                ConfirmScreen(
                    title="VIDER L'HISTORIQUE ?",
                    message="Toutes les analyses persistees seront definitivement supprimees.",
                ),
                self._clear_history_if_confirmed,
            )
        elif event.button.id == "clear-exports":
            self.app.push_screen(
                ConfirmScreen(
                    title="SUPPRIMER LES EXPORTS ?",
                    message="Tous les fichiers du dossier d'export seront definitivement supprimes.",
                ),
                self._clear_exports_if_confirmed,
            )
        elif event.button.id == "clear-screenshots":
            self.app.push_screen(
                ConfirmScreen(
                    title="SUPPRIMER LES SCREENSHOTS ?",
                    message="Tous les fichiers du dossier de captures d'ecran seront definitivement supprimes.",
                ),
                self._clear_screenshots_if_confirmed,
            )

    def _clear_history_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        clear_scan_history(scan_repository=self._container.scan_repository)
        self.app.notify("Historique vide.")

    def _clear_exports_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        clear_exports(self._container.default_exports_dir)
        self.app.notify("Exports supprimes.")

    def _clear_screenshots_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        clear_screenshots(self._container.default_screenshots_dir)
        self.app.notify("Screenshots supprimes.")
