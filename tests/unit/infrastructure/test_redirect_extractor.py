from omega_deep.infrastructure.discovery.redirect_extractor import extract_from_redirect


def test_extracts_absolute_redirect() -> None:
    results = extract_from_redirect("https://backend.internal:8443/path")
    assert results == [("backend.internal", "redirection Location: https://backend.internal:8443/path")]


def test_relative_redirect_reveals_no_new_host() -> None:
    assert extract_from_redirect("/login") == []


def test_no_location_returns_empty() -> None:
    assert extract_from_redirect(None) == []
