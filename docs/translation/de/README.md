<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT-Lizenz (siehe Datei LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-deep.png" alt="Omega-Deep" width="512">
</div>

# 🖧 OMEGA-DEEP

**Architekturanalyse über mehrere Ziele (Erkundung + Schutzgrenzen + Graph)**

> Entwickelt von [kraynux](https://github.com/kraynux) für [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Offizielle Seite: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Vorschau: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Oberfläche und exportierte Berichte in **17 Sprachen** verfügbar — siehe [Sprachen der Oberfläche](#sprachen-der-oberfläche).  
**Sprachen:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** übernimmt alles, was `omega-check` auf einem einzelnen Ziel tut (Port-Scan, Dienstidentifikation, Rollen, WAF, TLS), und ergänzt die **Erkundung weiterer Ziele** anhand der Hinweise, die das bereits gescannte Ziel hinterlässt (Header, Weiterleitungen, Zertifikat, HTML-Links) — unter **strengen Schutzgrenzen** und mit **ausdrücklicher Bestätigung durch den Nutzer**, bevor ein entdecktes Ziel gescannt wird —, und **rekonstruiert anschließend einen Architekturgraphen** (wer mit wem spricht, mit welchem Vertrauen). Werkzeug der Suite `omega-`, aufgebaut nach Clean Architecture — siehe `docs/ARCHITECTURE.md` für alle technischen Details.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-deep/D.png" width="24%" />
</p>

## 1. Vision und Umfang

Omega-deep beantwortet eine Frage, die omega-check nicht stellt: *Was steckt sonst noch hinter dieser IP?* Ein Reverse Proxy, der sein Backend ankündigt, ein Zertifikat für mehrere Hosts, eine Seite, die auf einen benachbarten Dienst verweist — lauter Hinweise, denen omega-deep folgt, vorsichtig und nie eigenmächtig.

### Was Omega-deep tut

- Scannt ein Wurzelziel genau wie omega-check (Systemprofil oder gespeichertes persönliches Profil).
- Erkundet Kandidatenziele anhand der Hinweise, die jeder bereits gescannte Host hinterlässt: HTTP-Header (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), Weiterleitung (`Location`), TLS-Zertifikat (SAN), HTML-Links — siehe [§4](#4-erkundung-von-zielen-und-schutzgrenzen).
- Scannt ein entdecktes Ziel **nie** ohne ausdrückliche Bestätigung, Ziel für Ziel — Schweigen ist nie eine Zustimmung.
- Begrenzt die Erkundung durch strenge Schutzgrenzen: maximale Tiefe, maximale Zahl zusätzlicher Ziele, erlaubtes Subnetz (standardmäßig derselbe private Bereich wie die Wurzel).
- Rekonstruiert einen **Architekturgraphen** aus der Herkunft jedes akzeptierten Ziels (`proxy_to`, `redirect_to`, `linked_to`), mit einer Vertrauensstufe pro Beziehung — siehe [§8](#8-architekturgraph).
- Zeigt das Ergebnis in der TUI (Textual) oder in der skriptfähigen CLI, mit denselben drei Exporten wie omega-check (JSON, Text, HTML mit 5 Themes) — der Graph ist dort ein **echtes gezeichnetes Diagramm** in HTML, keine Tabelle.
- Versieht jede gesammelte Information (Dienst wie Erkundung) mit einer ausdrücklichen Vertrauensstufe — siehe [§9](#9-vertrauensrichtlinie).
- Führt einen dauerhaften Verlauf der Analysen, der wiederholt und über die Zeit verglichen werden kann.

### Was Omega-deep nicht tut

- Aktives Schwachstellen-Scannen: kein SQLi, XSS oder RCE.
- CVE-Scannen.
- Betriebssystem-Fingerprinting.
- Low-Level-Scantechniken im Stil von nmap (SYN-Scan, Rohpakete) — nur TCP-Verbindungen auf Anwendungsebene.
- Brute-Force- oder Fuzzing-Werkzeug.
- Ein entdecktes Ziel ohne ausdrückliche Bestätigung des Nutzers scannen — nie, in keinem Modus.
- Erkundung über das private Subnetz des Ausgangsziels hinaus, außer bei ausdrücklicher Konfiguration (`--subnet`).
- Web-Dashboard.

## 2. Installation

### Voraussetzungen

- Python 3.10+
- Internetverbindung, für die Abhängigkeiten

### Installation

```bash
[ -d omega-deep ] && echo "ℹ️ Hier bereits entpackt, Schritt übersprungen." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Legt die virtuelle Umgebung `.venv` an, falls sie noch nicht existiert.
2. Installiert die Abhängigkeiten (`vendor/omega-lib/`, dann `pip install -e .`; `pyproject.toml` bleibt die einzige maßgebliche Quelle).
3. Macht `omega-deep.sh` und `install.sh` ausführbar.
4. Fügt den Alias `deep` zu `~/.bashrc` und `~/.zshrc` hinzu (ohne Duplikat, falls schon vorhanden).

### Abhängigkeiten

Deklariert in `pyproject.toml` (kein `requirements.txt` mehr):
- `omega-lib`: gemeinsame Bibliothek der Suite (`ConfidenceLevel`, Themes, Terminalerkennung) — mitgeliefert in `vendor/omega-lib/`
- `textual`: TUI-Oberfläche, Themes, automatische Anpassung an das Terminal
- `httpx`: HTTP/HTTPS-Sonden (Dienst und Erkundung)
- `cryptography`: Auslesen des ausgehandelten TLS-Zertifikats
- `jinja2`: Templates für den HTML-Export
- Entwicklungsabhängigkeiten (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Verwendung

### Interaktiver Modus (TUI)

Empfohlen für den täglichen Gebrauch — ohne Argumente gestartet:

```bash
./omega-deep.sh
```
wenn Sie den Alias angelegt haben, tippen Sie einfach `deep` im Terminal:
```bash
deep
```

Ablauf: Startbildschirm (schließt sich per Tastendruck oder Klick) → Hauptmenü (Analysieren / Profile / Verlauf / Einstellungen / Hilfe) → Eingabe des Wurzelziels, Wahl des Profils und der Schutzgrenzen der Erkundung (maximale Tiefe, maximale Zahl von Zielen, erlaubtes Subnetz) → Analyse (unbestimmte Fortschrittsanzeige und Live-Protokoll der Netzwerkvorgänge) → für jede Gruppe entdeckter Ziele ein Bestätigungsbildschirm (eine Zeile pro Ziel mit Quelle/Vertrauen/Beleg, Umschalter Annehmen/Ablehnen — standardmäßig nichts ausgewählt) → Analyse-Details (Hosts, Ports/Dienste/Rollen, Graph, Export) → Verlauf/Vergleich/Wiederholung und Einstellungen über das Hauptmenü. Die Anpassung an das Terminal (Farben, Größe, strukturelle Reduzierung) erfolgt automatisch.

#### Tastenkürzel

| Taste | Aktion |
|---|---|
| `↑` / `↓` | Zwischen den Elementen eines Bildschirms wechseln |
| `Tab` / `Umschalt+Tab` | Zwischen den Feldern eines Formulars wechseln |
| `Esc` | Zurück zum vorherigen Bildschirm (Bestätigung zum Beenden auf dem Startbildschirm) |
| `t` | Nächstes Theme (sofort angewendet, ohne Bestätigung) |
| `r` | Terminalerkennung aktualisieren |
| `a` | Hilfe anzeigen |
| `q` | Beenden (mit Bestätigung) |

### Sprachen der Oberfläche

Die Oberfläche ist in 17 Sprachen verfügbar: Französisch, Englisch, Spanisch, Portugiesisch (Brasilien), Italienisch, Deutsch, Niederländisch, Polnisch, Russisch, vereinfachtes Chinesisch, Vietnamesisch, Thailändisch, Indonesisch, Japanisch, Koreanisch, Hindi und Arabisch. Die Auswahl erfolgt in den Einstellungen („Langue / Language“) und gilt nach einem Neustart der Oberfläche; die Variable `OMEGA_DEEP_LANG` (zum Beispiel `OMEGA_DEEP_LANG=de ./omega-deep.sh`) erzwingt eine Sprache für eine Sitzung. Aus omega-suite gestartet, übernimmt omega-deep die Sprache der Suite. Auf einer Linux-Textkonsole (TTY) werden Sprachen mit nicht lateinischer Schrift für die Sitzung auf Englisch angezeigt. Die Kommandozeile bleibt auf Französisch.

### Kontakt und Support

Die Hilfe (Taste `a`) bietet einen Bildschirm **Kontakt und Support**: *Einen Kaffee spendieren* (PayPal-Seite des Entwicklers), *Support kontaktieren* (E-Mail-Adresse und Kontaktformular der Website, im Klartext angezeigt), *Mich als Nutzer melden (anonym)* und *Updates prüfen*. Die Meldung ist freiwillig, standardmäßig deaktiviert und wird nur ein einziges Mal gesendet: Sie dient nur dazu, die Nutzer zu zählen und, wenn gewünscht, ihren Kontinent oder ihr Land (geschlossene Listen, nie Freitext). Gesendet werden ein zufällig gezogener Schlüssel, der Name der Software (`omega-deep`) und ihre Version; nie ein Name, ein Rechnername, eine Einstellung, ein Ziel oder ein Ergebnis. Die IP-Adresse wird in den Meldungen nicht gespeichert, durchläuft aber wie jeder Besuch die Sicherheitsprüfungen und das Protokoll des Empfangsservers. Rückzug jederzeit über denselben Bildschirm (*Mich nicht mehr melden*). Die Update-Prüfung liest nur die Liste der auf der Website veröffentlichten Versionen, und nie ohne Klick.

### Skriptfähiger Modus (CLI)

Jeder Unterbefehl aktiviert den CLI-Modus:

```bash
# Ein Ziel analysieren (Wurzel-Scan + Erkundung mehrerer Ziele)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Verlauf (nach Wurzelziel filterbar)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Details einer Analyse (Text, JSON oder HTML) — 5 Export-Themes zur Auswahl
./omega-deep.sh show <scan_id> --format html --theme omega-base --output bericht.html

# Zwei Analysen vergleichen (Portzustand des Wurzelziels)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Persönliche Portprofile
./omega-deep.sh profile list
./omega-deep.sh profile create labor --ports 22,80,443 --description "Mein Profil"
./omega-deep.sh profile edit labor --ports 22,80,443,8080
./omega-deep.sh profile pin labor
./omega-deep.sh profile unpin labor
./omega-deep.sh profile delete labor
```

In der CLI werden entdeckte Ziele über eine interaktive Frage pro Ziel bestätigt (`Scanner <cible> ? [o/N]`, auf Französisch wie die übrige Kommandozeile), wobei vor jeder Frage der Beleg angezeigt wird. `--auto-validate` nimmt alles ohne Prüfung an (**nicht empfohlen**, es erscheint eine Warnung); in einer nicht interaktiven Umgebung (kein TTY, kein `--auto-validate`) wird jedes entdeckte Ziel standardmäßig abgelehnt, statt ohne Bestätigung gescannt zu werden.

### Akzeptierte Zielformate

```text
192.168.1.10                IPv4
example.org                 Hostname
http://example.org          HTTP-URL  (Schema vor der Auflösung entfernt)
https://example.org:8443    HTTPS-URL mit Port  (Schema und Port entfernt)
```

Schema und gegebenenfalls Port werden vor der DNS-Auflösung entfernt (`domain/targets/validation.py::normalize_target_input`) — eine komplette URL einzufügen funktioniert, nur der Host bleibt erhalten. *Entdeckte* Ziele werden auf dieselbe Weise normalisiert, aber nie ohne Bestätigung gescannt (siehe [§4](#4-erkundung-von-zielen-und-schutzgrenzen)).

## 4. Erkundung von Zielen und Schutzgrenzen

### Quellen der Hinweise

| Quelle | Herkunft | Vertrauen |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | `Location`-Header einer HTTP-Antwort | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) des ausgehandelten TLS-Zertifikats | `DECLARED` |
| `html_link` | Von der Seite ausgelieferte Links (`<a href>`) | `INFERRED` |

Ein `DECLARED`-Wert bleibt eine Selbstauskunft des Ziels (fälschbar) — siehe [§10](#10-schutz-vor-gefälschten-werten). `html_link` ist bewusst die schwächste Quelle: Ein bloßer Link erklärt keine Infrastrukturbeziehung.

### Schutzgrenzen (immer aktiv, nie abschaltbar)

- **Perimeter**: Ein Kandidatenziel muss eine private IP im selben `/24` wie das Wurzelziel sein, außer bei ausdrücklichem `--subnet` (dann zählt nur die Zugehörigkeit zum angegebenen Subnetz, selbst wenn es öffentliche IPs umfasst — die ausdrückliche Konfiguration erlaubt die Ausnahme). Ein nicht aufgelöster Hostname wird von diesem Filter nie akzeptiert (ihn zur Prüfung aufzulösen wäre bereits eine Netzwerkaktion außerhalb dieser Prüfung).
- **Tiefe**: `--max-depth` (Standard 3) — höchstens A → B → C → D.
- **Zahl der Ziele**: `--max-targets` (Standard 10) — über alle Tiefen.

### Bestätigung (nie ein Scan ohne Zustimmung)

Jedes vorgeschlagene Ziel durchläuft `PROPOSED → PRESENTED → ACCEPTED` oder `REJECTED`. Die Regel ist **ausfallsicher**: Jedes nie ausdrücklich angenommene Ziel (Schweigen, geschlossener Bildschirm, Unterbrechung, Zeitüberschreitung, kein TTY) gilt als abgelehnt — nie umgekehrt. In der TUI listet ein eigener Bildschirm die Ziele einer Gruppe mit Beleg und Vertrauen, einem Umschalter Annehmen/Ablehnen pro Zeile, „alle annehmen“/„alle ablehnen“ und standardmäßiger Ablehnung aller mit Esc. In der CLI eine Frage pro Ziel; `--auto-validate` (nicht empfohlen) ist der einzige Weg, die Interaktivität zu umgehen.

## 5. Scan-Profile

| Profil | Beschreibung | Angeheftet |
|---|---|---|
| `minimal` | Ultraschneller Scan: SSH + HTTP + HTTPS (22, 80, 443) | ja |
| `classic` | Klassische Internet-/LAN-Dienste | ja |
| `web` | Webdienste und Alternativen | nein |
| `db` | Datenbanken und Datendienste | nein |
| `remote` | Fernzugriffe — Shell, Desktop, RustDesk | nein |
| `mail` | Maildienste | nein |
| `dns` | DNS-Dienste | nein |
| `iot` | IoT-Geräte, Kameras, Router, Hausautomation | nein |
| `dev` | Entwicklungs-/Laborumgebungen | nein |
| `docker` | Docker, Swarm und übliche Dienste in Containern | nein |
| `complet` | **Spontan erzeugt**: sortierte, duplikatfreie Vereinigung aller obigen Profile | nein |
| *persönliches Profil* | Im Bildschirm **Profile** (TUI) oder mit `profile create` (CLI) angelegt, zusammen mit den Systemprofilen aufgeführt, in der TUI mit `* ` gekennzeichnet | nein |

Das Profil gilt für das Wurzelziel **und** für jedes angenommene entdeckte Ziel — kein eigenes Profil pro Host. Vollständige Details, Validierungsregeln und Verwaltung der persönlichen Profile: `docs/PROFILES.md`.

## 6. Architektur

Omega-deep ist nach **Clean Architecture** aufgebaut (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), angelehnt an die Vorlage der Suite `omega-` (siehe `omega-scan`/`omega-check`) und bei jeder Änderung durch `import-linter` geprüft. Alle Details stehen in **`docs/ARCHITECTURE.md`**.

Sehr kurzer Überblick:

```text
src/omega_deep/
├── domain/          Reine Fachlogik: Scans, Ziele, Dienste, Profile, Berichte,
│                    discovery (vorgeschlagene Ziele, Zustandsautomat der Bestätigung),
│                    architecture (Graph, Beziehungsregeln)
├── application/     Anwendungsfälle (commands/queries) — darunter discover_targets,
│                    validate_targets, reconstruct_architecture (neu gegenüber omega-check)
├── ports/           Von der Anwendung erwartete Verträge (Sonden, darunter discovery_prober,
│                    Repositories, Exporter...)
├── infrastructure/  Konkrete Implementierungen (socket/httpx/cryptography, SQLite,
│                    SVG-Darstellung des Graphen — Textual ist NICHT hier)
├── interfaces/      tui/ (Textual) und cli/ (skriptfähig), mit strikter Funktionsgleichheit
├── app/             Zusammenbau (DependencyContainer, Bootstrap, Lebenszyklus)
├── core/, shared/   Übergreifendes Vokabular, fachfremde Hilfsmittel
└── plugins/         Struktur angelegt, leer (keine bestätigte Erweiterungsachse)
```

Entwurfsregeln:
- `domain/services/policies.py`: klassifiziert die bereits gesammelten Hinweise, greift nie aufs Netzwerk zu.
- `domain/discovery/policies.py`: Schutzgrenzen für Perimeter/Tiefe/Anzahl — reine Logik, ohne Netzwerk testbar.
- `domain/architecture/service.py`: rekonstruiert den Graphen aus der Herkunft, die jeder `Host` bereits trägt, stellt keine neue Anfrage.
- `infrastructure/network/` und `infrastructure/discovery/`: greifen aufs Netzwerk zu (Sockets, `httpx`, `cryptography`), bewerten nie.
- `interfaces/`: zeigt an, enthält keine Fachlogik — der Bestätigungsbildschirm für entdeckte Ziele ruft `validate_targets` auf und setzt die ausfallsichere Regel nicht selbst um.
- `infrastructure/exporters/`: lesen das Analyseergebnis (Scan, Hosts, Graph), berechnen nichts neu.

## 7. Dienstidentifikation und Rollen

### Erkannte Protokolle

| Protokoll | Sonde | Gesammelte Details |
|---|---|---|
| HTTP / HTTPS | `httpx` | `Server`-Banner, Authentifizierungs-Header |
| TLS | `cryptography` (ausgehandeltes Zertifikat, `CERT_NONE` eingeschlossen) | Version, Cipher, Subjekt/Aussteller des Zertifikats |
| SSH | Rohes Banner | Software und Version (z. B. `OpenSSH 10.4`) |
| VNC (RFB) | Vom Server angekündigte Sicherheitscodes | Unterstützte Authentifizierungsarten |
| Generisch | Rohes Banner auf einem nicht erkannten offenen Port | Vorsichtige Extraktion, keine aggressive Heuristik |

### Abgeleitete Rollen

Abgeleitet aus dem **tatsächlich ausgehandelten** Protokoll, nie aus einer Vermutung anhand der Portnummer:

| Rolle | Bedingung | Vertrauen |
|---|---|---|
| `Webserver` | HTTP/HTTPS-Protokoll bestätigt | `INFERRED` |
| `Shell-Zugang` | SSH-Protokoll bestätigt | `CORROBORATED` |
| `grafischer Zugang` | VNC-Protokoll bestätigt | `CORROBORATED` |
| `Datenbank` | Port im Bereich des Systemprofils `db` | `INFERRED` |

### Bekannte WAF-Signaturen

Erkannt über einen deklarativen Header (`server`, `x-sdk`) — Präsenz **vom Ziel deklariert**, nie unabhängig überprüft: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (zur Information aufgeführt, streng genommen keine Anwendungs-WAF).

## 8. Architekturgraph

Ausschließlich aus der Herkunft rekonstruiert, die jeder angenommene Host bereits trägt (`discovered_from`/`discovery_source`/`discovery_confidence`) — keine neue Netzwerkanfrage, keine erneute Auswertung der Rohhinweise.

### Erzeugte Beziehungen

| Beziehung | Erkundungsquelle | Bedeutung |
|---|---|---|
| `proxy_to` | `header` | Das Wurzelziel (oder ein bereits angenommener Host) ist vermutlich ein Proxy zum entdeckten Ziel |
| `redirect_to` | `redirection` | Beobachtete HTTP-Weiterleitung zum entdeckten Ziel |
| `linked_to` | `certificate` oder `html_link` | Die neutralste Beziehung — gemeinsame Infrastruktur/Anwendung, ohne behauptete Flussrichtung |

`backend_of` (die umgekehrte Kante eines `proxy_to`) wird bewusst nicht erzeugt — das wäre eine doppelte Information, keine neue Ableitung.

### Darstellung

- **TUI** (Analyse-Details) und **JSON-/Text-Exporte**: Liste der Kanten (Quelle, Beziehung, Ziel, Vertrauen) — ein Terminal ist nicht der Ort für eine reichhaltige grafische Darstellung.
- **HTML-Export**: ein **echtes SVG-Diagramm** (Knoten = Kreise, Kanten = beschriftete Pfeile), Schichtenlayout vom Wurzelziel aus berechnet, Größe proportional zur Zahl der entdeckten Maschinen — nie eine schwere Abhängigkeit für Graphlayout; der Graph bleibt konstruktionsbedingt klein (begrenzt durch die Schutzgrenzen aus [§4](#4-erkundung-von-zielen-und-schutzgrenzen)).

## 9. Vertrauensrichtlinie

Jedes gesammelte Feld trägt eine dieser Stufen:

| Stufe | Bedeutung |
|---|---|
| `VERIFIED` | Direkt beobachtete Protokolltatsache, die das Ziel nicht fälschen kann (z. B. geschlossener Port, durch TCP-RST bestätigt, tatsächlich ausgehandelte TLS-Version). |
| `DECLARED` | Vom Ziel selbst angekündigter Wert in einem Feld, das es vollständig kontrolliert (z. B. `Server`-Banner, `X-Backend-Server`-Header) — plausibel, aber beliebig fälschbar. |
| `CORROBORATED` | Ein `DECLARED`-Wert, der durch einen unabhängigen Hinweis bestätigt wird (z. B. SSH-Rolle, da das Protokoll tatsächlich ausgehandelt wurde). |
| `INFERRED` | Aus einem Muster/einer Heuristik abgeleitet, ohne ausdrückliche Angabe des Ziels (z. B. HTML-Link). |
| `UNKNOWN` | Kein verwertbarer Hinweis oder vom Ziel aktiv verborgen. |

## 10. Schutz vor gefälschten Werten

Omega-deep vertraut keinen vom Ziel selbst deklarierten Daten, ohne dies ausdrücklich zu kennzeichnen — und die Erkundung von Zielen ist der empfindlichste Teil des Projekts: Ein bösartiges Ziel *könnte* einen falschen `X-Backend-Server` ankündigen, um die Erkundung auf eine IP seiner Wahl zu lenken. Zwei strukturelle Schutzmaßnahmen, unabhängig voneinander:
- Keine von einem Ziel abgeleitete Information ist je `VERIFIED`, nur weil sie angekündigt wird — ein `Server`-Banner oder ein `X-Backend-Server`-Header bleibt `DECLARED`, so plausibel er auch ist.
- Die Perimeter-Schutzgrenze ([§4](#4-erkundung-von-zielen-und-schutzgrenzen)) begrenzt, wohin ein angekündigtes Ziel führen kann (dasselbe private `/24`, außer bei ausdrücklicher Konfiguration), und die Bestätigung durch den Nutzer bestimmt, ob es überhaupt gescannt wird — ein falsches Ziel außerhalb des Perimeters wird gar nicht erst vorgeschlagen; ein Ziel innerhalb des Perimeters bleibt vor jedem Scan an eine ausdrückliche Zustimmung gebunden.

## 11. Terminal-Kompatibilität

Die TUI (Textual) erkennt automatisch die Fähigkeiten des Terminals (Emulator, Größe) und passt ihr strukturelles Stylesheet entsprechend an (`complete`/`standard`/`reduced`/`mono`), ohne manuelle Option. Der CLI-Modus bleibt immer einfacher Text, unabhängig vom Terminal. Richtlinie der gesamten Suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil nach erkanntem Emulator

| Emulator | Anfangsprofil |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modernes SSH | `reduced` |
| Linux-TTY, älteres SSH | `mono` |
| Nicht erkannter Emulator | `reduced` (Standard-Rückfall) |

### Profil nach Terminalgröße

| Mindestgröße (Spalten × Zeilen) | Profil-Obergrenze |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| darunter | `mono` |

Das endgültige Profil ist **das strengere der beiden** (Emulator und Größe) — ein Ghostty im Vollbild, auf 70 Spalten verkleinert, fällt auf `mono` zurück, obwohl sein Emulator `complete` erlauben würde. Live aktualisierbar mit der Taste `r`.

## 12. Exporte

Text- und HTML-Berichte werden in der in den Einstellungen gewählten Sprache geschrieben („Sprache der Exporte“, standardmäßig die der Oberfläche); JSON bleibt Daten und wird nicht übersetzt. Die Berichte werden standardmäßig in `var/exports/` erzeugt (Laufzeitpfad im Projektordner verankert, mit `$OMEGA_DEEP_VAR_DIR` überschreibbar) oder unter dem angegebenen Pfad (`--output` in der CLI, Dialog in der TUI). Eindeutiger Dateiname mit Zeitstempel: `analyse-{profil}-{datum}.ext`, `analyse-custom-{datum}.ext` für ein persönliches Profil.

### JSON, die maßgebliche Quelle

Vollständige Struktur der Analyse (`Scan` + `Host[]` + `ArchitectureGraph`), streng JSON-serialisierbar, Vertrauensstufen eingeschlossen.

### Text, kompakter lesbarer Bericht

Außerhalb des Terminals lesbar, ohne ANSI-Codes — Graph als Liste von Kanten.

### HTML, eigenständiger Webbericht

5 Themes zur Auswahl (`--theme` in der CLI, Auswahlfeld in der TUI; folgt standardmäßig dem aktiven Oberflächen-Theme, wenn es eine Entsprechung gibt). Eigenes Layout: Container, Informationsraster, Statistikkästen pro Portzustand, farbige Abzeichen, **SVG-Diagramm des Architekturgraphen** (siehe [§8](#8-architekturgraph)) — dieselbe visuelle Familie wie `omega-scan`/`omega-check`.

## 13. Verlauf und Vergleich

Jede Analyse wird gespeichert (SQLite, `var/db/omega-deep.db`): Eine `scan_id` umfasst das Wurzelziel **und** alle entdeckten/angenommenen Hosts sowie den rekonstruierten Graphen. Verlauf nach Wurzelziel einsehbar (mit eigener Spalte für die Zahl entdeckter Ziele), Details einer früheren Analyse (Hosts + Graph), Vergleich zweier Analysen (Portzustand nur des **Wurzelziels** — Erkundungsgraphen zu vergleichen wäre eine mögliche Erweiterung, derzeit nicht nötig) und Wiederholung einer Analyse auf demselben Wurzelziel ohne erneute Eingabe.

## 14. Tests

```bash
source .venv/bin/activate
lint-imports        # prüft die Dependency Rule
pytest -q           # 191 Tests
ruff check src tests
mypy -p omega_deep
```

Struktur: `tests/unit/` (Domain und Anwendung, ohne echte E/A), `tests/integration/` (echte SQLite-Datenbank/Dateien, simulierter HTTP-Server `pytest-httpserver`, TLS über `trustme`), `tests/tui/` (Navigation über `Pilot`, strukturell — keine selbst behauptete visuelle Prüfung).

## 15. Außerhalb des Umfangs

- CVE-Scannen
- Aktive Erkennung von SQLi, XSS, RCE
- Betriebssystem-Fingerprinting
- Low-Level-Scantechniken im Stil von nmap (SYN-Scan, Rohpakete)
- Crawling
- Fuzzing
- Brute Force
- Ein entdecktes Ziel ohne ausdrückliche Bestätigung scannen — nie, in keinem Modus
- Erkundung außerhalb des privaten Subnetzes des Ausgangsziels ohne ausdrückliche Konfiguration
- Web-Dashboard

---

> Omega-deep — Erkunden, kartieren, einstufen, berichten.
> Eine Architektur, rekonstruiert mit ausdrücklichem Vertrauen, nie eine als Tatsache verkleidete Vermutung.
