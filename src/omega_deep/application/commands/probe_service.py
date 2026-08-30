# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : identifier le service tournant sur un port deja detecte
OPEN. Identique a omega-check."""
from __future__ import annotations

from omega_deep.domain.services.models import Service
from omega_deep.domain.services.policies import classify_probe_strategy
from omega_deep.domain.services.service import enrich_with_role_and_layers, merge_probes
from omega_deep.ports.generic_banner_prober import GenericBannerProber
from omega_deep.ports.http_prober import HttpProber
from omega_deep.ports.ssh_prober import SshProber
from omega_deep.ports.tls_prober import TlsProber
from omega_deep.ports.vnc_prober import VncProber


def probe_service(
    *,
    target_ip: str,
    port: int,
    host_header: str,
    http_prober: HttpProber,
    tls_prober: TlsProber,
    ssh_prober: SshProber,
    vnc_prober: VncProber,
    generic_prober: GenericBannerProber,
    timeout: float = 2.0,
) -> Service:
    strategy = classify_probe_strategy(port)

    if strategy == "https":
        http_result = http_prober.probe(target_ip, port, host_header, timeout, use_tls=True)
        tls_result = tls_prober.probe(target_ip, port, host_header, timeout)
        result = merge_probes(http=http_result, tls=tls_result)
    elif strategy == "http":
        result = http_prober.probe(target_ip, port, host_header, timeout, use_tls=False)
    elif strategy == "ssh":
        result = ssh_prober.probe(target_ip, port, timeout)
    elif strategy == "vnc":
        result = vnc_prober.probe(target_ip, port, timeout)
    else:
        result = generic_prober.probe(target_ip, port, timeout)

    return enrich_with_role_and_layers(port, strategy, result)
