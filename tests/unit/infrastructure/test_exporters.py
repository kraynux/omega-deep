import json

from omega_deep.core.enums import ConfidenceLevel, PortState, ScanMode, ScanStatus
from omega_deep.domain.architecture.models import ArchitectureEdge, ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.services.models import Port, Service
from omega_deep.domain.targets.models import Host
from omega_deep.infrastructure.exporters.exporter import CompositeReportExporter
from omega_deep.infrastructure.exporters.html_exporter import export_html
from omega_deep.infrastructure.exporters.json_exporter import export_json
from omega_deep.infrastructure.exporters.text_exporter import export_text


def _scan() -> Scan:
    return Scan(
        id="scan-1",
        created_at="2026-08-29T00:00:00+00:00",
        target="192.168.1.10",
        target_ip="192.168.1.10",
        profile_name="minimal",
        profile_origin="system",
        scan_mode=ScanMode.PROFILE,
        status=ScanStatus.COMPLETED,
    )


def _host(ip: str = "192.168.1.10", depth_level: int = 0) -> Host:
    service = Service(
        protocol_name="SSH",
        protocol_confidence=ConfidenceLevel.VERIFIED,
        software="OpenSSH",
        software_confidence=ConfidenceLevel.DECLARED,
        version="10.4",
        role="acces shell",
        role_confidence=ConfidenceLevel.CORROBORATED,
    )
    port = Port(port_number=22, protocol="tcp", state=PortState.OPEN, state_confidence=ConfidenceLevel.VERIFIED, service=service)
    return Host(ip=ip, ports=[port], depth_level=depth_level)


def _graph() -> ArchitectureGraph:
    return ArchitectureGraph(
        nodes=["192.168.1.10", "192.168.1.11"],
        edges=[
            ArchitectureEdge(
                source_ip="192.168.1.10", target_ip="192.168.1.11", relation_type="proxy_to",
                confidence=ConfidenceLevel.DECLARED,
            )
        ],
        root_node="192.168.1.10",
    )


def test_export_json_round_trips_via_json_loads() -> None:
    output = export_json(_scan(), (_host(),), None)
    parsed = json.loads(output)

    assert parsed["scan"]["id"] == "scan-1"
    assert parsed["hosts"][0]["ports"][0]["port_number"] == 22
    assert parsed["hosts"][0]["ports"][0]["service"]["software"] == "OpenSSH"
    assert parsed["hosts"][0]["ports"][0]["service"]["protocol_confidence"] == "verified"
    assert parsed["architecture_graph"] is None


def test_export_json_includes_graph_when_present() -> None:
    output = export_json(_scan(), (_host(),), _graph())
    parsed = json.loads(output)
    assert parsed["architecture_graph"]["root_node"] == "192.168.1.10"
    assert parsed["architecture_graph"]["edges"][0]["relation_type"] == "proxy_to"


def test_export_json_handles_no_hosts() -> None:
    output = export_json(_scan(), (), None)
    parsed = json.loads(output)
    assert parsed["hosts"] == []


def test_export_text_contains_key_facts() -> None:
    output = export_text(_scan(), (_host(),), None)
    assert "scan-1" in output
    assert "22/tcp : open" in output
    assert "OpenSSH 10.4" in output
    assert "acces shell" in output


def test_export_text_handles_no_hosts() -> None:
    output = export_text(_scan(), (), None)
    assert "echoue" in output


def test_export_text_includes_graph_section() -> None:
    output = export_text(_scan(), (_host(), _host(ip="192.168.1.11", depth_level=1)), _graph())
    assert "Graphe d'architecture" in output
    assert "192.168.1.10 --proxy_to--> 192.168.1.11" in output


def test_export_html_renders_port_and_role() -> None:
    output = export_html(_scan(), (_host(),), None)
    assert "192.168.1.10" in output
    assert "OpenSSH" in output
    assert "acces shell" in output
    assert "<table>" in output


def test_export_html_handles_no_hosts() -> None:
    output = export_html(_scan(), (), None)
    assert "échoué" in output


def test_export_html_renders_graph_section_when_present() -> None:
    output = export_html(_scan(), (_host(),), _graph())
    assert "proxy_to" in output
    assert "192.168.1.11" in output


def test_export_html_uses_requested_export_theme_palette() -> None:
    from omega_lib.theme.policies import EXPORT_PALETTES

    output = export_html(_scan(), (_host(),), None, theme_name="omega-neon")
    assert EXPORT_PALETTES["omega-neon"].background in output
    assert EXPORT_PALETTES["omega-base"].background not in output


def test_export_html_unknown_theme_falls_back_to_default() -> None:
    from omega_lib.theme.policies import EXPORT_PALETTES

    output = export_html(_scan(), (_host(),), None, theme_name="does-not-exist")
    assert EXPORT_PALETTES["omega-base"].background in output


def test_composite_exporter_delegates_to_each_format() -> None:
    exporter = CompositeReportExporter()
    scan, hosts, graph = _scan(), (_host(),), _graph()
    assert exporter.export_json(scan, hosts, graph) == export_json(scan, hosts, graph)
    assert exporter.export_text(scan, hosts, graph) == export_text(scan, hosts, graph)
    assert exporter.export_html(scan, hosts, graph, "omega-neon") == export_html(scan, hosts, graph, "omega-neon")
