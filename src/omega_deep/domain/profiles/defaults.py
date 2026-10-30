# Copyright (c) 2026 kraynux - Licence MIT
"""Profils systeme par defaut (voir OMEGA-DEEP_SPECIFICATIONS.md §3).
Identique a omega-check.

Lecture seule : ces profils ne sont jamais modifies par l'utilisateur
(voir domain/profiles/policies.py::ensure_name_not_reserved). Le profil
'complet' est calcule dynamiquement, pas stocke ici en dur.
"""
from __future__ import annotations

from omega_deep.domain.profiles.models import Profile
from omega_deep.domain.profiles.policies import normalize_ports
from omega_deep.shared.i18n import _

_REMOTE_DESKTOP_RANGE = list(range(5900, 5911))
_RUSTDESK_RANGE = list(range(59000, 59011))

SYSTEM_PROFILES: dict[str, Profile] = {
    "minimal": Profile(
        name="minimal",
        description=_("Scan ultra-rapide : SSH + HTTP + HTTPS"),
        ports=[22, 80, 443],
        pinned=True,
    ),
    "classic": Profile(
        name="classic",
        description=_("Services classiques Internet / LAN"),
        ports=[
            21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 123, 135, 137, 138,
            139, 143, 161, 162, 389, 443, 445, 514, 587, 636, 993, 995, 1433,
            1521, 3306, 3389, 5432, 5900, 6379, 8080, 27017,
        ],
        pinned=True,
    ),
    "web": Profile(
        name="web",
        description=_("Services web et alternatives"),
        ports=[80, 443, 8000, 8008, 8080, 8081, 8082, 8443, 8880, 8888, 9000, 9090, 9443, 10000, 10080, 10443],
        pinned=False,
    ),
    "db": Profile(
        name="db",
        description=_("Bases de données et services de données"),
        ports=[1433, 1521, 3306, 5432, 5984, 6379, 7000, 7001, 7474, 7687, 8529, 9042, 27017, 27018, 27019, 28015],
        pinned=False,
    ),
    "remote": Profile(
        name="remote",
        description=_("Accès distants (shell, bureau, RustDesk)"),
        ports=[22, 23, 3389, *_REMOTE_DESKTOP_RANGE, *_RUSTDESK_RANGE, 21114, 21115, 21116, 21117],
        pinned=False,
    ),
    "mail": Profile(
        name="mail",
        description=_("Services de messagerie"),
        ports=[25, 110, 143, 465, 587, 993, 995, 2525, 4190],
        pinned=False,
    ),
    "dns": Profile(
        name="dns",
        description=_("Services DNS"),
        ports=[53, 853, 5353],
        pinned=False,
    ),
    "iot": Profile(
        name="iot",
        description=_("Équipements IoT, caméras, box, domotique"),
        ports=[80, 443, 554, 8554, 1935, 8080, 8443, 8888, 5000, 5001, 8000, 8008, 1883, 8883, 18080],
        pinned=False,
    ),
    "dev": Profile(
        name="dev",
        description=_("Environnements de dev / lab"),
        ports=[22, 80, 443, 3000, 3306, 5432, 6379, 27017, 8000, 8008, 8080, 8443, 9000, 9090, 5601, 9200, 9300, 5672, 15672, 8161, 10000],
        pinned=False,
    ),
    "docker": Profile(
        name="docker",
        description=_("Docker, Swarm et services courants en containers"),
        ports=[2375, 2376, 2377, 4789, 7946, 80, 443, 8080, 8443, 9000, 9090, 5672, 15672, 9200, 9300, 3306, 5432, 27017, 6379, 5601, 8161],
        pinned=False,
    ),
}

RESERVED_NAMES: frozenset[str] = frozenset({*SYSTEM_PROFILES.keys(), "complet"})


def build_complete_profile() -> Profile:
    """Profil 'complet' : union triee et sans doublons de tous les profils
    systeme ci-dessus. Genere dynamiquement (jamais stocke), voir
    OMEGA-DEEP_SPECIFICATIONS.md §3."""
    all_ports: list[int] = []
    for profile in SYSTEM_PROFILES.values():
        all_ports.extend(profile.ports)

    return Profile(
        name="complet",
        description=_("TOUS les profils système (scan exhaustif, long)"),
        ports=normalize_ports(all_ports),
        pinned=False,
    )
