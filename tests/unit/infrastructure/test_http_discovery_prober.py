import socket
import threading

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.infrastructure.discovery.http_discovery_prober import HttpDiscoveryProber


def _serve_raw_http_response_once(response: bytes) -> tuple[socket.socket, int, threading.Thread]:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def _serve() -> None:
        try:
            conn, _ = server.accept()
        except OSError:
            return
        conn.recv(4096)
        conn.sendall(response)
        conn.close()

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    return server, port, thread


def test_probe_collects_header_redirect_and_html_candidates() -> None:
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"X-Forwarded-Host: backend.internal\r\n"
        b"Content-Type: text/html\r\n"
        b"Content-Length: 45\r\n"
        b"Connection: close\r\n"
        b"\r\n"
        b'<a href="https://cdn.internal/app.js">app</a>'
    )
    server, port, thread = _serve_raw_http_response_once(response)
    try:
        result = HttpDiscoveryProber().probe(
            "127.0.0.1", port, host_header="127.0.0.1", timeout=2.0, use_tls=False, tls_cert_san=[]
        )
    finally:
        server.close()
        thread.join(timeout=1)

    by_source = {target.source: target for target in result}
    assert by_source["header"].host == "backend.internal"
    assert by_source["header"].confidence == ConfidenceLevel.DECLARED
    assert by_source["html_link"].host == "cdn.internal"
    assert by_source["html_link"].confidence == ConfidenceLevel.INFERRED


def test_probe_includes_certificate_candidates_without_extra_handshake() -> None:
    # Rien n'ecoute reellement : la requete HTTP echoue, mais le SAN deja
    # fourni doit quand meme etre retourne (pas de dependance a la requete).
    result = HttpDiscoveryProber().probe(
        "127.0.0.1", 1, host_header="127.0.0.1", timeout=0.3, use_tls=False,
        tls_cert_san=["DNS:backend.internal"],
    )

    assert len(result) == 1
    assert result[0].source == "certificate"
    assert result[0].host == "backend.internal"
    assert result[0].confidence == ConfidenceLevel.DECLARED


def test_probe_connection_failure_returns_empty_without_san() -> None:
    result = HttpDiscoveryProber().probe(
        "127.0.0.1", 1, host_header="127.0.0.1", timeout=0.3, use_tls=False, tls_cert_san=[]
    )
    assert result == []


def test_probe_all_candidates_are_proposed_state() -> None:
    result = HttpDiscoveryProber().probe(
        "127.0.0.1", 1, host_header="127.0.0.1", timeout=0.3, use_tls=False,
        tls_cert_san=["DNS:backend.internal"],
    )
    assert all(target.state.value == "proposed" for target in result)
    assert all(target.discovered_from == "127.0.0.1" for target in result)
