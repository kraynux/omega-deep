# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation du port TlsProber (handshake, cipher, certificat).
Identique a omega-check.

`verify_mode = ssl.CERT_NONE` (posture passive, cible interne au
certificat souvent auto-signe) fait que `getpeercert()` (sans argument)
renvoie un dict VIDE — Python ne parse le certificat que s'il a ete
valide. On demande donc le DER brut via `getpeercert(binary_form=True)`
(fonctionne quel que soit verify_mode) et on le parse nous-memes avec
`cryptography`."""
from __future__ import annotations

import socket
import ssl

from cryptography import x509
from cryptography.x509.oid import ExtensionOID, NameOID

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.services.models import Service


def _common_name(name: x509.Name) -> str | None:
    attributes = name.get_attributes_for_oid(NameOID.COMMON_NAME)
    return str(attributes[0].value) if attributes else None


def _subject_alt_names(cert: x509.Certificate) -> list[str]:
    try:
        extension = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
    except x509.ExtensionNotFound:
        return []
    san = extension.value
    assert isinstance(san, x509.SubjectAlternativeName)
    return [f"DNS:{name}" for name in san.get_values_for_type(x509.DNSName)]


class SslTlsProber:
    """Implemente ports/tls_prober.py::TlsProber."""

    def probe(self, target_ip: str, port: int, sni_hostname: str, timeout: float) -> Service:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # posture passive : on OBSERVE le certificat,
        # on ne bloque pas le scan sur une chaine de confiance invalide (self-signed frequent en interne).

        try:
            with socket.create_connection((target_ip, port), timeout=timeout) as sock, context.wrap_socket(
                sock, server_hostname=sni_hostname
            ) as ssl_sock:
                tls_version = ssl_sock.version()
                cipher_info = ssl_sock.cipher()
                cert_der = ssl_sock.getpeercert(binary_form=True)
        except (ssl.SSLError, OSError) as exc:
            return Service(evidence=[f"echec du handshake TLS : {exc}"])

        subject = issuer = None
        san: list[str] = []
        if cert_der:
            cert = x509.load_der_x509_certificate(cert_der)
            subject = _common_name(cert.subject)
            issuer = _common_name(cert.issuer)
            san = _subject_alt_names(cert)

        evidence = [f"handshake TLS reussi : {tls_version}"]
        if subject:
            evidence.append(f"certificat subject={subject}")

        return Service(
            tls_library=None,  # fingerprint de librairie hors-scope (comportemental, phase ulterieure)
            tls_library_confidence=ConfidenceLevel.UNKNOWN,
            tls_version=tls_version,
            tls_version_confidence=ConfidenceLevel.VERIFIED,
            tls_cipher=cipher_info[0] if cipher_info else None,
            tls_cipher_confidence=ConfidenceLevel.VERIFIED if cipher_info else ConfidenceLevel.UNKNOWN,
            tls_cert_subject=subject,
            tls_cert_issuer=issuer,
            tls_cert_san=san,
            evidence=evidence,
        )
