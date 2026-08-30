# Copyright (c) 2026 kraynux - Licence MIT
"""Use case (lecture pure) : construire un nom de fichier d'export explicite
et horodate ('analyse-profil-date', 'analyse-custom-date', 'analyse'),
meme convention que omega-check/build_export_filename.py."""
from __future__ import annotations

from datetime import datetime

from omega_deep.domain.scans.models import Scan

_EXTENSIONS = {"json": "json", "text": "txt", "html": "html"}


def build_export_filename(scan: Scan, fmt: str) -> str:
    date_str = datetime.fromisoformat(scan.created_at).strftime("%Y%m%d-%H%M%S")

    if scan.profile_name is None:
        stem = "analyse"
    elif scan.profile_origin == "user":
        stem = "analyse-custom"
    else:
        stem = f"analyse-{scan.profile_name}"

    return f"{stem}-{date_str}.{_EXTENSIONS[fmt]}"
