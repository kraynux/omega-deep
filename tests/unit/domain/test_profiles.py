import pytest

from omega_deep.domain.profiles.defaults import (
    RESERVED_NAMES,
    SYSTEM_PROFILES,
    build_complete_profile,
)
from omega_deep.domain.profiles.exceptions import (
    DuplicatePortsError,
    InvalidPortError,
    ReservedProfileNameError,
)
from omega_deep.domain.profiles.policies import (
    ensure_name_not_reserved,
    normalize_ports,
    parse_port_spec,
    validate_ports,
)


def test_validate_ports_accepts_valid_list() -> None:
    validate_ports([1, 80, 443, 65535])  # ne doit pas lever


def test_validate_ports_rejects_out_of_range() -> None:
    with pytest.raises(InvalidPortError):
        validate_ports([0])
    with pytest.raises(InvalidPortError):
        validate_ports([65536])


def test_validate_ports_rejects_duplicates() -> None:
    with pytest.raises(DuplicatePortsError):
        validate_ports([80, 443, 80])


def test_normalize_ports_sorts_and_dedupes() -> None:
    assert normalize_ports([443, 80, 80, 22]) == [22, 80, 443]


def test_ensure_name_not_reserved_rejects_system_names() -> None:
    with pytest.raises(ReservedProfileNameError):
        ensure_name_not_reserved("minimal", RESERVED_NAMES)


def test_ensure_name_not_reserved_accepts_free_name() -> None:
    ensure_name_not_reserved("mon-profil", RESERVED_NAMES)  # ne doit pas lever


def test_all_system_profiles_have_valid_ports() -> None:
    for profile in SYSTEM_PROFILES.values():
        validate_ports(profile.ports)


def test_minimal_and_classic_are_pinned_others_are_not() -> None:
    assert SYSTEM_PROFILES["minimal"].pinned is True
    assert SYSTEM_PROFILES["classic"].pinned is True
    assert SYSTEM_PROFILES["web"].pinned is False


def test_complete_profile_is_union_of_all_system_profiles() -> None:
    complete = build_complete_profile()
    expected = normalize_ports(
        [port for profile in SYSTEM_PROFILES.values() for port in profile.ports]
    )
    assert complete.ports == expected
    assert complete.name == "complet"
    # Un port present dans plusieurs profils (ex: 80) ne doit apparaitre qu'une fois.
    assert complete.ports.count(80) == 1


def test_reserved_names_include_complet_even_though_it_has_no_dict_entry() -> None:
    assert "complet" in RESERVED_NAMES
    assert "complet" not in SYSTEM_PROFILES


def test_parse_port_spec_single_port() -> None:
    assert parse_port_spec("80") == [80]


def test_parse_port_spec_comma_separated_list() -> None:
    assert parse_port_spec("22,443,8080") == [22, 443, 8080]


def test_parse_port_spec_range() -> None:
    assert parse_port_spec("1000-1002") == [1000, 1001, 1002]


def test_parse_port_spec_combination_sorts() -> None:
    assert parse_port_spec("80,22,1000-1002") == [22, 80, 1000, 1001, 1002]


def test_parse_port_spec_rejects_duplicates_same_as_saved_profiles() -> None:
    with pytest.raises(DuplicatePortsError):
        parse_port_spec("22,80,22")


def test_parse_port_spec_ignores_surrounding_whitespace() -> None:
    assert parse_port_spec(" 22 , 443 ") == [22, 443]


def test_parse_port_spec_rejects_out_of_range_port() -> None:
    with pytest.raises(InvalidPortError):
        parse_port_spec("70000")


def test_parse_port_spec_rejects_non_numeric_token() -> None:
    with pytest.raises(ValueError):
        parse_port_spec("abc")
