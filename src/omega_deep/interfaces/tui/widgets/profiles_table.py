# Copyright (c) 2026 kraynux - Licence MIT
"""Tableau des profils utilisateur (ecran Profils, backend deja existant
avant ce round : application/commands/{create,update,delete}_profile.py
n'etaient jusqu'ici cables a aucun ecran)."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_deep.domain.profiles.models import Profile
from omega_deep.shared.i18n import _


class ProfilesTable(DataTable[str]):
    """Une ligne par profil utilisateur (les profils systeme ne sont pas
    listes ici : lecture seule, deja visibles dans l'ecran Scanner)."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns(_("Nom"), _("Description"), _("Ports"))

    def set_profiles(self, profiles: list[Profile]) -> None:
        self.clear()
        for profile in sorted(profiles, key=lambda p: p.name):
            ports_str = ", ".join(str(p) for p in profile.ports)
            self.add_row(profile.name, _(profile.description), ports_str, key=profile.name)
