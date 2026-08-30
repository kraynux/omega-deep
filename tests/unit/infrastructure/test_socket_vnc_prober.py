import socket
import struct
import threading

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.infrastructure.network.socket_vnc_prober import SocketVncProber


def _serve_rfb_once(server_handler: "callable") -> tuple[socket.socket, int, threading.Thread]:  # type: ignore[valid-type]
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def _serve() -> None:
        try:
            conn, _ = server.accept()
        except OSError:
            return
        try:
            server_handler(conn)
        finally:
            conn.close()

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    return server, port, thread


def test_probe_rfb_3_8_with_two_security_types() -> None:
    def handler(conn: socket.socket) -> None:
        conn.sendall(b"RFB 003.008\n")
        conn.recv(12)  # echo du client
        conn.sendall(bytes([2, 1, 2]))  # 2 types : none (1), vnc_auth (2)

    server, port, thread = _serve_rfb_once(handler)
    try:
        result = SocketVncProber().probe("127.0.0.1", port, timeout=2.0)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.protocol_name == "VNC"
    assert result.protocol_confidence == ConfidenceLevel.VERIFIED
    assert result.version == "3.8"
    assert result.auth_required is False  # "none" est parmi les options offertes
    assert set(result.auth_types) == {"none", "vnc_auth"}


def test_probe_rfb_3_3_legacy_single_security_type() -> None:
    def handler(conn: socket.socket) -> None:
        conn.sendall(b"RFB 003.003\n")
        conn.recv(12)
        conn.sendall(struct.pack(">I", 2))  # vnc_auth uniquement, encode sur 4 octets

    server, port, thread = _serve_rfb_once(handler)
    try:
        result = SocketVncProber().probe("127.0.0.1", port, timeout=2.0)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.version == "3.3"
    assert result.auth_required is True
    assert result.auth_types == ["vnc_auth"]


def test_probe_connection_refused_by_server() -> None:
    def handler(conn: socket.socket) -> None:
        conn.sendall(b"RFB 003.008\n")
        conn.recv(12)
        conn.sendall(bytes([0]))  # count=0 : connexion refusee

    server, port, thread = _serve_rfb_once(handler)
    try:
        result = SocketVncProber().probe("127.0.0.1", port, timeout=2.0)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.protocol_name == "VNC"
    assert result.auth_types == []


def test_probe_rejects_non_rfb_banner() -> None:
    def handler(conn: socket.socket) -> None:
        conn.sendall(b"not-rfb-at-all\n")

    server, port, thread = _serve_rfb_once(handler)
    try:
        result = SocketVncProber().probe("127.0.0.1", port, timeout=2.0)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.protocol_name is None


def test_probe_connection_failure_is_collected_not_raised() -> None:
    result = SocketVncProber().probe("127.0.0.1", 1, timeout=0.3)
    assert result.protocol_name is None
    assert result.evidence
