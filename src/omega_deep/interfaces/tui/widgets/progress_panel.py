# Copyright (c) 2026 kraynux - Licence MIT
"""Indicateur de progression indetermine, avec le detail des operations en
cours. Porte verbatim depuis omega-scan/omega-stress/omega-check
(D-007/D-008)."""
from __future__ import annotations

from textual.containers import Middle
from textual.widgets import LoadingIndicator, RichLog, Static


class ProgressPanel(Middle):
    """Ecran d'attente pendant l'execution d'une analyse."""

    def __init__(self, *, message: str) -> None:
        super().__init__(
            Static(message, classes="omega-subtitle"),
            LoadingIndicator(),
            RichLog(classes="omega-progress-log", max_lines=200, auto_scroll=True, markup=False),
            classes="omega-progress-panel",
        )

    def write_line(self, line: str) -> None:
        self.query_one(RichLog).write(line)
