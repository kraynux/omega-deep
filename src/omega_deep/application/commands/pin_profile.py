# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : epingler un profil utilisateur. Identique a omega-check.

Les profils systeme ont leur `pinned` fixe a la definition (voir
domain/profiles/defaults.py) et ne sont pas concernes par ce use case —
seuls les profils utilisateur sont persistes, donc seuls eux peuvent
changer d'etat apres coup.
"""
from __future__ import annotations

from omega_deep.domain.profiles.exceptions import ProfileNotFoundError
from omega_deep.domain.profiles.models import Profile
from omega_deep.ports.profile_repository import ProfileRepository


def pin_profile(repo: ProfileRepository, name: str) -> Profile:
    existing = repo.load_user_profiles()
    profile = existing.get(name)
    if profile is None:
        raise ProfileNotFoundError(name)

    profile.pinned = True
    repo.save_user_profiles(existing)
    return profile
