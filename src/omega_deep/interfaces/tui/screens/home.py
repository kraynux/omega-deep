# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran d'accueil : menu principal vers les autres ecrans. Adapte du
patron screens/home.py d'omega-check (D-007/D-008) — pas d'entree
"Cibles" (DEEP n'a pas de concept de cible epinglee), "Scanner" devient
"Analyser" (analyse multi-cibles, pas un scan fixe)."""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from omega_deep.interfaces.tui.screens.help_screen import HelpScreen
from omega_deep.interfaces.tui.screens.history import HistoryScreen
from omega_deep.interfaces.tui.screens.profiles_screen import ProfilesScreen
from omega_deep.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_deep.interfaces.tui.screens.scan_setup import ScanSetupScreen
from omega_deep.interfaces.tui.screens.settings_screen import SettingsScreen
from omega_deep.interfaces.tui.widgets.home_wordmark import HomeWordmark
from omega_deep.shared.i18n import _

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer

_MENU_ITEMS: tuple[tuple[str, str], ...] = (
    ("scan", _("Analyser")),
    ("profiles", _("Profils")),
    ("history", _("Historique")),
    ("settings", _("Réglages")),
    ("help", _("Aide")),
    ("quit", _("Quitter")),
)


class HomeScreen(Screen[None]):
    """Menu principal, racine de la pile de navigation. N'herite pas de
    OmegaScreen : `echap` ici demande confirmation de sortie, pas un
    dismiss() (rien "en dessous" de cet ecran)."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "back", _("Retour"), show=True),
        Binding("up", "focus_previous_item", _("Monter"), show=False),
        Binding("down", "focus_next_item", _("Descendre"), show=False),
    ]

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-home-root"):
            with Center():
                yield HomeWordmark()
            with Center():
                with Vertical(classes="omega-home-menu") as menu:
                    for item_id, label in _MENU_ITEMS:
                        with Container(classes="omega-btn-frame"):
                            yield Button(label.upper(), id=item_id)
                menu.border_title = _("MENU PRINCIPAL")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "help":
            self.app.push_screen(HelpScreen())
            return
        if event.button.id == "quit":
            self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)
            return
        screen = self._screen_for(event.button.id)
        if screen is not None:
            self.app.push_screen(screen)

    def action_back(self) -> None:
        self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def action_focus_previous_item(self) -> None:
        self.focus_previous()

    def action_focus_next_item(self) -> None:
        self.focus_next()

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.app.exit()

    def _screen_for(self, item_id: str | None) -> Screen[None] | None:
        if item_id == "scan":
            return ScanSetupScreen(container=self._container)
        if item_id == "profiles":
            return ProfilesScreen(container=self._container)
        if item_id == "history":
            return HistoryScreen(container=self._container)
        if item_id == "settings":
            return SettingsScreen(container=self._container)
        return None
