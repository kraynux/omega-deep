from omega_deep.domain.discovery.policies import (
    is_additional_target_count_allowed,
    is_depth_allowed,
    is_within_allowed_scope,
)


def test_candidate_in_same_private_subnet_as_root_is_allowed() -> None:
    assert is_within_allowed_scope("192.168.1.11", root_ip="192.168.1.10") is True


def test_candidate_outside_root_subnet_is_rejected() -> None:
    assert is_within_allowed_scope("192.168.2.11", root_ip="192.168.1.10") is False


def test_public_candidate_is_rejected_without_explicit_subnet() -> None:
    assert is_within_allowed_scope("8.8.8.8", root_ip="192.168.1.10") is False


def test_explicit_subnet_allows_public_ip_as_configured() -> None:
    # "configuration explicite" (spec §4.2) : le garde-fou d'exclusion des
    # IPs publiques ne s'applique plus si l'utilisateur a fourni un subnet.
    assert is_within_allowed_scope("8.8.8.8", root_ip="192.168.1.10", allowed_subnet="8.8.8.0/24") is True


def test_explicit_subnet_rejects_candidate_outside_it() -> None:
    assert is_within_allowed_scope("192.168.1.11", root_ip="192.168.1.10", allowed_subnet="8.8.8.0/24") is False


def test_unresolved_hostname_candidate_is_rejected_fail_safe() -> None:
    assert is_within_allowed_scope("backend.internal", root_ip="192.168.1.10") is False


def test_invalid_root_ip_is_rejected() -> None:
    assert is_within_allowed_scope("192.168.1.11", root_ip="not-an-ip") is False


def test_is_depth_allowed() -> None:
    assert is_depth_allowed(current_depth=2, max_depth=3) is True
    assert is_depth_allowed(current_depth=3, max_depth=3) is False


def test_is_additional_target_count_allowed() -> None:
    assert is_additional_target_count_allowed(current_count=9, max_additional_targets=10) is True
    assert is_additional_target_count_allowed(current_count=10, max_additional_targets=10) is False
