from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.architecture.service import reconstruct_architecture
from omega_deep.domain.targets.models import Host


def test_root_host_has_no_edge() -> None:
    root = Host(ip="192.168.1.10", depth_level=0)
    graph = reconstruct_architecture([root])

    assert graph.nodes == ["192.168.1.10"]
    assert graph.edges == []
    assert graph.root_node == "192.168.1.10"


def test_discovered_host_produces_an_edge_with_mapped_relation() -> None:
    root = Host(ip="192.168.1.10", depth_level=0)
    discovered = Host(
        ip="192.168.1.11",
        depth_level=1,
        discovered_from="192.168.1.10",
        discovery_source="header",
        discovery_confidence=ConfidenceLevel.DECLARED,
    )

    graph = reconstruct_architecture([root, discovered])

    assert graph.nodes == ["192.168.1.10", "192.168.1.11"]
    assert len(graph.edges) == 1
    edge = graph.edges[0]
    assert edge.source_ip == "192.168.1.10"
    assert edge.target_ip == "192.168.1.11"
    assert edge.relation_type == "proxy_to"
    assert edge.confidence == ConfidenceLevel.DECLARED


def test_multi_hop_chain_produces_one_edge_per_discovered_host() -> None:
    root = Host(ip="10.0.0.1", depth_level=0)
    hop1 = Host(
        ip="10.0.0.2", depth_level=1, discovered_from="10.0.0.1",
        discovery_source="redirection", discovery_confidence=ConfidenceLevel.DECLARED,
    )
    hop2 = Host(
        ip="10.0.0.3", depth_level=2, discovered_from="10.0.0.2",
        discovery_source="html_link", discovery_confidence=ConfidenceLevel.INFERRED,
    )

    graph = reconstruct_architecture([root, hop1, hop2])

    assert len(graph.edges) == 2
    relations = {(e.source_ip, e.target_ip): e.relation_type for e in graph.edges}
    assert relations[("10.0.0.1", "10.0.0.2")] == "redirect_to"
    assert relations[("10.0.0.2", "10.0.0.3")] == "linked_to"


def test_empty_hosts_returns_empty_graph() -> None:
    graph = reconstruct_architecture([])
    assert graph.nodes == []
    assert graph.edges == []
    assert graph.root_node == ""


def test_no_root_present_still_builds_edges_with_empty_root_node() -> None:
    # Cas degenere (ne devrait pas arriver en pratique : la cible initiale
    # est toujours depth_level=0) — verifie juste l'absence de crash.
    only_discovered = Host(
        ip="10.0.0.2", depth_level=1, discovered_from="10.0.0.1",
        discovery_source="header", discovery_confidence=ConfidenceLevel.DECLARED,
    )
    graph = reconstruct_architecture([only_discovered])
    assert graph.root_node == ""
    assert len(graph.edges) == 1
