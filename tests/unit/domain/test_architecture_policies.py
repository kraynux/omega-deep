from omega_deep.domain.architecture.policies import relation_type_for_source


def test_header_maps_to_proxy_to() -> None:
    assert relation_type_for_source("header") == "proxy_to"


def test_redirection_maps_to_redirect_to() -> None:
    assert relation_type_for_source("redirection") == "redirect_to"


def test_certificate_maps_to_linked_to() -> None:
    assert relation_type_for_source("certificate") == "linked_to"


def test_html_link_maps_to_linked_to() -> None:
    assert relation_type_for_source("html_link") == "linked_to"


def test_unknown_source_defaults_to_linked_to() -> None:
    assert relation_type_for_source("some-future-source") == "linked_to"


def test_none_source_defaults_to_linked_to() -> None:
    assert relation_type_for_source(None) == "linked_to"
