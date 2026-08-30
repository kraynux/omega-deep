# Copyright (c) 2026 kraynux - Licence MIT
"""Definition DDL des tables SQLite. Etend le schema d'omega-check :

- `scans` : colonnes DEEP additionnelles (`analysis_mode`, `root_target_ip`,
  `discovered_targets` JSON, `max_depth`, `max_additional_targets`,
  `allowed_subnet`).
- `hosts` : colonnes DEEP additionnelles (`depth_level`, `discovered_from`,
  `discovery_source`, `discovery_confidence`).
- `architecture_graph` (NOUVELLE table) : un graphe par scan racine
  (OMEGA-DEEP_SPECIFICATIONS.md §7.1) — `nodes`/`edges` en JSON, comme
  `ports_scanned`/`discovered_targets` (pas de sur-normalisation pour un
  graphe qui n'a pas besoin d'etre requete port par port).

`id` en UUID (pas autoincrement), `created_at` en ISO8601 UTC — memes
principes que omega-check/omega-scan (D-006)."""
from __future__ import annotations

SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS scans (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        tool TEXT NOT NULL DEFAULT 'deep',
        target TEXT NOT NULL,
        target_ip TEXT NOT NULL,
        profile_name TEXT,
        profile_origin TEXT,
        ports_scanned TEXT NOT NULL,
        scan_mode TEXT NOT NULL,
        status TEXT NOT NULL,
        analysis_mode TEXT NOT NULL DEFAULT 'fixed',
        root_target_ip TEXT NOT NULL DEFAULT '',
        discovered_targets TEXT NOT NULL DEFAULT '[]',
        max_depth INTEGER NOT NULL DEFAULT 3,
        max_additional_targets INTEGER NOT NULL DEFAULT 10,
        allowed_subnet TEXT
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_scans_target ON scans (target)
    """,
    """
    CREATE TABLE IF NOT EXISTS hosts (
        id TEXT PRIMARY KEY,
        scan_id TEXT NOT NULL REFERENCES scans (id),
        ip TEXT NOT NULL,
        hostname TEXT,
        os_guess TEXT,
        os_confidence TEXT NOT NULL,
        firewall_network_present INTEGER,
        firewall_network_confidence TEXT NOT NULL,
        waf_present INTEGER,
        waf_name_guess TEXT,
        waf_confidence TEXT NOT NULL,
        exposure TEXT,
        exposure_confidence TEXT NOT NULL,
        depth_level INTEGER NOT NULL DEFAULT 0,
        discovered_from TEXT,
        discovery_source TEXT,
        discovery_confidence TEXT NOT NULL DEFAULT 'unknown'
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_hosts_scan_id ON hosts (scan_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS ports (
        id TEXT PRIMARY KEY,
        host_id TEXT NOT NULL REFERENCES hosts (id),
        port_number INTEGER NOT NULL,
        protocol TEXT NOT NULL,
        state TEXT NOT NULL,
        state_confidence TEXT NOT NULL,
        evidence TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_ports_host_id ON ports (host_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_ports_port_number ON ports (port_number)
    """,
    """
    CREATE TABLE IF NOT EXISTS services (
        id TEXT PRIMARY KEY,
        port_id TEXT NOT NULL REFERENCES ports (id),
        protocol_name TEXT,
        protocol_confidence TEXT NOT NULL,
        software TEXT,
        software_confidence TEXT NOT NULL,
        version TEXT,
        version_confidence TEXT NOT NULL,
        role TEXT,
        role_confidence TEXT NOT NULL,
        role_chain TEXT NOT NULL,
        auth_required INTEGER,
        auth_required_confidence TEXT NOT NULL,
        auth_types TEXT NOT NULL,
        auth_types_confidence TEXT NOT NULL,
        auth_details TEXT NOT NULL,
        firewall_app_present INTEGER,
        firewall_app_confidence TEXT NOT NULL,
        waf_present INTEGER,
        waf_name_guess TEXT,
        waf_confidence TEXT NOT NULL,
        tls_library TEXT,
        tls_library_confidence TEXT NOT NULL,
        tls_version TEXT,
        tls_version_confidence TEXT NOT NULL,
        tls_cipher TEXT,
        tls_cipher_confidence TEXT NOT NULL,
        tls_cert_subject TEXT,
        tls_cert_issuer TEXT,
        tls_cert_san TEXT NOT NULL,
        encapsulation_layers TEXT NOT NULL,
        evidence TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_services_port_id ON services (port_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS architecture_graph (
        id TEXT PRIMARY KEY,
        scan_id TEXT NOT NULL REFERENCES scans (id),
        root_node TEXT NOT NULL,
        nodes TEXT NOT NULL,
        edges TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_architecture_graph_scan_id ON architecture_graph (scan_id)
    """,
)
