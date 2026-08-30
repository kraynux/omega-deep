import socket
import threading

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.infrastructure.network.socket_generic_banner_prober import (
    SocketGenericBannerProber,
)


def _serve_banner_once(banner: bytes) -> tuple[socket.socket, int, threading.Thread]:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def _serve() -> None:
        try:
            conn, _ = server.accept()
        except OSError:
            return
        conn.sendall(banner)
        conn.close()

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    return server, port, thread


def test_probe_extracts_product_slash_version() -> None:
    server, port, thread = _serve_banner_once(b"220 ProFTPD/1.3.5e Server ready\r\n")
    try:
        result = SocketGenericBannerProber().probe("127.0.0.1", port, timeout=2.0)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.software == "ProFTPD"
    assert result.software_confidence == ConfidenceLevel.DECLARED
    assert result.version == "1.3.5e"


def test_probe_without_recognizable_pattern_stays_unknown() -> None:
    server, port, thread = _serve_banner_once(b"220 mail.example.com ESMTP Postfix\r\n")
    try:
        result = SocketGenericBannerProber().probe("127.0.0.1", port, timeout=2.0)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.software is None
    assert result.software_confidence == ConfidenceLevel.UNKNOWN
    assert result.evidence  # le banner brut reste dans evidence, meme non interprete
