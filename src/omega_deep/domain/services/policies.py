# Copyright (c) 2026 kraynux - Licence MIT
"""Regles pures de classification des indices de service (voir
OMEGA-DEEP_SPECIFICATIONS.md §4/§5.1). Identique a omega-check. Aucune E/S
ici : les adaptateurs infrastructure/network/*.py collectent les donnees
brutes (headers, banners) et appellent ces fonctions pour les interpreter."""
from __future__ import annotations

import re

from omega_deep.core.enums import ConfidenceLevel
from omega_deep.domain.profiles.defaults import SYSTEM_PROFILES
from omega_deep.domain.services.models import Service, TransportLayer
from omega_deep.shared.i18n import _

# --- HTTP : header Server -----------------------------------------------

_SERVER_HEADER_RE = re.compile(r"^([A-Za-z][\w.-]*)(?:/([\w.+-]+))?")


def parse_server_header(value: str | None) -> tuple[str | None, str | None]:
    """'nginx/1.25.3' -> ('nginx', '1.25.3'). 'cloudflare' -> ('cloudflare', None).
    Toujours DECLARED cote appelant : c'est une valeur auto-annoncee par la
    cible, jamais VERIFIED (voir D-001)."""
    if not value:
        return None, None
    match = _SERVER_HEADER_RE.match(value.strip())
    if not match:
        return None, None
    return match.group(1), match.group(2)


# --- HTTP : authentification ---------------------------------------------

def classify_http_auth(
    status_code: int, headers: dict[str, str]
) -> tuple[bool | None, ConfidenceLevel, list[str], ConfidenceLevel]:
    """Retourne (auth_required, sa confiance, auth_types, leur confiance).

    401 + WWW-Authenticate : signal protocolaire direct -> VERIFIED.
    200 : signal protocolaire direct (pas de mur d'auth) -> VERIFIED.
    Tout le reste (403, redirections, etc.) : ambigu -> UNKNOWN."""
    www_authenticate = headers.get("www-authenticate")
    if status_code == 401 and www_authenticate:
        scheme = www_authenticate.split(" ", 1)[0].strip()
        return True, ConfidenceLevel.VERIFIED, [scheme], ConfidenceLevel.VERIFIED
    if status_code == 200:
        return False, ConfidenceLevel.VERIFIED, [], ConfidenceLevel.VERIFIED
    return None, ConfidenceLevel.UNKNOWN, [], ConfidenceLevel.UNKNOWN


# --- HTTP : signatures WAF -------------------------------------------------

# (header en minuscule, sous-chaine attendue dans la valeur ou None si la
# seule presence du header suffit, nom du WAF)
_WAF_SIGNATURES: tuple[tuple[str, str | None, str], ...] = (
    ("cf-ray", None, "Cloudflare"),
    ("server", "cloudflare", "Cloudflare"),
    ("x-sucuri-id", None, "Sucuri"),
    ("server", "sucuri", "Sucuri"),
    ("x-akamai-transformed", None, "Akamai"),
    ("server", "akamaighost", "Akamai"),
    ("x-sdk", "imperva", "Imperva Incapsula"),
    ("x-iinfo", None, "Imperva Incapsula"),
    ("server", "awselb", _("AWS ELB (pas un WAF applicatif à proprement parler)")),
)


def detect_waf(headers: dict[str, str]) -> tuple[bool | None, str | None, ConfidenceLevel]:
    """Signature d'en-tete claire : la cible declare elle-meme la presence
    du WAF (directement ou via l'infrastructure qui le pose devant elle) ;
    reste DECLARED, pas VERIFIED, meme si le nom est tres explicite."""
    lower_headers = {k.lower(): v for k, v in headers.items()}
    for header_name, needle, waf_name in _WAF_SIGNATURES:
        value = lower_headers.get(header_name)
        if value is None:
            continue
        if needle is None or needle.lower() in value.lower():
            return True, waf_name, ConfidenceLevel.DECLARED
    return None, None, ConfidenceLevel.UNKNOWN


# --- SSH : banner ----------------------------------------------------------

_SSH_BANNER_RE = re.compile(r"^SSH-\d+\.\d+-(\S+)")


def parse_ssh_banner(banner: str) -> tuple[str | None, str | None]:
    """'SSH-2.0-OpenSSH_8.9' -> ('OpenSSH', '8.9'). 'SSH-2.0-dropbear' ->
    ('dropbear', None) : pas de '_' -> pas de version annoncee."""
    match = _SSH_BANNER_RE.match(banner.strip())
    if not match:
        return None, None

    token = match.group(1)
    if "_" in token:
        software, version = token.split("_", 1)
        return software, version
    return token, None


# --- Banner generique (FTP, SMTP, IMAP, etc.) ------------------------------

_PRODUCT_VERSION_RE = re.compile(r"([A-Za-z][\w.-]{2,})/([\w.]+)")


def parse_generic_banner(banner: str) -> tuple[str | None, str | None]:
    """Extraction volontairement prudente : seul un motif 'Produit/Version'
    explicite dans le banner est retenu, le reste est laisse UNKNOWN plutot
    que devine."""
    match = _PRODUCT_VERSION_RE.search(banner)
    if not match:
        return None, None
    return match.group(1), match.group(2)


# --- VNC : types de securite (RFB) -----------------------------------------

RFB_SECURITY_TYPE_NAMES: dict[int, str] = {
    0: "invalid",
    1: "none",
    2: "vnc_auth",
    5: "ra2",
    6: "ra2ne",
    16: "tight",
    17: "ultra",
    18: "vencrypt",
    19: "gtk_vnc_sasl",
    20: "md5_hash_auth",
    21: "colin_dean_xvp",
    30: "xvp",
    128: "apple_remote_desktop",
}


def classify_vnc_security(security_types: list[int]) -> tuple[bool | None, list[str]]:
    """A partir des codes de type de securite annonces par le serveur RFB,
    retourne (auth_required, noms lisibles). "none" (1) parmi les options
    offertes -> une connexion sans authentification est possible ->
    auth_required=False. Aucune option -> None (echec de negociation)."""
    if not security_types:
        return None, []
    names = [RFB_SECURITY_TYPE_NAMES.get(code, f"unknown({code})") for code in security_types]
    return 1 not in security_types, names


# --- Strategie de sonde par port -------------------------------------------

_HTTPS_PORTS = frozenset({443, 8443, 9443, 10443})
_HTTP_PORTS = frozenset({80, 8000, 8008, 8080, 8081, 8082, 8880, 8888, 9000, 9090, 10000, 10080})
_SSH_PORTS = frozenset({22})
_VNC_PORTS = frozenset(range(5900, 5911))  # meme plage que le profil systeme "remote"


# --- Regles de role ---------------------------------------------------------

_DATABASE_PORTS = frozenset(SYSTEM_PROFILES["db"].ports)  # reutilise la liste existante, pas de duplication


def infer_role(port: int, service: Service) -> tuple[str | None, ConfidenceLevel]:
    """Role a partir du protocole deja detecte par les probes.

    Perimetre volontairement limite : "reverse proxy" (headers
    X-Forwarded-*/Via) et "cache HTTP" (headers Age/X-Cache) NE SONT PAS
    couverts ici — ces regles ont besoin des en-tetes HTTP bruts, que
    Service ne conserve pas. Le bounded context 'architecture' de DEEP
    (domain/architecture/) prend le relai pour les chaines de roles inter-
    hosts, pas ce fichier."""
    if service.protocol_name in ("HTTP", "HTTPS"):
        return _("serveur web"), ConfidenceLevel.INFERRED
    if service.protocol_name == "SSH":
        return _("accès shell"), ConfidenceLevel.CORROBORATED
    if service.protocol_name == "VNC":
        return _("accès graphique"), ConfidenceLevel.CORROBORATED
    if port in _DATABASE_PORTS:
        return _("base de données"), ConfidenceLevel.INFERRED
    return None, ConfidenceLevel.UNKNOWN


# --- Pile protocolaire -------------------------------------------------

def build_transport_layers(strategy: str) -> list[TransportLayer]:
    """TCP est toujours la couche 0 (le port etant OPEN, verifie par le
    scan lui-meme). Le reste depend de la strategie de sonde utilisee —
    deduit du protocole reellement negocie, jamais devine."""
    layers = [
        TransportLayer(order=0, layer_type="transport", protocol="tcp", confidence=ConfidenceLevel.VERIFIED)
    ]
    if strategy == "https":
        layers.append(
            TransportLayer(order=1, layer_type="security", protocol="tls", confidence=ConfidenceLevel.VERIFIED)
        )
        layers.append(
            TransportLayer(order=2, layer_type="application", protocol="http", confidence=ConfidenceLevel.VERIFIED)
        )
    elif strategy == "http":
        layers.append(
            TransportLayer(order=1, layer_type="application", protocol="http", confidence=ConfidenceLevel.VERIFIED)
        )
    elif strategy == "ssh":
        layers.append(
            TransportLayer(order=1, layer_type="application", protocol="ssh", confidence=ConfidenceLevel.VERIFIED)
        )
    elif strategy == "vnc":
        layers.append(
            TransportLayer(order=1, layer_type="application", protocol="rfb", confidence=ConfidenceLevel.VERIFIED)
        )
    return layers


def classify_probe_strategy(port: int) -> str:
    """Heuristique basee sur les numeros de port bien connus (voir
    domain/profiles/defaults.py) : "https"/"http"/"ssh"/"vnc"/"generic" —
    premiere approximation raisonnable, pas une detection active."""
    if port in _HTTPS_PORTS:
        return "https"
    if port in _HTTP_PORTS:
        return "http"
    if port in _SSH_PORTS:
        return "ssh"
    if port in _VNC_PORTS:
        return "vnc"
    return "generic"
