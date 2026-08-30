from omega_deep.infrastructure.discovery.html_link_extractor import extract_from_html_links


def test_extracts_absolute_href_link() -> None:
    html = '<a href="https://backend.internal/admin">admin</a>'
    results = extract_from_html_links(html)
    assert results == [("backend.internal", "lien HTML : https://backend.internal/admin")]


def test_extracts_absolute_src_link() -> None:
    html = '<img src="http://cdn.internal/logo.png">'
    results = extract_from_html_links(html)
    assert results == [("cdn.internal", "lien HTML : http://cdn.internal/logo.png")]


def test_ignores_relative_links() -> None:
    html = '<a href="/contact">contact</a>'
    assert extract_from_html_links(html) == []


def test_empty_body_returns_empty() -> None:
    assert extract_from_html_links(None) == []
    assert extract_from_html_links("") == []
