# Copyright (c) 2026 kraynux - Licence MIT
"""Use cases de lecture : lister/recuperer les profils (systeme +
utilisateur). Identique a omega-check."""
from __future__ import annotations

from omega_deep.domain.profiles.defaults import SYSTEM_PROFILES, build_complete_profile
from omega_deep.domain.profiles.exceptions import ProfileNotFoundError
from omega_deep.domain.profiles.models import Profile
from omega_deep.ports.profile_repository import ProfileRepository


def list_profiles(repo: ProfileRepository) -> dict[str, Profile]:
    """Fusionne profils systeme (+ 'complet', genere a la volee) et profils
    utilisateur. En cas de collision de nom (ne devrait jamais arriver,
    les noms systeme sont reserves — voir policies.ensure_name_not_reserved),
    le profil systeme l'emporte."""
    merged: dict[str, Profile] = dict(repo.load_user_profiles())
    merged.update(SYSTEM_PROFILES)
    merged["complet"] = build_complete_profile()
    return merged


def get_profile(repo: ProfileRepository, name: str) -> Profile:
    profile = list_profiles(repo).get(name)
    if profile is None:
        raise ProfileNotFoundError(name)
    return profile
