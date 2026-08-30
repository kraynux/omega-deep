# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : valider (accepter/refuser) les cibles decouvertes, cible par
cible (OMEGA-DEEP_SPECIFICATIONS.md §6.2, machine a etats detaillee en
D-003). NOUVEAU pour DEEP — le point le plus sensible du projet.

Regle fail-safe : toute cible ABSENTE de `decisions` (jamais explicitement
tranchee par l'utilisateur — oubli, fermeture d'ecran, interruption,
timeout) est REJETEE par defaut. Le silence n'est jamais une acceptation.
`--auto-validate` (deconseille, avec avertissement) reste une decision
d'interface (CLI, phase ulterieure) qui construit `decisions` en acceptant
tout — cette fonction elle-meme ne connait aucun mode "tout accepter"."""
from __future__ import annotations

from dataclasses import replace

from omega_deep.domain.discovery.models import DiscoveredTarget, DiscoveryState


def validate_targets(
    presented: list[DiscoveredTarget], decisions: dict[str, bool]
) -> list[DiscoveredTarget]:
    """`decisions` : host -> True (accepte) / False (refuse). Une cible
    absente de ce dict est traitee comme False (voir regle fail-safe
    ci-dessus). Ne mute jamais les objets d'entree (`dataclasses.replace`)."""
    validated: list[DiscoveredTarget] = []
    for target in presented:
        accepted = decisions.get(target.host, False)
        new_state = DiscoveryState.ACCEPTED if accepted else DiscoveryState.REJECTED
        validated.append(replace(target, state=new_state))
    return validated
