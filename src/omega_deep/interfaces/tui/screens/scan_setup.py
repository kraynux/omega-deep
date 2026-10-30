# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de saisie : cible racine, profil de ports, garde-fous de
decouverte. Adapte du patron screens/scan_setup.py d'omega-check
(D-007/D-008) — deux divergences :

- pas de picker de cibles epinglees (DEEP n'a pas ce concept) ;
- pas de flux CUSTOM a saisie libre de ports : contrairement a
  omega-check/run_scan.py (qui accepte une liste de ports ad-hoc),
  interfaces/cli/commands/analyze_command.py (et donc
  screens/scan_progress.py::AnalyzeProgressScreen) ne connaissent qu'un
  profil par NOM (`get_profile`), necessaire pour pouvoir rejouer une
  analyse depuis l'historique a l'identique (screens/history.py::_replay
  ne stocke que `scan.profile_name`). Le Select "Profil" liste donc les
  profils systeme ET les profils personnels deja enregistres (ecran
  Profils) indifferemment — un profil ad-hoc doit d'abord y etre cree.

Trois champs en plus specifiques a l'analyse multi-cibles
(OMEGA-DEEP_SPECIFICATIONS.md §6.2/§8) : profondeur max de decouverte,
nombre max de cibles supplementaires, sous-reseau autorise. Pas de toggle
"--auto-validate" ici (CLI seulement, deconseille avec avertissement) :
le TUI rend chaque cible decouverte a valider via un ecran modal (voir
screens/target_validation.py), pas de raccourci "tout accepter" au
lancement."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_deep.application.queries.list_profiles import get_profile, list_profiles
from omega_deep.domain.profiles.defaults import SYSTEM_PROFILES
from omega_deep.interfaces.tui.screens._base import OmegaScreen
from omega_deep.interfaces.tui.screens.confirm import ConfirmScreen
from omega_deep.interfaces.tui.screens.scan_progress import AnalyzeProgressScreen
from omega_deep.shared.i18n import _

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer

_DEFAULT_MAX_DEPTH = "3"
_DEFAULT_MAX_TARGETS = "10"


class ScanSetupScreen(OmegaScreen):
    """Formulaire de lancement d'une analyse."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        system_names = (*sorted(SYSTEM_PROFILES), "complet")
        custom_names = sorted(
            name for name, p in list_profiles(self._container.profile_repository).items() if p.origin == "user"
        )

        yield Header()
        with Vertical(classes="omega-form-panel"):
            yield Static(_("ANALYSER UNE CIBLE"), classes="omega-title")

            yield Static(_("Cible racine"), classes="omega-subtitle")
            yield Input(placeholder=_("ex. 192.168.1.10, example.org"), id="target-input")

            yield Static(_("Profil"), classes="omega-subtitle")
            yield Select(
                [(name, name) for name in system_names]
                + [(_("* {name}").format(name=name), name) for name in custom_names],
                value="minimal",
                id="profile-select",
            )

            yield Static(_("Garde-fous de découverte"), classes="omega-subtitle")
            yield Input(value=_DEFAULT_MAX_DEPTH, placeholder=_("Profondeur max"), id="max-depth-input")
            yield Input(
                value=_DEFAULT_MAX_TARGETS, placeholder=_("Nombre max de cibles supplémentaires"), id="max-targets-input"
            )
            yield Input(placeholder=_("Sous-réseau autorisé (ex. 192.168.1.0/24, facultatif)"), id="subnet-input")

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Lancer"), id="launch", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")

            yield Static("", id="profile-detail", classes="omega-hint")
        yield Footer()

    def on_mount(self) -> None:
        self._update_profile_detail("minimal")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "profile-select":
            self._update_profile_detail(str(event.value))

    def _update_profile_detail(self, profile_name: str) -> None:
        detail = self.query_one("#profile-detail", Static)
        profile = get_profile(self._container.profile_repository, profile_name)
        ports_str = ", ".join(str(p) for p in profile.ports)
        detail.update(_("{description}\nPorts ({count}) : {ports_str}").format(description=_(profile.description), count=len(profile.ports), ports_str=ports_str))

    def _read_guardrails(self) -> tuple[int, int, str | None] | None:
        try:
            max_depth = int(self.query_one("#max-depth-input", Input).value.strip() or _DEFAULT_MAX_DEPTH)
            max_targets = int(self.query_one("#max-targets-input", Input).value.strip() or _DEFAULT_MAX_TARGETS)
        except ValueError:
            self.app.notify(_("Profondeur/nombre de cibles : entiers attendus."), severity="warning")
            return None
        if max_depth < 1 or max_targets < 0:
            self.app.notify(_("Profondeur >= 1 et nombre de cibles >= 0 attendus."), severity="warning")
            return None
        subnet = self.query_one("#subnet-input", Input).value.strip() or None
        return max_depth, max_targets, subnet

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id != "launch":
            return

        target = self.query_one("#target-input", Input).value.strip()
        if not target:
            self.app.notify(_("Saisissez une cible."), severity="warning")
            return

        guardrails = self._read_guardrails()
        if guardrails is None:
            return
        max_depth, max_targets, subnet = guardrails
        profile_name = str(self.query_one("#profile-select", Select).value)

        if profile_name == "complet":
            self.app.push_screen(
                ConfirmScreen(
                    title=_("PROFIL COMPLET"),
                    message=_("Ce profil est exhaustif (union de tous les profils système) : "
                              "l'analyse peut être longue. Continuer ?"),
                ),
                lambda confirmed: self._launch_if_confirmed(
                    confirmed, target, profile_name, max_depth, max_targets, subnet
                ),
            )
            return

        self._launch(
            target=target, profile_name=profile_name, max_depth=max_depth, max_targets=max_targets, subnet=subnet
        )

    def _launch_if_confirmed(
        self,
        confirmed: bool | None,
        target: str,
        profile_name: str,
        max_depth: int,
        max_targets: int,
        subnet: str | None,
    ) -> None:
        if confirmed:
            self._launch(
                target=target, profile_name=profile_name, max_depth=max_depth, max_targets=max_targets, subnet=subnet
            )

    def _launch(
        self, *, target: str, profile_name: str, max_depth: int, max_targets: int, subnet: str | None
    ) -> None:
        self.app.push_screen(
            AnalyzeProgressScreen(
                container=self._container,
                target=target,
                profile_name=profile_name,
                max_depth=max_depth,
                max_additional_targets=max_targets,
                allowed_subnet=subnet,
            )
        )
