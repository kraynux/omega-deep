import pytest

from omega_deep.application.queries.compare_scans import compare_scans
from omega_deep.application.queries.get_scan_details import get_scan_details
from omega_deep.core.enums import ConfidenceLevel, PortState, ScanMode, ScanStatus
from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.exceptions import ScanNotFoundError
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.services.models import Port
from omega_deep.domain.targets.models import Host


class FakeScanRepository:
    def __init__(self) -> None:
        self.scans: dict[str, Scan] = {}
        self.hosts: dict[str, tuple[Host, ...]] = {}
        self.graphs: dict[str, ArchitectureGraph] = {}

    def save(self, scan: Scan) -> None:
        self.scans[scan.id] = scan  # type: ignore[index]

    def get(self, scan_id: str) -> Scan | None:
        return self.scans.get(scan_id)

    def list_history(self, *, target: str | None = None, limit: int = 50) -> tuple[Scan, ...]:
        return tuple(self.scans.values())

    def clear(self) -> None:
        self.scans.clear()

    def save_hosts(self, scan_id: str, hosts: list[Host]) -> None:
        self.hosts[scan_id] = tuple(hosts)

    def get_hosts(self, scan_id: str) -> tuple[Host, ...]:
        return self.hosts.get(scan_id, ())

    def save_graph(self, scan_id: str, graph: ArchitectureGraph) -> None:
        self.graphs[scan_id] = graph

    def get_graph(self, scan_id: str) -> ArchitectureGraph | None:
        return self.graphs.get(scan_id)


def _scan(scan_id: str, target_ip: str = "10.0.0.1") -> Scan:
    return Scan(id=scan_id, created_at="2026-08-30T00:00:00+00:00", target=target_ip, target_ip=target_ip,
                scan_mode=ScanMode.PROFILE, status=ScanStatus.COMPLETED)


def _port(number: int, state: PortState) -> Port:
    return Port(port_number=number, protocol="tcp", state=state, state_confidence=ConfidenceLevel.VERIFIED)


def test_get_scan_details_returns_scan_hosts_and_graph() -> None:
    repo = FakeScanRepository()
    scan = _scan("scan-1")
    repo.save(scan)
    host = Host(ip="10.0.0.1", ports=[_port(80, PortState.OPEN)])
    repo.save_hosts("scan-1", [host])
    graph = ArchitectureGraph(nodes=["10.0.0.1"], root_node="10.0.0.1")
    repo.save_graph("scan-1", graph)

    fetched_scan, hosts, fetched_graph = get_scan_details(repo, "scan-1")

    assert fetched_scan == scan
    assert hosts == (host,)
    assert fetched_graph == graph


def test_get_scan_details_missing_raises() -> None:
    repo = FakeScanRepository()
    with pytest.raises(ScanNotFoundError):
        get_scan_details(repo, "inexistant")


def test_get_scan_details_without_graph_returns_none() -> None:
    repo = FakeScanRepository()
    repo.save(_scan("scan-2"))
    _, _, graph = get_scan_details(repo, "scan-2")
    assert graph is None


def test_compare_scans_compares_root_hosts() -> None:
    repo = FakeScanRepository()
    repo.save(_scan("scan-a"))
    repo.save(_scan("scan-b"))
    repo.save_hosts("scan-a", [Host(ip="10.0.0.1", ports=[_port(80, PortState.OPEN)])])
    repo.save_hosts("scan-b", [Host(ip="10.0.0.1", ports=[_port(80, PortState.CLOSED)])])

    comparison = compare_scans(repo, "scan-a", "scan-b")

    assert len(comparison.state_changes) == 1
    assert comparison.state_changes[0].state_a == PortState.OPEN
    assert comparison.state_changes[0].state_b == PortState.CLOSED


def test_compare_scans_ignores_discovered_hosts_beyond_root() -> None:
    repo = FakeScanRepository()
    repo.save(_scan("scan-a"))
    repo.save(_scan("scan-b"))
    root_a = Host(ip="10.0.0.1", ports=[_port(80, PortState.OPEN)], depth_level=0)
    child_a = Host(ip="10.0.0.2", ports=[_port(22, PortState.OPEN)], depth_level=1)
    repo.save_hosts("scan-a", [root_a, child_a])
    repo.save_hosts("scan-b", [Host(ip="10.0.0.1", ports=[_port(80, PortState.OPEN)], depth_level=0)])

    comparison = compare_scans(repo, "scan-a", "scan-b")

    assert comparison.state_changes == []
    assert comparison.ports_only_in_a == []
