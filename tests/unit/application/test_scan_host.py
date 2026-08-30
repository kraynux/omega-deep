from omega_deep.application.commands.scan_host import scan_host
from omega_deep.core.enums import ConfidenceLevel, PortState
from omega_deep.domain.services.models import Port, Service


class FakePortProber:
    def probe(self, target_ip: str, port: int, protocol: str, timeout: float, retries: int) -> Port:
        return Port(port_number=port, protocol=protocol, state=PortState.OPEN, state_confidence=ConfidenceLevel.VERIFIED)


class FakeHttpProber:
    def probe(self, target_ip: str, port: int, host_header: str, timeout: float, use_tls: bool) -> Service:
        return Service(protocol_name="HTTPS" if use_tls else "HTTP")


class FakeTlsProber:
    def probe(self, target_ip: str, port: int, sni_hostname: str, timeout: float) -> Service:
        return Service(tls_version="TLSv1.3")


class FakeSshProber:
    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        return Service(protocol_name="SSH")


class FakeVncProber:
    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        return Service(protocol_name="VNC")


class FakeGenericProber:
    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        return Service()


def _probers() -> dict[str, object]:
    return {
        "port_prober": FakePortProber(),
        "http_prober": FakeHttpProber(),
        "tls_prober": FakeTlsProber(),
        "ssh_prober": FakeSshProber(),
        "vnc_prober": FakeVncProber(),
        "generic_prober": FakeGenericProber(),
    }


def test_scan_host_defaults_to_root_provenance() -> None:
    host = scan_host(target_ip="10.0.0.5", ports=[22, 80], host_header="10.0.0.5", **_probers())  # type: ignore[arg-type]

    assert host.ip == "10.0.0.5"
    assert host.depth_level == 0
    assert host.discovered_from is None
    assert len(host.ports) == 2
    assert all(port.service is not None for port in host.ports)


def test_scan_host_carries_explicit_discovery_provenance() -> None:
    host = scan_host(
        target_ip="10.0.0.6", ports=[80], host_header="10.0.0.6",
        depth_level=2, discovered_from="10.0.0.5", discovery_source="redirection",
        discovery_confidence=ConfidenceLevel.DECLARED,
        **_probers(),  # type: ignore[arg-type]
    )

    assert host.depth_level == 2
    assert host.discovered_from == "10.0.0.5"
    assert host.discovery_source == "redirection"
    assert host.discovery_confidence == ConfidenceLevel.DECLARED
