# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation SQLite du port ScanRepository (ports/scan_repository.py).

Difference cle avec omega-check : `save_hosts`/`get_hosts` (pluriel — un
scan DEEP associe plusieurs hosts au meme scan_id, racine + cibles
acceptees) au lieu de `save_host`/`get_host` (singulier), et
`save_graph`/`get_graph` pour la nouvelle table `architecture_graph`.
Les champs riches de Service (role_chain, encapsulation_layers) restent
serialises en JSON via dataclasses.asdict — ConfidenceLevel etant un
str-Enum, json.dumps le rend directement sous sa valeur texte."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from typing import Any

from omega_lib.shared.ids import new_id

from omega_deep.core.enums import AnalysisMode, ConfidenceLevel, PortState, ScanMode, ScanStatus
from omega_deep.domain.architecture.models import ArchitectureEdge, ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.services.models import Port, RoleElement, Service, TransportLayer
from omega_deep.domain.targets.models import Host
from omega_deep.infrastructure.exceptions import StorageError


class SqliteScanRepository:
    """Implemente ports/scan_repository.py::ScanRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    # --- scans --------------------------------------------------------

    def save(self, scan: Scan) -> None:
        try:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO scans
                    (id, created_at, tool, target, target_ip, profile_name,
                     profile_origin, ports_scanned, scan_mode, status,
                     analysis_mode, root_target_ip, discovered_targets,
                     max_depth, max_additional_targets, allowed_subnet)
                VALUES (?, ?, 'deep', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan.id,
                    scan.created_at,
                    scan.target,
                    scan.target_ip,
                    scan.profile_name,
                    scan.profile_origin,
                    json.dumps(scan.ports_scanned),
                    scan.scan_mode.value,
                    scan.status.value,
                    scan.analysis_mode.value,
                    scan.root_target_ip,
                    json.dumps(scan.discovered_targets),
                    scan.max_depth,
                    scan.max_additional_targets,
                    scan.allowed_subnet,
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"echec de sauvegarde du scan {scan.id!r}") from exc

    def get(self, scan_id: str) -> Scan | None:
        row = self._connection.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        return self._row_to_scan(row) if row is not None else None

    def list_history(self, *, target: str | None = None, limit: int = 50) -> tuple[Scan, ...]:
        if target is not None:
            rows = self._connection.execute(
                "SELECT * FROM scans WHERE target = ? ORDER BY created_at DESC LIMIT ?", (target, limit)
            ).fetchall()
        else:
            rows = self._connection.execute(
                "SELECT * FROM scans ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return tuple(self._row_to_scan(row) for row in rows)

    def clear(self) -> None:
        self._connection.execute("DELETE FROM architecture_graph")
        self._connection.execute("DELETE FROM services")
        self._connection.execute("DELETE FROM ports")
        self._connection.execute("DELETE FROM hosts")
        self._connection.execute("DELETE FROM scans")
        self._connection.commit()

    @staticmethod
    def _row_to_scan(row: sqlite3.Row) -> Scan:
        return Scan(
            id=row["id"],
            created_at=row["created_at"],
            target=row["target"],
            target_ip=row["target_ip"],
            profile_name=row["profile_name"],
            profile_origin=row["profile_origin"],
            ports_scanned=json.loads(row["ports_scanned"]),
            scan_mode=ScanMode(row["scan_mode"]),
            status=ScanStatus(row["status"]),
            analysis_mode=AnalysisMode(row["analysis_mode"]),
            root_target_ip=row["root_target_ip"],
            discovered_targets=json.loads(row["discovered_targets"]),
            max_depth=row["max_depth"],
            max_additional_targets=row["max_additional_targets"],
            allowed_subnet=row["allowed_subnet"],
        )

    # --- hosts / ports / services ---------------------------------------

    def save_hosts(self, scan_id: str, hosts: list[Host]) -> None:
        try:
            cursor = self._connection.cursor()
            cursor.execute("DELETE FROM hosts WHERE scan_id = ?", (scan_id,))
            # ON DELETE CASCADE n'est pas active par defaut sur sqlite3, nettoyage manuel.
            for host in hosts:
                self._insert_host(cursor, scan_id, host)
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"echec de sauvegarde des hosts pour le scan {scan_id!r}") from exc

    def _insert_host(self, cursor: sqlite3.Cursor, scan_id: str, host: Host) -> None:
        host_id = new_id()
        cursor.execute(
            """
            INSERT INTO hosts
                (id, scan_id, ip, hostname, os_guess, os_confidence,
                 firewall_network_present, firewall_network_confidence,
                 waf_present, waf_name_guess, waf_confidence, exposure,
                 exposure_confidence, depth_level, discovered_from,
                 discovery_source, discovery_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                host_id,
                scan_id,
                host.ip,
                host.hostname,
                host.os_guess,
                host.os_confidence.value,
                host.firewall_network_present,
                host.firewall_network_confidence.value,
                host.waf_present,
                host.waf_name_guess,
                host.waf_confidence.value,
                host.exposure,
                host.exposure_confidence.value,
                host.depth_level,
                host.discovered_from,
                host.discovery_source,
                host.discovery_confidence.value,
            ),
        )
        for port in host.ports:
            self._insert_port(cursor, host_id, port)

    def _insert_port(self, cursor: sqlite3.Cursor, host_id: str, port: Port) -> None:
        port_id = new_id()
        cursor.execute(
            """
            INSERT INTO ports (id, host_id, port_number, protocol, state, state_confidence, evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                port_id,
                host_id,
                port.port_number,
                port.protocol,
                port.state.value,
                port.state_confidence.value,
                json.dumps(port.evidence),
            ),
        )
        if port.service is not None:
            self._insert_service(cursor, port_id, port.service)

    def _insert_service(self, cursor: sqlite3.Cursor, port_id: str, service: Service) -> None:
        cursor.execute(
            """
            INSERT INTO services (
                id, port_id, protocol_name, protocol_confidence, software,
                software_confidence, version, version_confidence, role,
                role_confidence, role_chain, auth_required,
                auth_required_confidence, auth_types, auth_types_confidence,
                auth_details, firewall_app_present, firewall_app_confidence,
                waf_present, waf_name_guess, waf_confidence, tls_library,
                tls_library_confidence, tls_version, tls_version_confidence,
                tls_cipher, tls_cipher_confidence, tls_cert_subject,
                tls_cert_issuer, tls_cert_san, encapsulation_layers, evidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id(),
                port_id,
                service.protocol_name,
                service.protocol_confidence.value,
                service.software,
                service.software_confidence.value,
                service.version,
                service.version_confidence.value,
                service.role,
                service.role_confidence.value,
                json.dumps([asdict(r) for r in service.role_chain]),
                service.auth_required,
                service.auth_required_confidence.value,
                json.dumps(service.auth_types),
                service.auth_types_confidence.value,
                json.dumps(service.auth_details),
                service.firewall_app_present,
                service.firewall_app_confidence.value,
                service.waf_present,
                service.waf_name_guess,
                service.waf_confidence.value,
                service.tls_library,
                service.tls_library_confidence.value,
                service.tls_version,
                service.tls_version_confidence.value,
                service.tls_cipher,
                service.tls_cipher_confidence.value,
                service.tls_cert_subject,
                service.tls_cert_issuer,
                json.dumps(service.tls_cert_san),
                json.dumps([asdict(t) for t in service.encapsulation_layers]),
                json.dumps(service.evidence),
            ),
        )

    def get_hosts(self, scan_id: str) -> tuple[Host, ...]:
        host_rows = self._connection.execute(
            "SELECT * FROM hosts WHERE scan_id = ? ORDER BY depth_level ASC", (scan_id,)
        ).fetchall()

        hosts = []
        for host_row in host_rows:
            port_rows = self._connection.execute(
                "SELECT * FROM ports WHERE host_id = ?", (host_row["id"],)
            ).fetchall()
            ports = [self._row_to_port(row) for row in port_rows]
            hosts.append(
                Host(
                    ip=host_row["ip"],
                    hostname=host_row["hostname"],
                    os_guess=host_row["os_guess"],
                    os_confidence=ConfidenceLevel(host_row["os_confidence"]),
                    firewall_network_present=(
                        bool(host_row["firewall_network_present"])
                        if host_row["firewall_network_present"] is not None
                        else None
                    ),
                    firewall_network_confidence=ConfidenceLevel(host_row["firewall_network_confidence"]),
                    waf_present=bool(host_row["waf_present"]) if host_row["waf_present"] is not None else None,
                    waf_name_guess=host_row["waf_name_guess"],
                    waf_confidence=ConfidenceLevel(host_row["waf_confidence"]),
                    exposure=host_row["exposure"],
                    exposure_confidence=ConfidenceLevel(host_row["exposure_confidence"]),
                    ports=ports,
                    depth_level=host_row["depth_level"],
                    discovered_from=host_row["discovered_from"],
                    discovery_source=host_row["discovery_source"],
                    discovery_confidence=ConfidenceLevel(host_row["discovery_confidence"]),
                )
            )
        return tuple(hosts)

    def _row_to_port(self, row: sqlite3.Row) -> Port:
        service_row = self._connection.execute(
            "SELECT * FROM services WHERE port_id = ?", (row["id"],)
        ).fetchone()
        return Port(
            port_number=row["port_number"],
            protocol=row["protocol"],
            state=PortState(row["state"]),
            state_confidence=ConfidenceLevel(row["state_confidence"]),
            evidence=json.loads(row["evidence"]),
            service=self._row_to_service(service_row) if service_row is not None else None,
        )

    @staticmethod
    def _row_to_service(row: sqlite3.Row) -> Service:
        def _role_elements(raw: str) -> list[RoleElement]:
            return [
                RoleElement(
                    role=d["role"], software=d["software"],
                    confidence=ConfidenceLevel(d["confidence"]), evidence=d["evidence"],
                )
                for d in json.loads(raw)
            ]

        def _transport_layers(raw: str) -> list[TransportLayer]:
            return [
                TransportLayer(
                    order=d["order"], layer_type=d["layer_type"], protocol=d["protocol"],
                    software=d["software"], version=d["version"],
                    confidence=ConfidenceLevel(d["confidence"]), evidence=d["evidence"],
                )
                for d in json.loads(raw)
            ]

        def _bool(value: Any) -> bool | None:
            return bool(value) if value is not None else None

        return Service(
            protocol_name=row["protocol_name"],
            protocol_confidence=ConfidenceLevel(row["protocol_confidence"]),
            software=row["software"],
            software_confidence=ConfidenceLevel(row["software_confidence"]),
            version=row["version"],
            version_confidence=ConfidenceLevel(row["version_confidence"]),
            role=row["role"],
            role_confidence=ConfidenceLevel(row["role_confidence"]),
            role_chain=_role_elements(row["role_chain"]),
            auth_required=_bool(row["auth_required"]),
            auth_required_confidence=ConfidenceLevel(row["auth_required_confidence"]),
            auth_types=json.loads(row["auth_types"]),
            auth_types_confidence=ConfidenceLevel(row["auth_types_confidence"]),
            auth_details=json.loads(row["auth_details"]),
            firewall_app_present=_bool(row["firewall_app_present"]),
            firewall_app_confidence=ConfidenceLevel(row["firewall_app_confidence"]),
            waf_present=_bool(row["waf_present"]),
            waf_name_guess=row["waf_name_guess"],
            waf_confidence=ConfidenceLevel(row["waf_confidence"]),
            tls_library=row["tls_library"],
            tls_library_confidence=ConfidenceLevel(row["tls_library_confidence"]),
            tls_version=row["tls_version"],
            tls_version_confidence=ConfidenceLevel(row["tls_version_confidence"]),
            tls_cipher=row["tls_cipher"],
            tls_cipher_confidence=ConfidenceLevel(row["tls_cipher_confidence"]),
            tls_cert_subject=row["tls_cert_subject"],
            tls_cert_issuer=row["tls_cert_issuer"],
            tls_cert_san=json.loads(row["tls_cert_san"]),
            encapsulation_layers=_transport_layers(row["encapsulation_layers"]),
            evidence=json.loads(row["evidence"]),
        )

    # --- graphe d'architecture -------------------------------------------

    def save_graph(self, scan_id: str, graph: ArchitectureGraph) -> None:
        try:
            self._connection.execute("DELETE FROM architecture_graph WHERE scan_id = ?", (scan_id,))
            self._connection.execute(
                "INSERT INTO architecture_graph (id, scan_id, root_node, nodes, edges) VALUES (?, ?, ?, ?, ?)",
                (
                    new_id(),
                    scan_id,
                    graph.root_node,
                    json.dumps(graph.nodes),
                    json.dumps([asdict(edge) for edge in graph.edges]),
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"echec de sauvegarde du graphe pour le scan {scan_id!r}") from exc

    def get_graph(self, scan_id: str) -> ArchitectureGraph | None:
        row = self._connection.execute(
            "SELECT * FROM architecture_graph WHERE scan_id = ?", (scan_id,)
        ).fetchone()
        if row is None:
            return None

        edges = [
            ArchitectureEdge(
                source_ip=d["source_ip"], target_ip=d["target_ip"], relation_type=d["relation_type"],
                confidence=ConfidenceLevel(d["confidence"]), evidence=d["evidence"],
            )
            for d in json.loads(row["edges"])
        ]
        return ArchitectureGraph(nodes=json.loads(row["nodes"]), edges=edges, root_node=row["root_node"])
