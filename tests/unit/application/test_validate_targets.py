from omega_deep.application.commands.validate_targets import validate_targets
from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.discovery.models import DiscoveredTarget, DiscoveryState


def _target(host: str) -> DiscoveredTarget:
    return DiscoveredTarget(
        host=host, source="header", confidence=ConfidenceLevel.DECLARED,
        discovered_from="192.168.1.10", state=DiscoveryState.PRESENTED,
    )


def test_explicitly_accepted_target_becomes_accepted() -> None:
    presented = [_target("192.168.1.11")]
    result = validate_targets(presented, {"192.168.1.11": True})
    assert result[0].state == DiscoveryState.ACCEPTED


def test_explicitly_rejected_target_becomes_rejected() -> None:
    presented = [_target("192.168.1.11")]
    result = validate_targets(presented, {"192.168.1.11": False})
    assert result[0].state == DiscoveryState.REJECTED


def test_target_absent_from_decisions_is_rejected_fail_safe() -> None:
    # Simule un oubli/fermeture d'ecran/timeout : le silence n'est jamais
    # une acceptation (D-003).
    presented = [_target("192.168.1.11")]
    result = validate_targets(presented, {})
    assert result[0].state == DiscoveryState.REJECTED


def test_does_not_mutate_input_targets() -> None:
    original = _target("192.168.1.11")
    validate_targets([original], {"192.168.1.11": True})
    assert original.state == DiscoveryState.PRESENTED  # inchange


def test_multiple_targets_decided_independently() -> None:
    presented = [_target("192.168.1.11"), _target("192.168.1.12"), _target("192.168.1.13")]
    result = validate_targets(presented, {"192.168.1.11": True, "192.168.1.12": False})

    states = {t.host: t.state for t in result}
    assert states["192.168.1.11"] == DiscoveryState.ACCEPTED
    assert states["192.168.1.12"] == DiscoveryState.REJECTED
    assert states["192.168.1.13"] == DiscoveryState.REJECTED  # absent -> fail-safe
