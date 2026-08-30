from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.discovery.models import DiscoveredTarget
from omega_deep.domain.discovery.service import filter_discovered_targets


def test_filter_keeps_only_in_scope_candidates() -> None:
    candidates = [
        DiscoveredTarget(host="192.168.1.11", source="header", confidence=ConfidenceLevel.DECLARED, discovered_from="192.168.1.10"),
        DiscoveredTarget(host="8.8.8.8", source="header", confidence=ConfidenceLevel.DECLARED, discovered_from="192.168.1.10"),
        DiscoveredTarget(host="backend.internal", source="html_link", confidence=ConfidenceLevel.INFERRED, discovered_from="192.168.1.10"),
    ]

    kept = filter_discovered_targets(candidates, root_ip="192.168.1.10")

    assert [c.host for c in kept] == ["192.168.1.11"]


def test_filter_with_no_candidates_returns_empty() -> None:
    assert filter_discovered_targets([], root_ip="192.168.1.10") == []
