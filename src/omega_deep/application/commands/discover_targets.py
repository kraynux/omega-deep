# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : decouvrir des cibles candidates depuis un host deja scanne
(OMEGA-DEEP_SPECIFICATIONS.md §6.2). NOUVEAU pour DEEP.

Le garde-fou de PROFONDEUR (`max_depth`) n'est PAS verifie ici : c'est a
l'appelant de ne meme pas invoquer cette fonction si `host.depth_level`
a deja atteint `max_depth` (pas de decouverte partielle a filtrer apres
coup — plus simple a auditer : "cette fonction n'a pas ete appelee" est
une preuve plus forte que "elle a ete appelee mais a tout rejete"). Le
garde-fou de NOMBRE (`max_additional_targets`) est en revanche verifie
ici, puisqu'il depend d'un compteur global du scan, pas d'un etat du host
lui-meme."""
from __future__ import annotations

from omega_deep.core.enums import PortState
from omega_deep.domain.discovery.models import DiscoveredTarget
from omega_deep.domain.discovery.service import filter_discovered_targets
from omega_deep.domain.targets.models import Host
from omega_deep.ports.discovery_prober import DiscoveryProber

_DISCOVERABLE_PROTOCOLS = ("HTTP", "HTTPS")


def discover_targets(
    *,
    host: Host,
    discovery_prober: DiscoveryProber,
    root_ip: str,
    allowed_subnet: str | None,
    current_additional_target_count: int,
    max_additional_targets: int,
    timeout: float = 2.0,
) -> list[DiscoveredTarget]:
    remaining_slots = max_additional_targets - current_additional_target_count
    if remaining_slots <= 0:
        return []

    candidates: list[DiscoveredTarget] = []
    for port in host.ports:
        if port.state != PortState.OPEN or port.service is None:
            continue
        if port.service.protocol_name not in _DISCOVERABLE_PROTOCOLS:
            continue

        use_tls = port.service.protocol_name == "HTTPS"
        candidates.extend(
            discovery_prober.probe(
                host.ip,
                port.port_number,
                host.hostname or host.ip,
                timeout,
                use_tls,
                port.service.tls_cert_san,
            )
        )

    in_scope = filter_discovered_targets(candidates, root_ip, allowed_subnet)

    # Plusieurs ports/sources peuvent reveler le meme hote : ne garder
    # qu'une occurrence (la premiere trouvee, source/confiance associees).
    deduped: dict[str, DiscoveredTarget] = {}
    for candidate in in_scope:
        deduped.setdefault(candidate.host, candidate)

    return list(deduped.values())[:remaining_slots]
