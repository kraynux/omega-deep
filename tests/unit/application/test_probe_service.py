from omega_deep.application.commands.probe_service import probe_service
from omega_deep.domain.services.models import Service


class FakeHttpProber:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, str, float, bool]] = []

    def probe(self, target_ip: str, port: int, host_header: str, timeout: float, use_tls: bool) -> Service:
        self.calls.append((target_ip, port, host_header, timeout, use_tls))
        return Service(protocol_name="HTTPS" if use_tls else "HTTP")


class FakeTlsProber:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, str, float]] = []

    def probe(self, target_ip: str, port: int, sni_hostname: str, timeout: float) -> Service:
        self.calls.append((target_ip, port, sni_hostname, timeout))
        return Service(tls_version="TLSv1.3")


class FakeSshProber:
    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        return Service(protocol_name="SSH")


class FakeVncProber:
    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        return Service(protocol_name="VNC")


class FakeGenericProber:
    def probe(self, target_ip: str, port: int, timeout: float) -> Service:
        return Service(protocol_name=None, software="mystery-daemon")


def _probers() -> dict[str, object]:
    return {
        "http_prober": FakeHttpProber(),
        "tls_prober": FakeTlsProber(),
        "ssh_prober": FakeSshProber(),
        "vnc_prober": FakeVncProber(),
        "generic_prober": FakeGenericProber(),
    }


def test_https_port_calls_both_http_and_tls_and_merges() -> None:
    probers = _probers()
    result = probe_service(target_ip="10.0.0.1", port=443, host_header="example.com", **probers)  # type: ignore[arg-type]

    assert result.protocol_name == "HTTPS"
    assert result.tls_version == "TLSv1.3"
    assert probers["http_prober"].calls == [("10.0.0.1", 443, "example.com", 2.0, True)]  # type: ignore[attr-defined]
    assert probers["tls_prober"].calls == [("10.0.0.1", 443, "example.com", 2.0)]  # type: ignore[attr-defined]


def test_http_port_calls_only_http_without_tls() -> None:
    probers = _probers()
    result = probe_service(target_ip="10.0.0.1", port=8080, host_header="example.com", **probers)  # type: ignore[arg-type]

    assert result.protocol_name == "HTTP"
    assert probers["http_prober"].calls == [("10.0.0.1", 8080, "example.com", 2.0, False)]  # type: ignore[attr-defined]
    assert probers["tls_prober"].calls == []  # type: ignore[attr-defined]


def test_ssh_port_dispatches_to_ssh_prober() -> None:
    result = probe_service(target_ip="10.0.0.1", port=22, host_header="example.com", **_probers())  # type: ignore[arg-type]
    assert result.protocol_name == "SSH"


def test_unknown_port_dispatches_to_generic_prober() -> None:
    result = probe_service(target_ip="10.0.0.1", port=21, host_header="example.com", **_probers())  # type: ignore[arg-type]
    assert result.software == "mystery-daemon"


def test_vnc_port_dispatches_to_vnc_prober() -> None:
    result = probe_service(target_ip="10.0.0.1", port=5900, host_header="example.com", **_probers())  # type: ignore[arg-type]
    assert result.protocol_name == "VNC"
