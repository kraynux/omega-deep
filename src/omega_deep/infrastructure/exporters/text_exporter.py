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
from omega_deep.shared.i18n import _


def export_text(scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None) -> str:
    lines = [
        _("=== OMEGA-DEEP — Rapport d'analyse ==="),
        _("Scan ID    : {id}").format(id=scan.id),
        _("Cible      : {target} ({value})").format(target=scan.target, value=scan.target_ip or _("non résolue")),
        _("Date       : {created_at}").format(created_at=scan.created_at),
        _("Profil     : {value} (origine: {value2})").format(value=scan.profile_name or '-', value2=scan.profile_origin or '-'),
        _("Mode       : {value}").format(value=scan.analysis_mode.value),
        _("Statut     : {value}").format(value=scan.status.value),
        "",
    ]

    if not hosts:
        lines.append(_("Aucun résultat (scan échoué)."))
        return "\n".join(lines)

    for host in sorted(hosts, key=lambda h: h.depth_level):
        prefix = _("Cible initiale") if host.depth_level == 0 else _("Cible découverte (profondeur "
                                                                  "{depth_level})").format(depth_level=host.depth_level)
        lines.append(f"--- {prefix} : {host.ip} ---")
        if host.discovered_from:
            lines.append(_("    découverte depuis {discovered_from} via {discovery_source} "
                           "[{value}]").format(discovered_from=host.discovered_from, discovery_source=host.discovery_source, value=host.discovery_confidence.value))

        lines.append(_("{count} port(s) scanné(s) :").format(count=len(host.ports)))
        for port in sorted(host.ports, key=lambda p: p.port_number):
            lines.append(f"  - {port.port_number}/{port.protocol} : {port.state.value} [{port.state_confidence.value}]")
            service = port.service
            if service is None or not service.protocol_name:
                continue
            lines.append(_("      protocole : {protocol_name} [{value}]").format(protocol_name=service.protocol_name, value=service.protocol_confidence.value))
            if service.software:
                lines.append(
                    f"      logiciel  : {service.software} {service.version or ''} "
                    f"[{service.software_confidence.value}]".rstrip()
                )
            if service.role:
                lines.append(_("      rôle      : {role} [{value}]").format(role=service.role, value=service.role_confidence.value))
        lines.append("")

    if graph is not None and graph.edges:
        lines.append(_("=== Graphe d'architecture ==="))
        for edge in graph.edges:
            lines.append(f"  {edge.source_ip} --{edge.relation_type}--> {edge.target_ip} [{edge.confidence.value}]")

    return "\n".join(lines)
