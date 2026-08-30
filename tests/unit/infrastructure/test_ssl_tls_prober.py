import socket
import ssl
import threading

import trustme

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.infrastructure.network.ssl_tls_prober import SslTlsProber


def _serve_tls_once(server_socket: socket.socket, server_context: ssl.SSLContext) -> None:
    try:
        conn, _ = server_socket.accept()
    except OSError:
        return
    try:
        ssl_conn = server_context.wrap_socket(conn, server_side=True)
        ssl_conn.close()
    except ssl.SSLError:
        pass


def test_probe_extracts_tls_version_cipher_and_certificate() -> None:
    ca = trustme.CA()
    cert = ca.issue_cert("example.test")
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cert.configure_cert(server_context)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 0))
    server_socket.listen(1)
    port = server_socket.getsockname()[1]

    thread = threading.Thread(target=_serve_tls_once, args=(server_socket, server_context), daemon=True)
    thread.start()

    try:
        result = SslTlsProber().probe("127.0.0.1", port, "example.test", timeout=2.0)
    finally:
        server_socket.close()
        thread.join(timeout=2)

    assert result.tls_version is not None
    assert result.tls_version_confidence == ConfidenceLevel.VERIFIED
    assert result.tls_cipher is not None
    assert any("example.test" in san for san in result.tls_cert_san)


def test_probe_handshake_failure_is_collected_not_raised() -> None:
    result = SslTlsProber().probe("127.0.0.1", 1, "example.test", timeout=0.3)
    assert result.tls_version is None
    assert result.evidence
