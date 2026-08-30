import socket
from unittest.mock import MagicMock, patch

import pytest

from omega_deep.core.enums import ConfidenceLevel, PortState
from omega_deep.infrastructure.network.tcp_port_prober import TcpPortProber


def test_probe_returns_open_for_a_listening_port() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    try:
        result = TcpPortProber().probe("127.0.0.1", port, "tcp", timeout=1.0, retries=0)
        assert result.state == PortState.OPEN
        assert result.state_confidence == ConfidenceLevel.VERIFIED
    finally:
        server.close()


def test_probe_returns_closed_when_connection_refused() -> None:
    # bind puis fermer immediatement : port libre garanti, rien n'ecoute dessus.
    probe_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe_socket.bind(("127.0.0.1", 0))
    port = probe_socket.getsockname()[1]
    probe_socket.close()

    result = TcpPortProber().probe("127.0.0.1", port, "tcp", timeout=1.0, retries=0)
    assert result.state == PortState.CLOSED
    assert result.state_confidence == ConfidenceLevel.VERIFIED


def test_probe_returns_filtered_after_all_retries_timeout() -> None:
    mock_sock = MagicMock()
    mock_sock.__enter__.return_value = mock_sock
    mock_sock.connect.side_effect = TimeoutError()

    with patch("socket.socket", return_value=mock_sock):
        result = TcpPortProber().probe("10.0.0.1", 12345, "tcp", timeout=0.01, retries=2)

    assert result.state == PortState.FILTERED
    assert result.state_confidence == ConfidenceLevel.INFERRED
    assert mock_sock.connect.call_count == 3  # retries + 1 tentative initiale


def test_probe_rejects_unsupported_protocol() -> None:
    with pytest.raises(NotImplementedError):
        TcpPortProber().probe("127.0.0.1", 80, "udp", timeout=1.0, retries=0)
