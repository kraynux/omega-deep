import re

from omega_lib.theme.policies import EXPORT_PALETTES

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.architecture.models import ArchitectureEdge, ArchitectureGraph
from omega_deep.infrastructure.exporters.graph_layout import render_architecture_svg

_PALETTE = EXPORT_PALETTES["omega-base"]


def _graph(*, root: str = "192.168.1.10", edges: list[ArchitectureEdge] | None = None) -> ArchitectureGraph:
    if edges is None:
        edges = [
            ArchitectureEdge(
                source_ip="192.168.1.10", target_ip="192.168.1.11", relation_type="proxy_to",
                confidence=ConfidenceLevel.DECLARED,
            )
        ]
    nodes = sorted({root, *(e.source_ip for e in edges), *(e.target_ip for e in edges)})
    return ArchitectureGraph(nodes=nodes, edges=edges, root_node=root)


def test_render_architecture_svg_returns_empty_string_for_graph_with_no_nodes() -> None:
    empty = ArchitectureGraph(nodes=[], edges=[], root_node="")
    assert render_architecture_svg(empty, _PALETTE) == ""


def test_render_architecture_svg_produces_valid_svg_root_element() -> None:
    output = render_architecture_svg(_graph(), _PALETTE)
    assert output.startswith("<svg")
    assert output.endswith("</svg>")


def test_render_architecture_svg_includes_both_node_ip_labels() -> None:
    output = render_architecture_svg(_graph(), _PALETTE)
    assert "192.168.1.10" in output
    assert "192.168.1.11" in output


def test_render_architecture_svg_includes_relation_and_confidence_label() -> None:
    output = render_architecture_svg(_graph(), _PALETTE)
    assert "proxy_to" in output
    assert "declared" in output


def test_render_architecture_svg_places_deeper_nodes_further_down() -> None:
    """Mise en page en couches : un noeud a la profondeur 2 (B -> C) doit
    etre place plus bas (cy plus grand) qu'un noeud a la profondeur 1
    (A -> B), lui-meme plus bas que la racine (A, profondeur 0)."""
    graph = _graph(
        root="A",
        edges=[
            ArchitectureEdge(source_ip="A", target_ip="B", relation_type="proxy_to", confidence=ConfidenceLevel.DECLARED),
            ArchitectureEdge(source_ip="B", target_ip="C", relation_type="linked_to", confidence=ConfidenceLevel.INFERRED),
        ],
    )
    output = render_architecture_svg(graph, _PALETTE)

    # Les noeuds sont dessines dans l'ordre trie par profondeur (voir
    # _layout) : le 1er cercle est la racine, le dernier le plus profond.
    cy_values = [float(m) for m in re.findall(r'<circle cx="[\d.]+" cy="([\d.]+)"', output)]
    assert len(cy_values) == 3
    assert cy_values[0] < cy_values[1] < cy_values[2]


def test_render_architecture_svg_escapes_untrusted_relation_type() -> None:
    """`relation_type`/IP proviennent in fine d'un en-tete HTTP ou d'un lien
    HTML d'une cible scannee (jamais dignes de confiance) : doit etre
    echappe avant insertion dans le SVG, jamais interprete comme balise."""
    graph = _graph(
        edges=[
            ArchitectureEdge(
                source_ip="192.168.1.10", target_ip="192.168.1.11",
                relation_type="<script>alert(1)</script>", confidence=ConfidenceLevel.DECLARED,
            )
        ]
    )
    output = render_architecture_svg(graph, _PALETTE)
    assert "<script>" not in output
    assert "&lt;script&gt;" in output


def test_render_architecture_svg_falls_back_to_first_node_when_root_unknown() -> None:
    """`root_node` absent de `nodes` (defensif, ne devrait pas arriver en
    pratique) : la mise en page ne doit pas planter, un noeud est choisi
    comme racine de la mise en page malgre tout."""
    graph = ArchitectureGraph(
        nodes=["192.168.1.10", "192.168.1.11"],
        edges=[
            ArchitectureEdge(
                source_ip="192.168.1.10", target_ip="192.168.1.11", relation_type="linked_to",
                confidence=ConfidenceLevel.INFERRED,
            )
        ],
        root_node="unknown",
    )
    output = render_architecture_svg(graph, _PALETTE)
    assert output.startswith("<svg")
    assert "192.168.1.10" in output
    assert "192.168.1.11" in output
