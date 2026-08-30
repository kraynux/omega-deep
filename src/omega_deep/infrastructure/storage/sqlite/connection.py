# Copyright (c) 2026 kraynux - Licence MIT
"""Ouverture d'une connexion SQLite configuree pour le projet. Identique a
omega-check (D-007) : meme raisonnement `check_same_thread=False`."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from omega_deep.infrastructure.storage.sqlite.schema import SCHEMA_STATEMENTS


def open_connection(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    connection.commit()
    return connection
