from omega_deep.application.commands.discover_targets import discover_targets
from omega_deep.core.enums import ConfidenceLevel, PortState
from omega_deep.domain.discovery.models import DiscoveredTarget
from omega_deep.domain.services.models import Port, Service
from omega_deep.domain.targets.models import Host


class FakeDiscoveryProber:
    def __init__(self, candidates: list[DiscoveredTarget]) -> None:
        self._candidates = candidates
        self.calls: list[tuple[str, int, str, float, bool, list[str]]] = []

    def probe(
        self,
        target_ip: str,
        port: int,
        host_header: str,
        timeout: float,
        use_tls: bool,
        tls_cert_san: list[str],
    ) -> list[DiscoveredTarget]:
        self.calls.append((target_ip, port, host_header, timeout, use_tls, tls_cert_san))
        return self._candidates


def _open_http_port(port_number: int = 80, protocol_name: str = "HTTP") -> Port:
    return Port(
        port_number=port_number,
        protocol="tcp",
        state=PortState.OPEN,
        state_confidence=ConfidenceLevel.VERIFIED,
        service=Service(protocol_name=protocol_name, tls_cert_san=["DNS:backend.internal"]),
    )


def test_discover_targets_probes_only_open_http_https_ports() -> None:
    candidate = DiscoveredTarget(
        host="192.168.1.11", source="header", confidence=ConfidenceLevel.DECLARED, discovered_from="192.168.1.10"
    )
    prober = FakeDiscoveryProber([candidate])
    ssh_port = Port(port_number=22, protocol="tcp", state=PortState.OPEN, state_confidence=ConfidenceLevel.VERIFIED, service=Service(protocol_name="SSH"))
    host = Host(ip="192.168.1.10", ports=[_open_http_port(), ssh_port])

    result = discover_targets(
        host=host,
        discovery_prober=prober,
        root_ip="192.168.1.10",
        allowed_subnet=None,
        current_additional_target_count=0,
        max_additional_targets=10,
    )

    assert len(prober.calls) == 1  # seulement le port HTTP, pas le port SSH
    assert [t.host for t in result] == ["192.168.1.11"]


def test_discover_targets_filters_out_of_scope_candidates() -> None:
    candidate = DiscoveredTarget(
        host="8.8.8.8", source="header", confidence=ConfidenceLevel.DECLARED, discovered_from="192.168.1.10"
    )
    prober = FakeDiscoveryProber([candidate])
    host = Host(ip="192.168.1.10", ports=[_open_http_port()])

    result = discover_targets(
        host=host, discovery_prober=prober, root_ip="192.168.1.10", allowed_subnet=None,
        current_additional_target_count=0, max_additional_targets=10,
    )

    assert result == []


def test_discover_targets_dedupes_same_host_from_multiple_ports() -> None:
    candidate = DiscoveredTarget(
        host="192.168.1.11", source="header", confidence=ConfidenceLevel.DECLARED, discovered_from="192.168.1.10"
    )
    prober = FakeDiscoveryProber([candidate])
    host = Host(ip="192.168.1.10", ports=[_open_http_port(80), _open_http_port(8080)])

    result = discover_targets(
        host=host, discovery_prober=prober, root_ip="192.168.1.10", allowed_subnet=None,
        current_additional_target_count=0, max_additional_targets=10,
    )

    assert len(result) == 1  # meme candidat trouve sur les 2 ports, dedup


def test_discover_targets_respects_remaining_slot_budget() -> None:
    candidates = [
        DiscoveredTarget(host="192.168.1.11", source="header", confidence=ConfidenceLevel.DECLARED, discovered_from="192.168.1.10"),
        DiscoveredTarget(host="192.168.1.12", source="header", confidence=ConfidenceLevel.DECLARED, discovered_from="192.168.1.10"),
    ]
    prober = FakeDiscoveryProber(candidates)
    host = Host(ip="192.168.1.10", ports=[_open_http_port()])

    result = discover_targets(
        host=host, discovery_prober=prober, root_ip="192.168.1.10", allowed_subnet=None,
        current_additional_target_count=9, max_additional_targets=10,
    )

    assert len(result) == 1  # un seul slot restant


def test_discover_targets_returns_empty_when_budget_already_exhausted() -> None:
    prober = FakeDiscoveryProber([])
    host = Host(ip="192.168.1.10", ports=[_open_http_port()])

    result = discover_targets(
        host=host, discovery_prober=prober, root_ip="192.168.1.10", allowed_subnet=None,
        current_additional_target_count=10, max_additional_targets=10,
    )

    assert result == []
    assert prober.calls == []  # ne sonde meme pas si le budget est deja epuise


def test_discover_targets_skips_closed_ports() -> None:
    prober = FakeDiscoveryProber([])
    closed_port = Port(port_number=80, protocol="tcp", state=PortState.CLOSED, state_confidence=ConfidenceLevel.VERIFIED)
    host = Host(ip="192.168.1.10", ports=[closed_port])

    result = discover_targets(
        host=host, discovery_prober=prober, root_ip="192.168.1.10", allowed_subnet=None,
        current_additional_target_count=0, max_additional_targets=10,
    )

    assert result == []
    assert prober.calls == []
