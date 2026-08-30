from pathlib import Path

from omega_deep.domain.profiles.models import Profile
from omega_deep.infrastructure.storage.files.json_profile_store import JsonProfileStore


def test_load_returns_empty_dict_when_file_missing(tmp_path: Path) -> None:
    store = JsonProfileStore(tmp_path / "user_profiles.json")
    assert store.load_user_profiles() == {}


def test_save_then_load_round_trips(tmp_path: Path) -> None:
    store = JsonProfileStore(tmp_path / "sub" / "user_profiles.json")
    profiles = {
        "labo": Profile(name="labo", description="Profil de labo", ports=[22, 8080], pinned=True, origin="user"),
    }
    store.save_user_profiles(profiles)

    reloaded = store.load_user_profiles()
    assert reloaded["labo"] == profiles["labo"]


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    target = tmp_path / "does" / "not" / "exist" / "user_profiles.json"
    store = JsonProfileStore(target)
    store.save_user_profiles({})
    assert target.exists()
