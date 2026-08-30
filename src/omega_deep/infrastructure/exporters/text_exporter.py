# Copyright (c) 2026 kraynux - Licence MIT
"""Export TXT (rapport, avec graphe ASCII simple — liste des relations,
pas un rendu de graphe dessine : suffisant pour un rapport texte, un vrai
rendu visuel restant le travail de l'export HTML). Distinct de
interfaces/cli/formatters/text_formatter.py (affichage ephemere de
console, plus compact) — les deux ont vocation a diverger."""
from __future__ import annotations

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host


def export_text(scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None) -> str:
    lines = [
        "=== OMEGA-DEEP — Rapport d'analyse ===",
        f"Scan ID    : {scan.id}",
        f"Cible      : {scan.target} ({scan.target_ip or 'non resolue'})",
        f"Date       : {scan.created_at}",
        f"Profil     : {scan.profile_name or '-'} (origine: {scan.profile_origin or '-'})",
        f"Mode       : {scan.analysis_mode.value}",
        f"Statut     : {scan.status.value}",
        "",
    ]

    if not hosts:
        lines.append("Aucun resultat (scan echoue).")
        return "\n".join(lines)

    for host in sorted(hosts, key=lambda h: h.depth_level):
        prefix = "Cible initiale" if host.depth_level == 0 else f"Cible decouverte (profondeur {host.depth_level})"
        lines.append(f"--- {prefix} : {host.ip} ---")
        if host.discovered_from:
            lines.append(f"    decouverte depuis {host.discovered_from} via {host.discovery_source} [{host.discovery_confidence.value}]")

        lines.append(f"{len(host.ports)} port(s) scanne(s) :")
        for port in sorted(host.ports, key=lambda p: p.port_number):
            lines.append(f"  - {port.port_number}/{port.protocol} : {port.state.value} [{port.state_confidence.value}]")
            service = port.service
            if service is None or not service.protocol_name:
                continue
            lines.append(f"      protocole : {service.protocol_name} [{service.protocol_confidence.value}]")
            if service.software:
                lines.append(
                    f"      logiciel  : {service.software} {service.version or ''} "
                    f"[{service.software_confidence.value}]".rstrip()
                )
            if service.role:
                lines.append(f"      role      : {service.role} [{service.role_confidence.value}]")
        lines.append("")

    if graph is not None and graph.edges:
        lines.append("=== Graphe d'architecture ===")
        for edge in graph.edges:
            lines.append(f"  {edge.source_ip} --{edge.relation_type}--> {edge.target_ip} [{edge.confidence.value}]")

    return "\n".join(lines)
