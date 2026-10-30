# Copyright (c) 2026 kraynux - Licence MIT
"""Tableau des cibles decouvertes en attente de validation
(screens/target_validation.py). NOUVEAU pour DEEP : remplace les prompts
`input()` de interfaces/cli/commands/analyze_command.py::_decide par un
ecran interactif — meme regle fail-safe (D-003) : la colonne Decision
demarre a REJETER pour toutes les lignes, une acceptation est toujours un
geste explicite de l'utilisateur, jamais une valeur par defaut."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_deep.domain.discovery.models import DiscoveredTarget
from omega_deep.shared.i18n import _

_REJECT_LABEL = _("REJETER")
_ACCEPT_LABEL = _("ACCEPTER")
_DECISION_COLUMN_KEY = "decision"


class DiscoveryTable(DataTable[str]):
    """Une ligne par cible proposee. `decisions` (host -> bool) refletee
    en temps reel dans la colonne Decision au fil des bascules."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns(
            (_("Cible"), "target"),
            (_("Source"), "source"),
            (_("Confiance"), "confidence"),
            (_("Découvert depuis"), "discovered_from"),
            (_("Décision"), _DECISION_COLUMN_KEY),
        )

    def set_targets(self, targets: list[DiscoveredTarget], decisions: dict[str, bool]) -> None:
        self.clear()
        for target in targets:
            self.add_row(
                target.host,
                target.source,
                target.confidence.value,
                target.discovered_from,
                _ACCEPT_LABEL if decisions.get(target.host, False) else _REJECT_LABEL,
                key=target.host,
            )

    def refresh_decision(self, host: str, accepted: bool) -> None:
        self.update_cell(host, _DECISION_COLUMN_KEY, _ACCEPT_LABEL if accepted else _REJECT_LABEL)
