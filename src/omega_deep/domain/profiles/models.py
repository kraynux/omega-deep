# Copyright (c) 2026 kraynux - Licence MIT
"""Bounded context 'profiles' : profils de ports (systeme + utilisateur).
Identique a omega-check (OMEGA-DEEP_SPECIFICATIONS.md §3)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Profile:
    name: str
    description: str
    ports: list[int]  # tries, sans doublons, 1-65535
    pinned: bool = False
    origin: str = "system"  # "system" ou "user"
