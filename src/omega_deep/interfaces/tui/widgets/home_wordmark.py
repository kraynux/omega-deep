# Copyright (c) 2026 kraynux - Licence MIT
"""Bandeau texte OMEGA-DEEP affiche en haut de screens/home.py (logo fourni
par l'utilisateur, voir ~/DEV/DEEP/ascii.txt, section "MENU GENERAL" —
caracteres non modifies). Couleur par jetons de theme Rich/Textual
(`$accent`/`$foreground`) directement dans le markup — reactif au
changement de theme (meme mecanisme que widgets/splash_hero.py).

Pas de boite/cadre autour du bandeau (retour utilisateur : "il faut
enlever le container OMEGA-DEEP du menu principal, c'etait une erreur de
ma part, les autres n'en ont pas") — memes 3 lignes de lettres que dans
la boite OMEGA-DEEP du splash, mais sans le cadre '┌───┐'/'│ │'/'└───┘'
qui les entourait la-bas : ligne 1 vif, ligne 2 clair, ligne 3 vif, comme
omega-check."""
from __future__ import annotations

from textual.widgets import Static

_WORDMARK_LINES: tuple[str, str, str] = (
    "┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐    ┌╦╦══╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐",
    "│║   ║│ │║ ║ ║│ ├╬══    │║  ═╦┐ ├╬═══╬┤ ═  │║║  ║│ ├╬══    ├╬══    │╠═══╩┘",
    "└╩═══╩┘ └╩   ╩┘ └╩═══╩┘ └╩═══╩┘ └╩   ╩┘    └╩╩══╩┘ └╩═══╩┘ └╩═══╩┘ └╩",
)
"""OMEGA-DEEP en un seul bandeau de lettres, fourni par l'utilisateur
(~/DEV/DEEP/ascii.txt), caracteres non modifies — cadre de la boite
d'origine retire (voir docstring du module)."""

_MARKUP = "\n".join((
    f"[$accent]{_WORDMARK_LINES[0]}[/]",
    f"[$foreground]{_WORDMARK_LINES[1]}[/]",
    f"[$accent]{_WORDMARK_LINES[2]}[/]",
))


class HomeWordmark(Static):
    """Bandeau decoratif centre en haut de screens/home.py."""

    def __init__(self) -> None:
        super().__init__(_MARKUP, classes="omega-home-wordmark")
