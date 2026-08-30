from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.targets.models import Host


def test_host_defaults_to_depth_zero_no_parent() -> None:
    # depth_level=0 : cible initiale, jamais decouverte (pas de parent).
    host = Host(ip="192.168.1.10")
    assert host.depth_level == 0
    assert host.discovered_from is None
    assert host.discovery_source is None
    assert host.discovery_confidence == ConfidenceLevel.UNKNOWN


def test_host_discovered_carries_provenance() -> None:
    host = Host(
        ip="192.168.1.11",
        depth_level=1,
        discovered_from="192.168.1.10",
        discovery_source="header",
        discovery_confidence=ConfidenceLevel.DECLARED,
    )
    assert host.depth_level == 1
    assert host.discovered_from == "192.168.1.10"
    assert host.discovery_source == "header"
    assert host.discovery_confidence == ConfidenceLevel.DECLARED


def test_host_ports_default_to_empty_list() -> None:
    assert Host(ip="192.168.1.10").ports == []
