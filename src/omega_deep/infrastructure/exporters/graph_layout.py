# Copyright (c) 2026 kraynux - Licence MIT
"""Rendu du graphe d'architecture en SVG pour l'export HTML
(OMEGA-DEEP_SPECIFICATIONS.md §9, D-009 : "un vrai diagramme du graphe
(noeuds + aretes dessines, pas un tableau)"). Genere a la main (mise en
page en couches par BFS depuis `graph.root_node`, positions calculees ici
en Python) : aucune dependance de layout de graphe lourde (type
graphviz) — le graphe reste petit (un host racine + ses cibles
decouvertes, jamais plus de `max_additional_targets`), une mise en page
naive suffit.

N'importe PAS jinja2 (voir html_exporter.py, seul module autorise a le
faire) : construit une chaine `<svg>...</svg>` complete et autonome,
directement embarquee par le template via `| safe`. Toutes les valeurs
dynamiques (IP, type de relation) sont issues de cibles potentiellement
decouvertes depuis un host scanne — jamais dignes de confiance —
`xml.sax.saxutils.escape` est donc applique systematiquement avant
insertion dans le SVG."""
from __future__ import annotations

from dataclasses import dataclass
from xml.sax.saxutils import escape

from omega_lib.theme.policies import Palette

from omega_deep.domain.architecture.models import ArchitectureGraph

_NODE_RADIUS = 26
_LAYER_HEIGHT = 150
"""Assez d'espace vertical entre deux couches pour que l'etiquette d'une
arete (au milieu de la ligne) ne chevauche jamais la legende IP du noeud
source, juste en dessous de son cercle."""
_NODE_SPACING = 180
_MARGIN = 60


@dataclass(frozen=True)
class _PlacedNode:
    ip: str
    x: float
    y: float
    is_root: bool


def _layout(graph: ArchitectureGraph) -> tuple[dict[str, _PlacedNode], int, int]:
    """BFS depuis `graph.root_node` (ou le premier noeud si la racine est
    absente/inconnue — defensif, ne devrait pas arriver en pratique) pour
    assigner une profondeur a chaque noeud, puis repartir chaque couche
    a largeur egale. Un noeud jamais atteint (aucune arete entrante,
    isole) est place dans une derniere couche plutot qu'ignore."""
    children: dict[str, list[str]] = {}
    for edge in graph.edges:
        children.setdefault(edge.source_ip, []).append(edge.target_ip)

    root = graph.root_node if graph.root_node in graph.nodes else (graph.nodes[0] if graph.nodes else "")

    depth_by_node: dict[str, int] = {}
    if root:
        queue = [root]
        depth_by_node[root] = 0
        while queue:
            current = queue.pop(0)
            for child in children.get(current, []):
                if child not in depth_by_node:
                    depth_by_node[child] = depth_by_node[current] + 1
                    queue.append(child)

    orphan_depth = max(depth_by_node.values(), default=-1) + 1
    layers: dict[int, list[str]] = {}
    for ip in graph.nodes:
        depth = depth_by_node.get(ip, orphan_depth)
        layers.setdefault(depth, []).append(ip)

    max_nodes_per_layer = max((len(layer) for layer in layers.values()), default=1)
    width = max(1, max_nodes_per_layer) * _NODE_SPACING + 2 * _MARGIN
    height = len(layers) * _LAYER_HEIGHT + 2 * _MARGIN

    placed: dict[str, _PlacedNode] = {}
    for depth in sorted(layers):
        row = sorted(layers[depth])
        y = _MARGIN + depth * _LAYER_HEIGHT + _NODE_RADIUS
        step = (width - 2 * _MARGIN) / len(row)
        for index, ip in enumerate(row):
            x = _MARGIN + (index + 0.5) * step
            placed[ip] = _PlacedNode(ip=ip, x=x, y=y, is_root=(ip == root))

    return placed, width, height


def render_architecture_svg(graph: ArchitectureGraph, palette: Palette) -> str:
    """Diagramme SVG autonome (noeuds = cercles, aretes = fleches
    etiquetees par le type de relation), pret a etre insere directement
    dans le HTML (`| safe`, voir templates/scan_report.html.j2)."""
    placed, width, height = _layout(graph)
    if not placed:
        return ""

    # `width`/`height` fixes a la taille naturelle du graphe (pas "100%") :
    # un petit graphe (peu de machines) doit rester petit, pas s'etirer
    # pour remplir la largeur de la page. `.graph-box svg { max-width:
    # 100% }` (template) ne fait que REDUIRE un graphe plus large que le
    # conteneur (beaucoup de machines) — jamais agrandir un petit graphe.
    svg_open = (
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Graphe d\'architecture">'
    )
    arrow_marker = (
        f'<marker id="omega-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{palette.secondary}"/></marker>'
    )
    parts: list[str] = [svg_open, "<defs>", arrow_marker, "</defs>"]

    for edge in graph.edges:
        source = placed.get(edge.source_ip)
        target = placed.get(edge.target_ip)
        if source is None or target is None:
            continue
        dx, dy = target.x - source.x, target.y - source.y
        distance = max((dx**2 + dy**2) ** 0.5, 1e-6)
        ux, uy = dx / distance, dy / distance
        x1, y1 = source.x + ux * _NODE_RADIUS, source.y + uy * _NODE_RADIUS
        x2, y2 = target.x - ux * (_NODE_RADIUS + 8), target.y - uy * (_NODE_RADIUS + 8)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{palette.secondary}" stroke-width="1.5" marker-end="url(#omega-arrow)"/>'
        )
        label = escape(f"{edge.relation_type} [{edge.confidence.value}]")
        parts.append(
            f'<rect x="{mid_x - 55:.1f}" y="{mid_y - 10:.1f}" width="110" height="16" '
            f'fill="{palette.surface}" opacity="0.9"/>'
        )
        parts.append(
            f'<text x="{mid_x:.1f}" y="{mid_y + 2:.1f}" text-anchor="middle" '
            f'font-size="10" font-family="ui-monospace, monospace" fill="{palette.secondary}">{label}</text>'
        )

    for node in placed.values():
        fill = palette.accent if node.is_root else palette.panel
        text_color = palette.background if node.is_root else palette.foreground
        parts.append(
            f'<circle cx="{node.x:.1f}" cy="{node.y:.1f}" r="{_NODE_RADIUS}" '
            f'fill="{fill}" stroke="{palette.accent}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{node.x:.1f}" y="{node.y + 4:.1f}" text-anchor="middle" '
            f'font-size="9" font-family="ui-monospace, monospace" fill="{text_color}">'
            f"{escape(_short_label(node.ip))}</text>"
        )
        parts.append(
            f'<text x="{node.x:.1f}" y="{node.y + _NODE_RADIUS + 14:.1f}" text-anchor="middle" '
            f'font-size="10" font-family="ui-monospace, monospace" fill="{palette.foreground}">'
            f"{escape(node.ip)}</text>"
        )

    parts.append("</svg>")
    return "".join(parts)


def _short_label(ip: str) -> str:
    """Dernier octet de l'IP (ou repli sur les 4 premiers caracteres pour
    un hostname/IPv6) : identifiant court affiche a l'interieur du cercle,
    l'IP complete restant affichee juste en dessous."""
    last_octet = ip.rsplit(".", 1)[-1]
    return last_octet if last_octet.isdigit() else ip[:4]
