import socket
import threading

from pytest_httpserver import HTTPServer

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.infrastructure.network.httpx_http_prober import HttpxHttpProber


def _serve_raw_http_response_once(response: bytes) -> tuple[socket.socket, int, threading.Thread]:
    # pytest-httpserver (Werkzeug) impose son propre header Server, ce qui
    # rend ce framework inutilisable pour verifier le parsing du header
    # Server lui-meme — reponse HTTP ecrite a la main sur un socket brut.
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


def test_probe_detects_protocol_and_server_header() -> None:
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Server: nginx/1.25.3\r\n"
        b"Content-Length: 5\r\n"
        b"Connection: close\r\n"
        b"\r\n"
        b"hello"
    )
    server, port, thread = _serve_raw_http_response_once(response)
    try:
        result = HttpxHttpProber().probe("127.0.0.1", port, host_header="127.0.0.1", timeout=2.0, use_tls=False)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.protocol_name == "HTTP"
    assert result.protocol_confidence == ConfidenceLevel.VERIFIED
    assert result.software == "nginx"
    assert result.software_confidence == ConfidenceLevel.DECLARED
    assert result.version == "1.25.3"
    assert result.auth_required is False


def test_probe_detects_basic_auth_challenge(httpserver: HTTPServer) -> None:
    httpserver.expect_request("/").respond_with_data(
        "", status=401, headers={"WWW-Authenticate": 'Basic realm="admin"'}
    )

    result = HttpxHttpProber().probe(httpserver.host, httpserver.port, httpserver.host, 2.0, False)

    assert result.auth_required is True
    assert result.auth_required_confidence == ConfidenceLevel.VERIFIED
    assert result.auth_types == ["Basic"]


def test_probe_detects_waf_signature(httpserver: HTTPServer) -> None:
    httpserver.expect_request("/").respond_with_data("blocked", status=403, headers={"cf-ray": "abc123"})

    result = HttpxHttpProber().probe(httpserver.host, httpserver.port, httpserver.host, 2.0, False)

    assert result.waf_present is True
    assert result.waf_name_guess == "Cloudflare"
    assert result.waf_confidence == ConfidenceLevel.DECLARED


def test_probe_connection_failure_is_collected_not_raised() -> None:
    # Rien n'ecoute sur ce port (probable) : la sonde doit retourner un
    # Service degrade, jamais lever.
    result = HttpxHttpProber().probe("127.0.0.1", 1, "127.0.0.1", 0.3, False)

    assert result.protocol_name is None
    assert result.protocol_confidence == ConfidenceLevel.UNKNOWN
    assert result.evidence
