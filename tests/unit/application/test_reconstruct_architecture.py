from omega_deep.application.commands.reconstruct_architecture import reconstruct_architecture
from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.targets.models import Host


def test_delegates_to_domain_service() -> None:
    root = Host(ip="192.168.1.10", depth_level=0)
    discovered = Host(
        ip="192.168.1.11", depth_level=1, discovered_from="192.168.1.10",
        discovery_source="header", discovery_confidence=ConfidenceLevel.DECLARED,
    )

    graph = reconstruct_architecture([root, discovered])

    assert graph.root_node == "192.168.1.10"
    assert graph.nodes == ["192.168.1.10", "192.168.1.11"]
    assert len(graph.edges) == 1
    assert graph.edges[0].relation_type == "proxy_to"
