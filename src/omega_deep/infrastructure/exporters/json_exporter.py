# Copyright (c) 2026 kraynux - Licence MIT
"""Export JSON. `dataclasses.asdict` suffit pour l'integralite des
agregats Scan/Host(s)/ArchitectureGraph (contrairement au stockage SQLite
qui doit aplatir en colonnes) : ConfidenceLevel etant un str-Enum,
`json.dumps` le serialise nativement sous sa valeur texte."""
from __future__ import annotations

import json
from dataclasses import asdict

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host


def export_json(scan: Scan, hosts: tuple[Host, ...], graph: ArchitectureGraph | None) -> str:
    payload = {
        "scan": asdict(scan),
        "hosts": [asdict(host) for host in hosts],
        "architecture_graph": asdict(graph) if graph is not None else None,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
