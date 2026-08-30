import socket
import threading

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.infrastructure.network.socket_ssh_prober import SocketSshProber


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


def test_probe_parses_ssh_banner() -> None:
    server, port, thread = _serve_banner_once(b"SSH-2.0-OpenSSH_8.9\r\n")
    try:
        result = SocketSshProber().probe("127.0.0.1", port, timeout=2.0)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.protocol_name == "SSH"
    assert result.protocol_confidence == ConfidenceLevel.VERIFIED
    assert result.software == "OpenSSH"
    assert result.software_confidence == ConfidenceLevel.DECLARED
    assert result.version == "8.9"


def test_probe_rejects_non_ssh_banner() -> None:
    server, port, thread = _serve_banner_once(b"220 not-ssh-at-all\r\n")
    try:
        result = SocketSshProber().probe("127.0.0.1", port, timeout=2.0)
    finally:
        server.close()
        thread.join(timeout=1)

    assert result.protocol_name is None
    assert result.protocol_confidence == ConfidenceLevel.UNKNOWN


def test_probe_connection_failure_is_collected_not_raised() -> None:
    result = SocketSshProber().probe("127.0.0.1", 1, timeout=0.3)
    assert result.protocol_name is None
    assert result.evidence
