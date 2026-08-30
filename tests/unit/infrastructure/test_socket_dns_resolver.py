import socket

import pytest

from omega_deep.application.exceptions import TargetResolutionError
from omega_deep.infrastructure.network.socket_dns_resolver import SocketDnsResolver


def test_resolve_returns_ip_unchanged() -> None:
    assert SocketDnsResolver().resolve("127.0.0.1") == "127.0.0.1"


def test_resolve_hostname_via_gethostbyname(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda name: "93.184.216.34")
    assert SocketDnsResolver().resolve("example.invalid") == "93.184.216.34"


def test_resolve_raises_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_oserror(name: str) -> str:
        raise OSError("nodename nor servname provided")

    monkeypatch.setattr(socket, "gethostbyname", raise_oserror)
    with pytest.raises(TargetResolutionError):
        SocketDnsResolver().resolve("does-not-exist.invalid")
