# Copyright (c) 2026 kraynux - Licence MIT
"""Mise en forme texte simple pour la CLI (affichage ephemere de console,
distinct de infrastructure/exporters/text_exporter.py — voir sa docstring)."""
from __future__ import annotations

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host


def format_host(host: Host) -> str:
    prefix = "cible initiale" if host.depth_level == 0 else f"cible decouverte (profondeur {host.depth_level})"
    lines = [f"[{prefix}] {host.ip} — {len(host.ports)} port(s) scanne(s) :"]
    for port in sorted(host.ports, key=lambda p: p.port_number):
        lines.append(
            f"  {port.port_number:>5}/{port.protocol} — {port.state.value:<8} [{port.state_confidence.value}]"
        )
        service = port.service
        if service is not None and service.protocol_name:
            software = f" {service.software} {service.version or ''}".rstrip() if service.software else ""
            role = f", role={service.role} [{service.role_confidence.value}]" if service.role else ""
            lines.append(f"         └─ {service.protocol_name}{software}{role}")
    return "\n".join(lines)


def format_scan_result(scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None = None) -> str:
    if not hosts:
        return f"Scan {scan.id} : ECHEC (resolution DNS impossible pour '{scan.target}')"

    lines = [f"Scan {scan.id} — cible {scan.target} ({scan.target_ip}) — mode {scan.analysis_mode.value} — statut {scan.status.value}"]
    for host in sorted(hosts, key=lambda h: h.depth_level):
        lines.append(format_host(host))

    if graph is not None and graph.edges:
        lines.append("Graphe d'architecture :")
        for edge in graph.edges:
            lines.append(f"  {edge.source_ip} --{edge.relation_type}--> {edge.target_ip} [{edge.confidence.value}]")

    return "\n".join(lines)


def format_error(message: str) -> str:
    return f"erreur : {message}"
