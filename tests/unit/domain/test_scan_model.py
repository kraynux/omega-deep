from omega_deep.core.enums import AnalysisMode, ScanMode, ScanStatus
from omega_deep.domain.scans.models import Scan


def test_scan_defaults_to_fixed_analysis_mode() -> None:
    scan = Scan()
    assert scan.analysis_mode == AnalysisMode.FIXED
    assert scan.scan_mode == ScanMode.PROFILE
    assert scan.status == ScanStatus.RUNNING


def test_scan_defaults_have_no_discovered_targets() -> None:
    scan = Scan()
    assert scan.discovered_targets == []
    assert scan.root_target_ip == ""
    assert scan.allowed_subnet is None


def test_scan_defaults_match_spec_guardrails() -> None:
    # OMEGA-DEEP_SPECIFICATIONS.md §2.2 : profondeur max 3, 10 cibles max par defaut.
    scan = Scan()
    assert scan.max_depth == 3
    assert scan.max_additional_targets == 10


def test_scan_deep_mode_carries_discovery_guardrails() -> None:
    scan = Scan(
        target="192.168.1.10",
        analysis_mode=AnalysisMode.DEEP,
        root_target_ip="192.168.1.10",
        discovered_targets=["192.168.1.11", "192.168.1.12"],
        max_depth=2,
        max_additional_targets=5,
        allowed_subnet="192.168.1.0/24",
    )
    assert scan.analysis_mode == AnalysisMode.DEEP
    assert scan.discovered_targets == ["192.168.1.11", "192.168.1.12"]
    assert scan.allowed_subnet == "192.168.1.0/24"
