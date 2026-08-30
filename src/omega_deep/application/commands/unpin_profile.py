# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : desepingler un profil utilisateur (voir pin_profile.py pour
la note sur le perimetre profils systeme vs utilisateur). Identique a
omega-check."""
from __future__ import annotations

from omega_deep.domain.profiles.exceptions import ProfileNotFoundError
from omega_deep.domain.profiles.models import Profile
from omega_deep.ports.profile_repository import ProfileRepository


def unpin_profile(repo: ProfileRepository, name: str) -> Profile:
    existing = repo.load_user_profiles()
    profile = existing.get(name)
    if profile is None:
        raise ProfileNotFoundError(name)

    profile.pinned = False
    repo.save_user_profiles(existing)
    return profile
