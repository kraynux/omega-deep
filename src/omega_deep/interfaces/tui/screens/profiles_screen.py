# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Profils : creer/modifier/supprimer des profils de ports
personnels, utilises via le profil CUSTOM de scan_setup.py. Backend
identique a omega-check (domain/profiles/ copie verbatim, D-005) — cable
des la premiere version de ce TUI, contrairement a CHECK ou l'ecran avait
ete ajoute apres coup (voir OMEGA-DEEP_PLAN_DEV.md, phase TUI)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_deep.application.commands.create_profile import (
    ProfileAlreadyExistsError,
    create_profile,
)
from omega_deep.application.commands.delete_profile import delete_profile
from omega_deep.application.commands.update_profile import update_profile
from omega_deep.domain.profiles.exceptions import (
    DomainError as ProfileDomainError,
)
from omega_deep.domain.profiles.exceptions import (
    DuplicatePortsError,
    InvalidPortError,
    ProfileNotFoundError,
)
from omega_deep.domain.profiles.policies import parse_port_spec
from omega_deep.interfaces.tui.screens._base import OmegaScreen
from omega_deep.interfaces.tui.screens.confirm import ConfirmScreen
from omega_deep.interfaces.tui.widgets.profiles_table import ProfilesTable

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


class ProfilesScreen(OmegaScreen):
    """Creer/modifier/supprimer des profils de ports personnels."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_name: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("PROFILS", classes="omega-title")
            yield ProfilesTable(id="profiles-table")
            yield Input(placeholder="Nom", id="name-input")
            yield Input(placeholder="Description", id="description-input")
            yield Input(placeholder="Ports : ex. 80  /  22,443,8080  /  1000-2000", id="ports-input")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Creer", id="create", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Modifier", id="update")
                with Container(classes="omega-btn-frame"):
                    yield Button("Supprimer", id="delete", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        repo = self._container.profile_repository
        profiles = list(repo.load_user_profiles().values())
        self.query_one(ProfilesTable).set_profiles(profiles)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        name = str(event.row_key.value)
        self._selected_name = name
        profile = self._container.profile_repository.load_user_profiles().get(name)
        if profile is None:
            return
        self.query_one("#name-input", Input).value = profile.name
        self.query_one("#description-input", Input).value = profile.description
        self.query_one("#ports-input", Input).value = ", ".join(str(p) for p in profile.ports)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "create":
            self._create()
        elif event.button.id == "update":
            self._update()
        elif event.button.id == "delete":
            self._delete()

    def _read_ports(self) -> list[int] | None:
        raw = self.query_one("#ports-input", Input).value.strip()
        if not raw:
            self.app.notify("Saisissez au moins un port.", severity="warning")
            return None
        try:
            return parse_port_spec(raw)
        except (ValueError, InvalidPortError, DuplicatePortsError) as exc:
            self.app.notify(f"Ports invalides : {exc}", severity="warning")
            return None

    def _create(self) -> None:
        name = self.query_one("#name-input", Input).value.strip()
        description = self.query_one("#description-input", Input).value.strip()
        if not name:
            self.app.notify("Saisissez un nom.", severity="warning")
            return
        ports = self._read_ports()
        if ports is None:
            return

        try:
            create_profile(self._container.profile_repository, name, description, ports)
        except (ProfileAlreadyExistsError, ProfileDomainError) as exc:
            self.app.notify(str(exc), severity="error")
            return
        self._refresh()

    def _update(self) -> None:
        if self._selected_name is None:
            self.app.notify("Selectionnez d'abord un profil.", severity="warning")
            return
        description = self.query_one("#description-input", Input).value.strip()
        ports = self._read_ports()
        if ports is None:
            return

        try:
            update_profile(self._container.profile_repository, self._selected_name, description, ports)
        except ProfileNotFoundError as exc:
            self.app.notify(str(exc), severity="error")
            return
        self._refresh()

    def _delete(self) -> None:
        if self._selected_name is None:
            self.app.notify("Selectionnez d'abord un profil.", severity="warning")
            return
        name = self._selected_name

        def _delete_if_confirmed(confirmed: bool | None) -> None:
            if not confirmed:
                return
            try:
                delete_profile(self._container.profile_repository, name)
            except ProfileNotFoundError as exc:
                self.app.notify(str(exc), severity="error")
                return
            self._selected_name = None
            self._refresh()

        self.app.push_screen(
            ConfirmScreen(title="SUPPRIMER LE PROFIL ?", message=f"Le profil '{name}' sera definitivement supprime."),
            _delete_if_confirmed,
        )
