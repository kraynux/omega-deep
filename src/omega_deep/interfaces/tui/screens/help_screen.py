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

_SHORTCUTS = (
    ("Haut / Bas", "Naviguer entre les elements d'un ecran"),
    ("Tab / Maj+Tab", "Naviguer entre les champs d'un formulaire"),
    ("Echap", "Retour a l'ecran precedent (confirmation de sortie sur l'accueil)"),
    ("t", "Theme suivant (applique immediatement, sans confirmation)"),
    ("r", "Rafraichir la detection du terminal"),
    ("a", "Cette aide"),
    ("q", "Quitter (avec confirmation)"),
)

_SECTIONS = (
    (
        "Analyser",
        (
            "Saisir une cible racine (IP ou hostname), un profil de ports et les garde-fous "
            "de decouverte (profondeur max, nombre de cibles supplementaires, sous-reseau "
            "autorise), puis lancer l'analyse. Chaque cible decouverte est presentee pour "
            "validation avant tout scan (aucune cible n'est jamais scannee automatiquement)."
        ),
    ),
    (
        "Historique",
        (
            "Liste toutes les analyses passees : detail complet (hosts + graphe "
            "d'architecture), comparaison entre deux analyses, ou rejouer une analyse sur "
            "la meme cible racine."
        ),
    ),
    (
        "Export",
        (
            "Depuis le detail d'une analyse : JSON (structure complete), texte (rapport "
            "compact) ou HTML (rapport visuel avec diagramme du graphe d'architecture, "
            "theme d'export independant du theme de l'interface)."
        ),
    ),
)

_SCOPE_NOTICE = (
    "Omega-deep decouvre et cartographie l'architecture autour d'une cible racine (analyse "
    "multi-cibles) : chaque cible decouverte (lien HTTP, service annonce) est proposee a "
    "l'utilisateur — jamais scannee sans validation explicite (fail-safe : tout ce qui n'est "
    "pas confirme est rejete). Les garde-fous (profondeur, nombre de cibles, sous-reseau) "
    "bornent toujours la portee de la decouverte."
)


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche `a`)."""

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static("AIDE", classes="omega-title")
            yield Static("Raccourcis clavier", classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(f"{key:<14} {description}")
            yield Static("")
            yield Static("Fonctions", classes="omega-subtitle")
            for title, description in _SECTIONS:
                yield Static(f"[b]{title}[/b]\n{description}\n")
            yield Static("")
            yield Static("Profils de ports systeme", classes="omega-subtitle")
            yield DataTable(id="profile-table")
            yield Static("")
            yield Static(_SCOPE_NOTICE, classes="omega-subtitle")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#profile-table", DataTable)
        table.add_columns("Profil", "Description", "Ports", "Epingle")
        for profile in SYSTEM_PROFILES.values():
            table.add_row(
                profile.name, profile.description, str(len(profile.ports)), "oui" if profile.pinned else "non"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
