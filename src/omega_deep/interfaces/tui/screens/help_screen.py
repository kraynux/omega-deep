# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Aide : reference statique des raccourcis et fonctions de l'application.
Adapte du patron screens/help_screen.py d'omega-check (D-007/D-008) — memes
raccourcis, contenu propre a DEEP pour les sections/profils (analyse
multi-cibles avec decouverte, pas un scan fixe unique)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_deep.domain.profiles.defaults import SYSTEM_PROFILES
from omega_deep.interfaces.tui.screens._base import OmegaScreen
from omega_deep.shared.i18n import _

_SHORTCUTS = (
    (_("Haut / Bas"), _("Naviguer entre les éléments d'un écran")),
    (_("Tab / Maj+Tab"), _("Naviguer entre les champs d'un formulaire")),
    (_("Échap"), _("Retour à l'écran précédent (confirmation de sortie sur l'accueil)")),
    ("t", _("Thème suivant (appliqué immédiatement, sans confirmation)")),
    ("r", _("Rafraîchir la détection du terminal")),
    ("a", _("Cette aide")),
    ("q", _("Quitter (avec confirmation)")),
)

_SECTIONS = (
    (
        _("Analyser"),
        (
            _("Saisir une cible racine (IP ou hostname), un profil de ports et les garde-fous "
              "de découverte (profondeur max, nombre de cibles supplémentaires, sous-réseau "
              "autorisé), puis lancer l'analyse. Chaque cible découverte est présentée pour "
              "validation avant tout scan (aucune cible n'est jamais scannée automatiquement).")
        ),
    ),
    (
        _("Historique"),
        (
            _("Liste toutes les analyses passées : détail complet (hosts + graphe "
              "d'architecture), comparaison entre deux analyses, ou rejouer une analyse sur la "
              "même cible racine.")
        ),
    ),
    (
        _("Export"),
        (
            _("Depuis le détail d'une analyse : JSON (structure complète), texte (rapport "
              "compact) ou HTML (rapport visuel avec diagramme du graphe d'architecture, thème "
              "d'export indépendant du thème de l'interface).")
        ),
    ),
)

_SCOPE_NOTICE = (
    _("Omega-deep découvre et cartographie l'architecture autour d'une cible racine (analyse "
      "multi-cibles) : chaque cible découverte (lien HTTP, service annoncé) est proposée à "
      "l'utilisateur — jamais scannée sans validation explicite (fail-safe : tout ce qui n'est "
      "pas confirmé est rejeté). Les garde-fous (profondeur, nombre de cibles, sous-réseau) "
      "bornent toujours la portée de la découverte.")
)


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche `a`)."""

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("AIDE"), classes="omega-title")
            yield Static(_("Raccourcis clavier"), classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(_("{key:<14} {description}").format(key=key, description=description))
            yield Static("")
            yield Static(_("Fonctions"), classes="omega-subtitle")
            for title, description in _SECTIONS:
                yield Static(f"[b]{title}[/b]\n{description}\n")
            yield Static("")
            yield Static(_("Profils de ports système"), classes="omega-subtitle")
            yield DataTable(id="profile-table")
            yield Static("")
            yield Static(_SCOPE_NOTICE, classes="omega-subtitle")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#profile-table", DataTable)
        table.add_columns(_("Profil"), _("Description"), _("Ports"), _("Épinglé"))
        for profile in SYSTEM_PROFILES.values():
            table.add_row(
                profile.name, profile.description, str(len(profile.ports)), "oui" if profile.pinned else _("non")
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
