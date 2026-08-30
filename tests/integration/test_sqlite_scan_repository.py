from collections.abc import Iterator
from pathlib import Path

import pytest

from omega_deep.core.enums import AnalysisMode, ConfidenceLevel, PortState, ScanMode, ScanStatus
from omega_deep.domain.architecture.models import ArchitectureEdge, ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.services.models import Port, RoleElement, Service, TransportLayer
from omega_deep.domain.targets.models import Host
from omega_deep.infrastructure.storage.sqlite.connection import open_connection
from omega_deep.infrastructure.storage.sqlite.scan_repository import SqliteScanRepository


@pytest.fixture
def repo(tmp_path: Path) -> Iterator[SqliteScanRepository]:
    connection = open_connection(tmp_path / "omega-deep.db")
    try:
        yield SqliteScanRepository(connection)
    finally:
        connection.close()


def _make_scan(**overrides: object) -> Scan:
    defaults: dict[str, object] = {
        "id": "scan-1",
        "created_at": "2026-08-28T00:00:00+00:00",
        "target": "192.168.1.10",
        "target_ip": "192.168.1.10",
        "profile_name": "minimal",
        "profile_origin": "system",
        "ports_scanned": [22, 80, 443],
        "scan_mode": ScanMode.PROFILE,
        "status": ScanStatus.COMPLETED,
    }
    defaults.update(overrides)
    return Scan(**defaults)  # type: ignore[arg-type]


def test_save_and_get_round_trips(repo: SqliteScanRepository) -> None:
    scan = _make_scan()
    repo.save(scan)

    fetched = repo.get("scan-1")
    assert fetched == scan


def test_save_and_get_round_trips_deep_fields(repo: SqliteScanRepository) -> None:
    scan = _make_scan(
        id="scan-deep-1",
        analysis_mode=AnalysisMode.DEEP,
        root_target_ip="192.168.1.10",
        discovered_targets=["192.168.1.11", "192.168.1.12"],
        max_depth=2,
        max_additional_targets=5,
        allowed_subnet="192.168.1.0/24",
    )
    repo.save(scan)

    fetched = repo.get("scan-deep-1")
    assert fetched == scan


def test_get_missing_returns_none(repo: SqliteScanRepository) -> None:
    assert repo.get("inexistant") is None


def test_list_history_ordered_and_filtered_by_target(repo: SqliteScanRepository) -> None:
    repo.save(_make_scan(id="a", target="host-a", created_at="2026-08-28T00:00:00+00:00"))
    repo.save(_make_scan(id="b", target="host-b", created_at="2026-08-28T01:00:00+00:00"))
    repo.save(_make_scan(id="c", target="host-a", created_at="2026-08-28T02:00:00+00:00"))

    all_history = repo.list_history()
    assert [s.id for s in all_history] == ["c", "b", "a"]

    host_a_history = repo.list_history(target="host-a")
    assert [s.id for s in host_a_history] == ["c", "a"]


def test_clear_removes_everything(repo: SqliteScanRepository) -> None:
    repo.save(_make_scan())
    repo.save_hosts("scan-1", [Host(ip="192.168.1.10")])
    repo.save_graph("scan-1", ArchitectureGraph(nodes=["192.168.1.10"], root_node="192.168.1.10"))
    repo.clear()
    assert repo.list_history() == ()
    assert repo.get_hosts("scan-1") == ()
    assert repo.get_graph("scan-1") is None


def _make_host_with_full_service(ip: str = "192.168.1.10", depth_level: int = 0) -> Host:
    service = Service(
        protocol_name="HTTPS",
        protocol_confidence=ConfidenceLevel.VERIFIED,
        software="nginx",
        software_confidence=ConfidenceLevel.DECLARED,
        version="1.25.3",
        version_confidence=ConfidenceLevel.DECLARED,
        role="reverse proxy",
        role_confidence=ConfidenceLevel.CORROBORATED,
        role_chain=[
            RoleElement(role="reverse proxy", software="NGINX", confidence=ConfidenceLevel.CORROBORATED),
            RoleElement(role="backend", software="Lighttpd", confidence=ConfidenceLevel.INFERRED),
        ],
        auth_required=True,
        auth_required_confidence=ConfidenceLevel.VERIFIED,
        auth_types=["Basic"],
        auth_types_confidence=ConfidenceLevel.VERIFIED,
        auth_details={"realm": "admin"},
        waf_present=True,
        waf_name_guess="Cloudflare",
        waf_confidence=ConfidenceLevel.DECLARED,
        tls_version="TLSv1.3",
        tls_version_confidence=ConfidenceLevel.VERIFIED,
        tls_cipher="TLS_AES_256_GCM_SHA384",
        tls_cipher_confidence=ConfidenceLevel.VERIFIED,
        tls_cert_subject="example.com",
        tls_cert_issuer="Let's Encrypt",
        tls_cert_san=["DNS:example.com", "DNS:www.example.com"],
        encapsulation_layers=[
            TransportLayer(order=0, layer_type="transport", protocol="tcp"),
            TransportLayer(order=1, layer_type="security", protocol="tls", version="1.3"),
        ],
        evidence=["HTTP 200 OK", "handshake TLS reussi : TLSv1.3"],
    )
    port_with_service = Port(
        port_number=443, protocol="tcp", state=PortState.OPEN,
        state_confidence=ConfidenceLevel.VERIFIED, evidence=["connexion TCP etablie"], service=service,
    )
    port_without_service = Port(port_number=80, protocol="tcp", state=PortState.CLOSED, state_confidence=ConfidenceLevel.VERIFIED)
    return Host(ip=ip, hostname="example.com", ports=[port_with_service, port_without_service], depth_level=depth_level)


def test_save_and_get_hosts_round_trips_full_aggregate(repo: SqliteScanRepository) -> None:
    repo.save(_make_scan(id="scan-host-1"))

    host = _make_host_with_full_service()
    repo.save_hosts("scan-host-1", [host])

    fetched = repo.get_hosts("scan-host-1")
    assert fetched == (host,)


def test_get_hosts_missing_returns_empty_tuple(repo: SqliteScanRepository) -> None:
    assert repo.get_hosts("inexistant") == ()


def test_save_hosts_replaces_previous_hosts_for_same_scan(repo: SqliteScanRepository) -> None:
    repo.save(_make_scan(id="scan-host-2"))

    repo.save_hosts("scan-host-2", [Host(ip="10.0.0.1", ports=[])])
    repo.save_hosts("scan-host-2", [Host(ip="10.0.0.2", ports=[])])

    fetched = repo.get_hosts("scan-host-2")
    assert [h.ip for h in fetched] == ["10.0.0.2"]


def test_save_hosts_multi_host_deep_analysis_ordered_by_depth(repo: SqliteScanRepository) -> None:
    repo.save(_make_scan(id="scan-deep-multi", analysis_mode=AnalysisMode.DEEP))

    child = Host(
        ip="192.168.1.11", ports=[], depth_level=1, discovered_from="192.168.1.10",
        discovery_source="header", discovery_confidence=ConfidenceLevel.DECLARED,
    )
    root = _make_host_with_full_service(ip="192.168.1.10", depth_level=0)
    repo.save_hosts("scan-deep-multi", [root, child])

    fetched = repo.get_hosts("scan-deep-multi")
    assert [h.ip for h in fetched] == ["192.168.1.10", "192.168.1.11"]  # racine d'abord
    assert fetched[1].discovered_from == "192.168.1.10"
    assert fetched[1].discovery_source == "header"
    assert fetched[1].discovery_confidence == ConfidenceLevel.DECLARED


def test_save_and_get_graph_round_trips(repo: SqliteScanRepository) -> None:
    repo.save(_make_scan(id="scan-graph-1"))
    graph = ArchitectureGraph(
        nodes=["192.168.1.10", "192.168.1.11"],
        edges=[
            ArchitectureEdge(
                source_ip="192.168.1.10", target_ip="192.168.1.11", relation_type="proxy_to",
                confidence=ConfidenceLevel.DECLARED, evidence=["decouvert via header"],
            )
        ],
        root_node="192.168.1.10",
    )

    repo.save_graph("scan-graph-1", graph)

    fetched = repo.get_graph("scan-graph-1")
    assert fetched == graph


def test_get_graph_missing_returns_none(repo: SqliteScanRepository) -> None:
    assert repo.get_graph("inexistant") is None


def test_save_graph_replaces_previous_graph_for_same_scan(repo: SqliteScanRepository) -> None:
    repo.save(_make_scan(id="scan-graph-2"))
    repo.save_graph("scan-graph-2", ArchitectureGraph(nodes=["a"], root_node="a"))
    repo.save_graph("scan-graph-2", ArchitectureGraph(nodes=["b"], root_node="b"))

    fetched = repo.get_graph("scan-graph-2")
    assert fetched is not None
    assert fetched.root_node == "b"
