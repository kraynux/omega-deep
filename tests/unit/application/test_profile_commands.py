import pytest

from omega_deep.application.commands.create_profile import (
    ProfileAlreadyExistsError,
    create_profile,
)
from omega_deep.application.commands.delete_profile import delete_profile
from omega_deep.application.commands.pin_profile import pin_profile
from omega_deep.application.commands.unpin_profile import unpin_profile
from omega_deep.application.commands.update_profile import update_profile
from omega_deep.application.queries.list_profiles import get_profile, list_profiles
from omega_deep.domain.profiles.exceptions import (
    DuplicatePortsError,
    ProfileNotFoundError,
    ReservedProfileNameError,
)
from omega_deep.domain.profiles.models import Profile


class FakeProfileRepository:
    """Implemente structurellement ports/profile_repository.py::ProfileRepository
    (Protocol — pas d'heritage necessaire). Double de test en memoire."""

    def __init__(self) -> None:
        self._profiles: dict[str, Profile] = {}

    def load_user_profiles(self) -> dict[str, Profile]:
        return dict(self._profiles)

    def save_user_profiles(self, profiles: dict[str, Profile]) -> None:
        self._profiles = dict(profiles)


@pytest.fixture
def repo() -> FakeProfileRepository:
    return FakeProfileRepository()


def test_create_profile_persists_it(repo: FakeProfileRepository) -> None:
    created = create_profile(repo, "labo", "Profil de labo", [22, 8080])
    assert created.origin == "user"
    assert repo.load_user_profiles()["labo"].ports == [22, 8080]


def test_create_profile_rejects_reserved_name(repo: FakeProfileRepository) -> None:
    with pytest.raises(ReservedProfileNameError):
        create_profile(repo, "minimal", "essai", [22])


def test_create_profile_rejects_duplicate_name(repo: FakeProfileRepository) -> None:
    create_profile(repo, "labo", "d1", [22])
    with pytest.raises(ProfileAlreadyExistsError):
        create_profile(repo, "labo", "d2", [80])


def test_create_profile_rejects_invalid_ports(repo: FakeProfileRepository) -> None:
    with pytest.raises(DuplicatePortsError):
        create_profile(repo, "labo", "d1", [22, 22])


def test_update_profile_changes_ports_and_description(repo: FakeProfileRepository) -> None:
    create_profile(repo, "labo", "avant", [22])
    updated = update_profile(repo, "labo", description="apres", ports=[22, 80])
    assert updated.description == "apres"
    assert updated.ports == [22, 80]


def test_update_profile_missing_raises(repo: FakeProfileRepository) -> None:
    with pytest.raises(ProfileNotFoundError):
        update_profile(repo, "inexistant", description="x")


def test_delete_profile_removes_it(repo: FakeProfileRepository) -> None:
    create_profile(repo, "labo", "d", [22])
    delete_profile(repo, "labo")
    assert "labo" not in repo.load_user_profiles()


def test_delete_profile_missing_raises(repo: FakeProfileRepository) -> None:
    with pytest.raises(ProfileNotFoundError):
        delete_profile(repo, "inexistant")


def test_pin_then_unpin_profile(repo: FakeProfileRepository) -> None:
    create_profile(repo, "labo", "d", [22], pinned=False)
    pinned = pin_profile(repo, "labo")
    assert pinned.pinned is True
    unpinned = unpin_profile(repo, "labo")
    assert unpinned.pinned is False


def test_list_profiles_merges_system_and_user(repo: FakeProfileRepository) -> None:
    create_profile(repo, "labo", "d", [22])
    merged = list_profiles(repo)
    assert "labo" in merged
    assert "minimal" in merged
    assert "complet" in merged


def test_system_profile_wins_on_name_collision(repo: FakeProfileRepository) -> None:
    # Ne peut pas arriver via create_profile (nom reserve bloque en amont),
    # mais on verifie quand meme la regle de priorite du merge lui-meme.
    repo.save_user_profiles({"minimal": Profile(name="minimal", description="faux", ports=[1])})
    merged = list_profiles(repo)
    assert merged["minimal"].description == "Scan ultra-rapide : SSH + HTTP + HTTPS"


def test_get_profile_found_and_missing(repo: FakeProfileRepository) -> None:
    assert get_profile(repo, "minimal").name == "minimal"
    with pytest.raises(ProfileNotFoundError):
        get_profile(repo, "inexistant")
