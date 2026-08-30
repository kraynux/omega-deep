#!/usr/bin/env python3
# Copyright (c) 2026 kraynux - Licence MIT
"""Petit labo local pour tester le flux d'analyse multi-cibles d'omega-deep
(decouverte -> validation -> scan enfant -> graphe) SANS avoir besoin d'un
lab autorise ni d'une adresse publique : uniquement des adresses loopback
(127.0.0.0/8), toujours autorisees a scanner sur sa propre machine.

Lance deux serveurs HTTP :
  - "frontend" sur 127.0.0.1:8080 : repond avec l'en-tete
    `X-Backend-Server: 127.0.0.2:8000`, qui simule un reverse-proxy
    annoncant son backend (meme mecanisme que
    infrastructure/discovery/header_extractor.py detecte reellement,
    aucun mock cote omega-deep).
  - "backend" sur 127.0.0.2:8000 : cible qui sera decouverte et proposee
    a la validation.

127.0.0.1 et 127.0.0.2 sont tous deux loopback (donc "prives" au sens
d'omega-deep, meme /24 par defaut) : la decouverte passe le garde-fou de
perimetre sans avoir a preciser --subnet.

Usage :
    python3 scripts/local_test_lab.py

Puis, dans un AUTRE terminal :
    .venv/bin/omega-deep
    -> Analyser -> cible "127.0.0.1", profil "web" (contient les ports
       8000/8080), garde-fous par defaut -> Lancer.
    -> Une cible decouverte (127.0.0.2) doit apparaitre a l'ecran de
       validation. Accepter -> le scan enfant s'execute reellement, et le
       graphe d'architecture (detail de l'analyse) doit montrer une arete
       127.0.0.1 -> 127.0.0.2.

Ctrl+C ici arrete les deux serveurs proprement.
"""
from __future__ import annotations

import http.server
import sys
import threading

_FRONTEND_ADDR = ("127.0.0.1", 8080)
_BACKEND_ADDR = ("127.0.0.2", 8000)
_BACKEND_HEADER_VALUE = f"{_BACKEND_ADDR[0]}:{_BACKEND_ADDR[1]}"


class _FrontendHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = b"<html><body>frontend (omega-deep local lab)</body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Backend-Server", _BACKEND_HEADER_VALUE)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[frontend 127.0.0.1:8080] {fmt % args}")


class _BackendHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = b"<html><body>backend (omega-deep local lab)</body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[backend  127.0.0.2:8000] {fmt % args}")


def _serve(address: tuple[str, int], handler: type[http.server.BaseHTTPRequestHandler]) -> http.server.HTTPServer:
    server = http.server.HTTPServer(address, handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> int:
    try:
        frontend = _serve(_FRONTEND_ADDR, _FrontendHandler)
    except OSError as exc:
        print(f"Impossible de demarrer le frontend sur {_FRONTEND_ADDR} : {exc}", file=sys.stderr)
        return 1

    try:
        backend = _serve(_BACKEND_ADDR, _BackendHandler)
    except OSError as exc:
        print(f"Impossible de demarrer le backend sur {_BACKEND_ADDR} : {exc}", file=sys.stderr)
        print(
            "Si 127.0.0.2 n'est pas routee vers loopback sur ta machine, "
            "essaie 'ip addr add 127.0.0.2/8 dev lo' (Linux) puis relance.",
            file=sys.stderr,
        )
        frontend.shutdown()
        return 1

    print(f"frontend : http://{_FRONTEND_ADDR[0]}:{_FRONTEND_ADDR[1]}/  (annonce backend via en-tete)")
    print(f"backend  : http://{_BACKEND_ADDR[0]}:{_BACKEND_ADDR[1]}/")
    print()
    print("Dans omega-deep : Analyser -> cible '127.0.0.1', profil 'web' -> Lancer.")
    print("Ctrl+C ici pour arreter les deux serveurs.")

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nArret des serveurs...")
    finally:
        frontend.shutdown()
        backend.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
