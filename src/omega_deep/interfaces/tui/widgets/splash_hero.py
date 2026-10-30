# Copyright (c) 2026 kraynux - Licence MIT
"""Composition ASCII de l'ecran de demarrage. Logo fourni par l'utilisateur,
voir ~/DEV/DEEP/ascii.txt (guide de couleurs en commentaire en tete de
fichier) — caracteres non modifies (l'utilisateur a deliberement retire
toutes les tabulations du fichier source, ne restent que des espaces).

Alignement : CONTRAIREMENT a omega-check (dont le logo est une pile de
blocs independants, chacun symetrique en lui-meme, ou re-centrer
chaque ligne sur un axe commun corrige un bug d'indentation du fichier
source) — ce logo est UNE SEULE composition integree (icone gauche +
cables + icone droite sur les memes lignes) : chaque ligne porte sa
propre indentation, deliberee et relative aux autres lignes (position de
la boite login sous l'icone gauche, du hub sous l'icone droite, etc.).
Les lignes sont donc utilisees telles quelles (seulement `rstrip()`, sans
strip() de l'indentation ni recentrage independant) — un recentrage par
ligne a ete tente puis abandonne : verifie que 14 des 25 lignes (la
moitie basse : prompt login, hub, tagline) avaient une indentation
d'origine differente de celle qu'un recentrage automatique aurait
produite, deformant leur position relative (voir historique de session).
Seul le bloc entier est centre dans l'ecran, via le `Center()` de
screens/splash.py — pas de centrage ligne par ligne ici.

Couleur par jetons de theme Rich/Textual (`$accent`=vif, `$foreground`
=clair) directement dans le markup, reactif au changement de theme (meme
mecanisme que widgets/home_wordmark.py). Regles confirmees par
l'utilisateur en direct (retour live sur le rendu, apres correctif
d'alignement) :
- cadres/"containers" (boites de bordure) : clair.
- bandeau OMEGA-DEEP (3 lignes, dans sa boite) : vif / clair / vif.
- tagline du bas : les "|" separateurs vifs, les mots clairs.
- '▓'/'▒'/'░' (nuances de gris) : clair a opacite decroissante, PARTOUT,
  sans exception (retour utilisateur : "laisse les nuances de gris comme
  ils sont c'est parfait").
- '█'/'▄' (pleins) : clair PAR DEFAUT partout (les deux icones
  "ordinateur" du haut ET le serveur central "V1.50" sont clairs en
  entier, retour utilisateur), SAUF deux exceptions ponctuelles :
  1. la "facade" du serveur en bas a droite (lignes 15-21, colonnes 53-64 —
     `_SERVER_PANEL_RANGE`) : ses '█' internes ("voyants" allumes parmi
     les zones eteintes en '░') restent vifs — seuls ces points precis,
     pas le cadre du serveur lui-meme (qui reste clair comme le reste).
  2. les deux barres "pied" pleines avec un '▓' isole en leur milieu
     (ligne 7 : base de l'icone-ecran de droite ; ligne 20 : base de la
     boite de login "~/su") : ce '▓' isole devient vif ("voyants des
     ecrans a la base, le bloc au milieu du pied" — retour utilisateur),
     alors qu'un '▓' normal (dans une nuance de gris) resterait clair.
Le texte "LINUX DEEP-ARCH TOOL" reste vif (meme convention que le "LINUX
SERVER CHECK" d'omega-check), regle non explicitee mais non contredite
par le retour utilisateur."""
from __future__ import annotations

from textual.widgets import Static

_WIDTH = 78
"""Largeur de la ligne la plus large (la boite OMEGA-DEEP) : sert
uniquement a completer les lignes plus courtes par des espaces a droite
(largeur uniforme du bloc), jamais a recentrer une ligne."""

_DENSITY_COLORS: dict[str, str] = {
    "▓": "$foreground 85%",
    "▒": "$foreground 65%",
    "░": "$foreground 45%",
}
"""'█'/'▄' n'y figurent pas : leur couleur depend de la position (voir
_shaded ci-dessous), clair par defaut, vif seulement dans
_SERVER_PANEL_RANGE (lignes 15-21)."""

_SERVER_PANEL_RANGE: tuple[int, int] = (53, 65)
"""Colonnes de l'interieur de la facade du serveur en bas a droite
(lignes 15-21), entre ses deux piliers de cadre ('█' aux colonnes 52 et
65, eux traites comme le reste du cadre : clairs). Les '█' isoles dans
cet intervalle sont les "voyants" allumes (retour utilisateur) et
restent vifs ; en dehors, '█'/'▄' sont clairs partout ailleurs dans le
logo (icones, serveur central, cables, boite de login)."""


def _padded(line: str) -> str:
    """Complete a droite jusqu'a `_WIDTH` : ne touche jamais l'indentation
    de gauche de `line`, deliberee (voir docstring du module)."""
    return line.ljust(_WIDTH)


def _shaded(
    line: str, *, accent_range: tuple[int, int] | None = None, force_accent_at: tuple[int, ...] = ()
) -> str:
    """Ligne generique (icones/connecteurs/puce/prompt, deja completee a
    largeur uniforme) : nuances de gris ('▓'/'▒'/'░') toujours clair a
    opacite decroissante ; '█'/'▄' clairs par defaut, vifs uniquement
    dans `accent_range` (colonnes, bornes incluse/exclue) ou a l'index
    exact d'un `force_accent_at` (utilise pour les deux '▓' isoles des
    barres "pied", vifs par exception — voir docstring du module)."""
    parts: list[str] = []
    current_color = "$foreground"
    buffer: list[str] = []
    for index, ch in enumerate(line):
        if index in force_accent_at:
            color = "$accent"
        elif ch in ("█", "▄"):
            in_range = accent_range is not None and accent_range[0] <= index < accent_range[1]
            color = "$accent" if in_range else "$foreground"
        else:
            color = _DENSITY_COLORS.get(ch, "$foreground")
        if color != current_color and buffer:
            parts.append(f"[{current_color}]{''.join(buffer)}[/]")
            buffer = []
        current_color = color
        buffer.append(ch)
    if buffer:
        parts.append(f"[{current_color}]{''.join(buffer)}[/]")
    return "".join(parts)


def _framed(line: str, *, inner_color: str) -> str:
    """Ligne '│ texte │' (deja centree, cadre '│' des deux cotes) -> cadre
    clair, texte dans la couleur demandee."""
    prefix, _, rest = line.partition("│")
    inner, _, suffix = rest.rpartition("│")
    return f"{prefix}[$foreground]│[/][{inner_color}]{inner}[/][$foreground]│{suffix}[/]"


def _tagline(line: str) -> str:
    """'SCAN | DEEP-ARCH | ...' -> mots clairs, '|' vifs."""
    parts = line.split("|")
    colored = [f"[$foreground]{part}[/]" for part in parts]
    return "[$accent]|[/]".join(colored)


_HERO_LINES: tuple[str, ...] = ('                          ┌────────────────────────┐', '                          │  LINUX DEEP-ARCH TOOL  │', '      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   └────────────────────────┘   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄', '      █╚╗░╔╝░░░╔══╝░░░█╗               │              ╔█      ║▒║      █', '      █░╚═╩╗░░╔╝░╔════█╠════════════╦┐ │ ┌╦═══════════╣█     ║▒ ▒║     █', '      █░░░░╠══╩══╣░╔╗░█╝            ║│ │ │║           ╚█    ║▒▒▒▒▒║    █', '      █░╔══╝░░░░░╚═╝╚═█        ┌▄█████████████▄┐       █   ║▒     ▒║   █', '      █████████████████        │███████████████│       ████████▓████████', '           ╠██▒██╣             │████▒V1.50▒████│             ║███║', '┌────────────────────────────────────────────────────────────────────────────┐', '│ ┌╦═══╦┐ ┌╦═╦═╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐    ┌╦╦══╦┐ ┌╦═══╦┐ ┌╦═══╦┐ ┌╦═══╦┐ │', '│ │║   ║│ │║ ║ ║│ ├╬══    │║  ═╦┐ ├╬═══╬┤ ═  │║║  ║│ ├╬══    ├╬══    │╠═══╩┘ │', '│ └╩═══╩┘ └╩   ╩┘ └╩═══╩┘ └╩═══╩┘ └╩   ╩┘    └╩╩══╩┘ └╩═══╩┘ └╩═══╩┘ └╩      │', '└────────────────────────────────────────────────────────────────────────────┘', '                               └███████████████┘    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄', '          ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄           ║▓║          ╔█░░░░░░░░░░░░█══╣  ╠╗', '          █┌─────────────┐█           ║▓║          ║█░▒▓█▒░░▒█▓▒░█┐   ┌╦╬╦┐', '          █│~/su░░░░░░░░░│█    █▓▒▒▓███████▓▒▒▓█   ║█░░░░░░░░░░░░█│   └╩╬╩┘', '          █│Password :▒░░│█╗        ║│ │ │║        ║█░▒▓▓▒░░▒▓▓▒░█│     ║', '          █└─────────────┘█╠════════╩┘ │ │║        ║█░░░░░░░░░░░░█│     ║', '          ████████▓████████╝           │ └╩════════╣█░▒█▓▒░░▒▓█▒░█┘   ┌╦╬╦┐', '               ╠═════╣                 │           ╚█░░░░░░░░░░░░█╗   └╩╬╩┘', '           ╠█░░░░░░░░░░░█╣        ┌╦═══════╦┐       ██████████████╩═════╝', '                                  └╩═══════╩┘', '                       SCAN | DEEP-ARCH | NETWORKS | EXPORT')
"""Logo brut (rstrip() du saut de ligne uniquement — l'indentation de
gauche N'EST PAS retiree, elle code la position relative des elements
entre eux), fourni par l'utilisateur (~/DEV/DEEP/ascii.txt), caracteres
non modifies."""

_LINES: tuple[str, ...] = (
    f"[$foreground]{_padded(_HERO_LINES[0])}[/]",
    _framed(_padded(_HERO_LINES[1]), inner_color="$accent"),
    _shaded(_padded(_HERO_LINES[2])),
    _shaded(_padded(_HERO_LINES[3])),
    _shaded(_padded(_HERO_LINES[4])),
    _shaded(_padded(_HERO_LINES[5])),
    _shaded(_padded(_HERO_LINES[6])),
    _shaded(_padded(_HERO_LINES[7]), force_accent_at=(63,)),  # ▓ isole, base de l'icone-ecran droite
    _shaded(_padded(_HERO_LINES[8])),
    f"[$foreground]{_padded(_HERO_LINES[9])}[/]",
    _framed(_padded(_HERO_LINES[10]), inner_color="$accent"),
    _framed(_padded(_HERO_LINES[11]), inner_color="$foreground"),
    _framed(_padded(_HERO_LINES[12]), inner_color="$accent"),
    f"[$foreground]{_padded(_HERO_LINES[13])}[/]",
    _shaded(_padded(_HERO_LINES[14])),
    _shaded(_padded(_HERO_LINES[15]), accent_range=_SERVER_PANEL_RANGE),
    _shaded(_padded(_HERO_LINES[16]), accent_range=_SERVER_PANEL_RANGE),
    _shaded(_padded(_HERO_LINES[17]), accent_range=_SERVER_PANEL_RANGE),
    _shaded(_padded(_HERO_LINES[18]), accent_range=_SERVER_PANEL_RANGE),
    _shaded(_padded(_HERO_LINES[19]), accent_range=_SERVER_PANEL_RANGE),
    # ligne 20 : voyants du serveur (accent_range) + ▓ isole de la base de la boite login (force_accent_at)
    _shaded(_padded(_HERO_LINES[20]), accent_range=_SERVER_PANEL_RANGE, force_accent_at=(18,)),
    _shaded(_padded(_HERO_LINES[21]), accent_range=_SERVER_PANEL_RANGE),
    _shaded(_padded(_HERO_LINES[22])),
    _shaded(_padded(_HERO_LINES[23])),
    _tagline(_padded(_HERO_LINES[24])),
)

_MARKUP = "\n".join(_LINES)


class SplashHero(Static):
    """Bloc decoratif de l'ecran de demarrage (screens/splash.py)."""

    def __init__(self) -> None:
        super().__init__(_MARKUP, classes="omega-splash-hero")
