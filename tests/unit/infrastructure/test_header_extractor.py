from omega_deep.infrastructure.discovery.header_extractor import extract_from_headers


def test_extracts_x_forwarded_host() -> None:
    results = extract_from_headers({"X-Forwarded-Host": "backend.internal"})
    assert results == [("backend.internal", "header x-forwarded-host: backend.internal")]


def test_extracts_x_real_ip() -> None:
    results = extract_from_headers({"X-Real-IP": "10.0.0.5"})
    assert results == [("10.0.0.5", "header x-real-ip: 10.0.0.5")]


def test_extracts_via_header_last_token() -> None:
    results = extract_from_headers({"Via": "1.1 proxy.internal"})
    assert results == [("proxy.internal", "header via: 1.1 proxy.internal")]


def test_extracts_multiple_comma_separated_values() -> None:
    results = extract_from_headers({"X-Forwarded-Host": "a.internal, b.internal"})
    assert [r[0] for r in results] == ["a.internal", "b.internal"]


def test_no_discovery_headers_present_returns_empty() -> None:
    assert extract_from_headers({"Content-Type": "text/html"}) == []


def test_header_lookup_is_case_insensitive() -> None:
    results = extract_from_headers({"X-REAL-IP": "10.0.0.5"})
    assert results == [("10.0.0.5", "header x-real-ip: 10.0.0.5")]
