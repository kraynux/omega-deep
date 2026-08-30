# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : supprimer un profil utilisateur. Identique a omega-check."""
from __future__ import annotations

from omega_deep.domain.profiles.exceptions import ProfileNotFoundError
from omega_deep.ports.profile_repository import ProfileRepository


def delete_profile(repo: ProfileRepository, name: str) -> None:
    existing = repo.load_user_profiles()
    if name not in existing:
        raise ProfileNotFoundError(name)

    del existing[name]
    repo.save_user_profiles(existing)
