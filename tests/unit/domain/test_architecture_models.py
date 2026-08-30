from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.architecture.models import ArchitectureEdge, ArchitectureGraph


def test_architecture_graph_defaults_to_empty() -> None:
    graph = ArchitectureGraph()
    assert graph.nodes == []
    assert graph.edges == []
    assert graph.root_node == ""


def test_architecture_edge_holds_relation_and_confidence() -> None:
    edge = ArchitectureEdge(
        source_ip="192.168.1.10",
        target_ip="192.168.1.11",
        relation_type="proxy_to",
        confidence=ConfidenceLevel.INFERRED,
        evidence=["header X-Forwarded-Host: 192.168.1.11"],
    )
    assert edge.relation_type == "proxy_to"
    assert edge.confidence == ConfidenceLevel.INFERRED
    assert edge.evidence == ["header X-Forwarded-Host: 192.168.1.11"]


def test_architecture_graph_holds_nodes_and_edges() -> None:
    edge = ArchitectureEdge(source_ip="10.0.0.1", target_ip="10.0.0.2", relation_type="backend_of")
    graph = ArchitectureGraph(nodes=["10.0.0.1", "10.0.0.2"], edges=[edge], root_node="10.0.0.1")
    assert graph.nodes == ["10.0.0.1", "10.0.0.2"]
    assert graph.edges == [edge]
    assert graph.root_node == "10.0.0.1"
