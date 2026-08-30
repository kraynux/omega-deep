from omega_deep.infrastructure.discovery.tls_san_extractor import extract_from_tls_san


def test_extracts_dns_san_entries() -> None:
    results = extract_from_tls_san(["DNS:backend.internal"])
    assert results == [("backend.internal", "certificat SAN : DNS:backend.internal")]


def test_ignores_wildcard_entries() -> None:
    assert extract_from_tls_san(["DNS:*.example.org"]) == []


def test_empty_san_list_returns_empty() -> None:
    assert extract_from_tls_san([]) == []
