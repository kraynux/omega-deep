<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT-licentie (zie het bestand LICENSE) -->
<div align="center">
  <img src="../../assets/omega-deep.png" alt="Omega-Deep" width="384">
</div>

# 🖧 OMEGA-DEEP

**Architectuuranalyse over meerdere doelen (ontdekking + veiligheidsgrenzen + graaf)**

> Gemaakt door [kraynux](https://github.com/kraynux) voor [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Officiële pagina: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Voorbeeld: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface en geëxporteerde rapporten beschikbaar in **17 talen** — zie [Talen van de interface](#talen-van-de-interface).  
**Talen:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** doet alles wat `omega-check` op één doel doet (poortscan, identificatie van diensten, rollen, WAF, TLS) en voegt daar de **ontdekking van extra doelen** aan toe op basis van de aanwijzingen die het al gescande doel achterlaat (headers, omleidingen, certificaat, HTML-links), onder **strikte veiligheidsgrenzen** en met een **uitdrukkelijke bevestiging door de gebruiker** voordat een ontdekt doel wordt gescand, en **reconstrueert daarna een architectuurgraaf** (wie praat met wie, met welk vertrouwen). Tool van de suite `omega-`, opgebouwd volgens Clean Architecture — zie `docs/ARCHITECTURE.md` voor alle technische details.

## 1. Visie en reikwijdte

Omega-deep beantwoordt een vraag die omega-check niet stelt: *wat zit er nog meer achter dit IP-adres?* Een reverse proxy die zijn backend aankondigt, een certificaat dat meerdere hosts dekt, een pagina die naar een naburige dienst wijst — evenveel aanwijzingen die omega-deep volgt, voorzichtig en nooit op eigen houtje.

### Wat Omega-deep doet

- Scant een hoofddoel precies zoals omega-check (systeemprofiel of opgeslagen persoonlijk profiel).
- Ontdekt kandidaat-doelen op basis van de aanwijzingen die elke al gescande host achterlaat: HTTP-headers (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), omleiding (`Location`), TLS-certificaat (SAN), HTML-links — zie [§4](#4-ontdekking-van-doelen-en-veiligheidsgrenzen).
- Scant een ontdekt doel **nooit** zonder uitdrukkelijke bevestiging, doel per doel — zwijgen is nooit instemming.
- Begrenst de ontdekking met strikte veiligheidsgrenzen: maximale diepte, maximaal aantal extra doelen, toegestaan subnet (standaard hetzelfde privébereik als het hoofddoel).
- Reconstrueert een **architectuurgraaf** uit de herkomst van elk geaccepteerd doel (`proxy_to`, `redirect_to`, `linked_to`), met een vertrouwensniveau per relatie — zie [§8](#8-architectuurgraaf).
- Toont het resultaat in de TUI (Textual) of in een scriptbare CLI, met dezelfde drie exports als omega-check (JSON, tekst, HTML met 5 thema's) — de graaf is daar een **echt getekend diagram** in HTML, geen tabel.
- Geeft elk verzameld gegeven (dienst of ontdekking) een expliciet vertrouwensniveau — zie [§9](#9-vertrouwensbeleid).
- Bewaart een blijvende geschiedenis van analyses, opnieuw uit te voeren en in de tijd te vergelijken.

### Wat Omega-deep niet doet

- Actief scannen op kwetsbaarheden: geen SQLi, XSS of RCE.
- CVE-scans.
- Herkenning van het besturingssysteem.
- Low-level scantechnieken in nmap-stijl (SYN-scan, ruwe pakketten) — alleen TCP-verbindingen op applicatieniveau.
- Brute-force- of fuzzingtool.
- Een ontdekt doel scannen zonder uitdrukkelijke bevestiging van de gebruiker — nooit, in geen enkele modus.
- Ontdekking buiten het privésubnet van het oorspronkelijke doel, behalve bij uitdrukkelijke configuratie (`--subnet`).
- Webdashboard.

## 2. Installatie

### Vereisten

- Python 3.10+
- Internetverbinding, voor de afhankelijkheden

### Installatie

```bash
[ -d omega-deep ] && echo "ℹ️ Hier al uitgepakt, stap overgeslagen." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Maakt de virtuele omgeving `.venv` aan als die nog niet bestaat.
2. Installeert de afhankelijkheden (`vendor/omega-lib/` en daarna `pip install -e .`; `pyproject.toml` blijft de enige bron van waarheid).
3. Maakt `omega-deep.sh` en `install.sh` uitvoerbaar.
4. Voegt de alias `deep` toe aan `~/.bashrc` en `~/.zshrc` (zonder dubbel als hij er al staat).

### Afhankelijkheden

Gedeclareerd in `pyproject.toml` (geen `requirements.txt` meer):
- `omega-lib`: gedeelde bibliotheek van de suite (`ConfidenceLevel`, thema's, terminaldetectie) — meegeleverd in `vendor/omega-lib/`
- `textual`: TUI-interface, thema's, automatische aanpassing aan de terminal
- `httpx`: HTTP/HTTPS-sondes (dienst en ontdekking)
- `cryptography`: uitlezen van het onderhandelde TLS-certificaat
- `jinja2`: templates voor de HTML-export
- Ontwikkelafhankelijkheden (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Gebruik

### Interactieve modus (TUI)

Aanbevolen voor dagelijks gebruik — gestart zonder argumenten:

```bash
./omega-deep.sh
```
als u de alias hebt aangemaakt, typ dan gewoon `deep` in de terminal:
```bash
deep
```

Verloop: startscherm (sluit met een toets of een klik) → hoofdmenu (Analyseren / Profielen / Geschiedenis / Instellingen / Help) → invoer van het hoofddoel, keuze van het profiel en de veiligheidsgrenzen voor ontdekking (maximale diepte, maximaal aantal doelen, toegestaan subnet) → analyse (onbepaalde voortgangsbalk en live verslag van de netwerkbewerkingen) → voor elke groep ontdekte doelen een bevestigingsscherm (één regel per doel, met bron/vertrouwen/bewijs zichtbaar, schakelaar accepteren/weigeren — standaard niets aangevinkt) → details van de analyse (hosts, poorten/diensten/rollen, graaf, export) → geschiedenis/vergelijking/opnieuw uitvoeren en instellingen vanuit het hoofdmenu. De aanpassing aan de terminal (kleuren, grootte, structurele vereenvoudiging) gebeurt automatisch.

#### Sneltoetsen

| Toets | Actie |
|---|---|
| `↑` / `↓` | Tussen de elementen van een scherm bewegen |
| `Tab` / `Shift+Tab` | Tussen de velden van een formulier bewegen |
| `Esc` | Terug naar het vorige scherm (bevestiging om af te sluiten op het startscherm) |
| `t` | Volgend thema (direct toegepast, zonder bevestiging) |
| `r` | Terminaldetectie vernieuwen |
| `a` | Help tonen |
| `q` | Afsluiten (met bevestiging) |

### Talen van de interface

De interface is beschikbaar in 17 talen: Frans, Engels, Spaans, Portugees (Brazilië), Italiaans, Duits, Nederlands, Pools, Russisch, vereenvoudigd Chinees, Vietnamees, Thai, Indonesisch, Japans, Koreaans, Hindi en Arabisch. De keuze gebeurt in de Instellingen („Langue / Language”) en geldt na een herstart van de interface; de variabele `OMEGA_DEEP_LANG` (bijvoorbeeld `OMEGA_DEEP_LANG=nl ./omega-deep.sh`) legt voor één sessie een taal op. Gestart vanuit omega-suite neemt omega-deep de taal van de suite over. Op een Linux-tekstconsole (TTY) worden talen met een niet-Latijns schrift voor die sessie in het Engels getoond. De opdrachtregel blijft in het Frans.

### Scriptbare modus (CLI)

Elke subopdracht activeert de CLI-modus:

```bash
# Een doel analyseren (scan van het hoofddoel + ontdekking van meerdere doelen)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Geschiedenis (te filteren op hoofddoel)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Details van een analyse (tekst, JSON of HTML) — keuze uit 5 exportthema's
./omega-deep.sh show <scan_id> --format html --theme omega-base --output rapport.html

# Twee analyses vergelijken (poortstatus van het hoofddoel)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Persoonlijke poortprofielen
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "Mijn profiel"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

In de CLI worden ontdekte doelen bevestigd via één interactieve vraag per doel (`Scanner <cible> ? [o/N]`, in het Frans zoals de rest van de opdrachtregel), waarbij vóór elke vraag het bewijs wordt getoond. `--auto-validate` accepteert alles zonder controle (**afgeraden**, er verschijnt een waarschuwing); in een niet-interactieve omgeving (geen TTY, geen `--auto-validate`) wordt elk ontdekt doel standaard geweigerd in plaats van zonder bevestiging gescand.

### Geaccepteerde doelformaten

```text
192.168.1.10                IPv4
example.org                 Hostnaam
http://example.org          HTTP-URL  (schema verwijderd vóór de resolutie)
https://example.org:8443    HTTPS-URL met poort  (schema en poort verwijderd)
```

Het schema en een eventuele poort worden vóór de DNS-resolutie verwijderd (`domain/targets/validation.py::normalize_target_input`) — een volledige URL plakken werkt, alleen de host blijft over. *Ontdekte* doelen worden op dezelfde manier genormaliseerd, maar nooit zonder bevestiging gescand (zie [§4](#4-ontdekking-van-doelen-en-veiligheidsgrenzen)).

## 4. Ontdekking van doelen en veiligheidsgrenzen

### Bronnen van aanwijzingen

| Bron | Herkomst | Vertrouwen |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | `Location`-header van een HTTP-antwoord | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) van het onderhandelde TLS-certificaat | `DECLARED` |
| `html_link` | Links (`<a href>`) die de pagina serveert | `INFERRED` |

Een `DECLARED`-waarde blijft een zelfverklaring van het doel (vervalsbaar) — zie [§10](#10-bescherming-tegen-vervalste-waarden). `html_link` is bewust de zwakste bron: een gewone link verklaart geen enkele infrastructuurrelatie.

### Veiligheidsgrenzen (altijd actief, nooit uit te schakelen)

- **Perimeter**: een kandidaat-doel moet een privé-IP zijn in hetzelfde `/24` als het hoofddoel, behalve bij uitdrukkelijk `--subnet` (dan telt alleen het lidmaatschap van het opgegeven subnet, ook als dat publieke IP-adressen omvat — de uitdrukkelijke configuratie staat de uitzondering toe). Een niet-opgeloste hostnaam wordt door dit filter nooit geaccepteerd (hem oplossen om te controleren zou al een netwerkactie buiten deze controle zijn).
- **Diepte**: `--max-depth` (standaard 3) — hoogstens A → B → C → D.
- **Aantal doelen**: `--max-targets` (standaard 10) — over alle diepten.

### Bevestiging (nooit een scan zonder akkoord)

Elk voorgesteld doel doorloopt `PROPOSED → PRESENTED → ACCEPTED` of `REJECTED`. De regel is **faalveilig**: elk doel dat nooit uitdrukkelijk is geaccepteerd (zwijgen, scherm gesloten, onderbreking, time-out, geen TTY) wordt als geweigerd behandeld — nooit andersom. In de TUI toont een apart scherm de doelen van een groep met bewijs en vertrouwen, een schakelaar accepteren/weigeren per regel, „alles accepteren”/„alles weigeren”, en standaard een volledige weigering met Esc. In de CLI één vraag per doel; `--auto-validate` (afgeraden) is de enige manier om de interactiviteit te omzeilen.

## 5. Scanprofielen

| Profiel | Beschrijving | Vastgepind |
|---|---|---|
| `minimal` | Supersnelle scan: SSH + HTTP + HTTPS (22, 80, 443) | ja |
| `classic` | Klassieke internet-/LAN-diensten | ja |
| `web` | Webdiensten en alternatieven | nee |
| `db` | Databases en datadiensten | nee |
| `remote` | Toegang op afstand — shell, bureaublad, RustDesk | nee |
| `mail` | Maildiensten | nee |
| `dns` | DNS-diensten | nee |
| `iot` | IoT-apparaten, camera's, routers, domotica | nee |
| `dev` | Ontwikkel-/labomgevingen | nee |
| `docker` | Docker, Swarm en gangbare diensten in containers | nee |
| `complet` | **Ter plekke gegenereerd**: gesorteerde, ontdubbelde vereniging van alle bovenstaande profielen | nee |
| *persoonlijk profiel* | Aangemaakt in het scherm **Profielen** (TUI) of met `profile create` (CLI), getoond naast de systeemprofielen, in de TUI voorafgegaan door `* ` | nee |

Het profiel geldt voor het hoofddoel **en** voor elk geaccepteerd ontdekt doel — geen ander profiel per host. Volledige details, validatieregels en beheer van de persoonlijke profielen: `docs/PROFILES.md`.

## 6. Architectuur

Omega-deep is opgebouwd volgens **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), afgestemd op het sjabloon van de suite `omega-` (zie `omega-scan`/`omega-check`) en bij elke wijziging gecontroleerd door `import-linter`. Alle details staan in **`docs/ARCHITECTURE.md`**.

Zeer kort overzicht:

```text
src/omega_deep/
├── domain/          Pure bedrijfslogica: scans, doelen, diensten, profielen, rapporten,
│                    discovery (voorgestelde doelen, toestandsmachine voor bevestiging),
│                    architecture (graaf, relatieregels)
├── application/     Use cases (commands/queries) — waaronder discover_targets,
│                    validate_targets, reconstruct_architecture (nieuw ten opzichte van omega-check)
├── ports/           Contracten die de applicatie verwacht (sondes, waaronder discovery_prober,
│                    repositories, exporteurs...)
├── infrastructure/  Concrete implementaties (socket/httpx/cryptography, SQLite,
│                    SVG-weergave van de graaf — Textual staat hier NIET)
├── interfaces/      tui/ (Textual) en cli/ (scriptbaar), met strikte functionele gelijkwaardigheid
├── app/             Samenstelling (DependencyContainer, bootstrap, levenscyclus)
├── core/, shared/   Gedeeld vocabulaire, niet-bedrijfsmatige hulpmiddelen
└── plugins/         Structuur aanwezig, leeg (geen bevestigde uitbreidingsas)
```

Ontwerpregels:
- `domain/services/policies.py`: deelt de al verzamelde aanwijzingen in, doet nooit netwerkverkeer.
- `domain/discovery/policies.py`: veiligheidsgrenzen voor perimeter/diepte/aantal — pure logica, zonder netwerk te testen.
- `domain/architecture/service.py`: reconstrueert de graaf uit de herkomst die elke `Host` al meedraagt, doet geen nieuw verzoek.
- `infrastructure/network/` en `infrastructure/discovery/`: doen het netwerkverkeer (sockets, `httpx`, `cryptography`), oordelen nooit.
- `interfaces/`: toont, bevat geen bedrijfslogica — het bevestigingsscherm voor ontdekte doelen roept `validate_targets` aan en implementeert de faalveilige regel niet zelf.
- `infrastructure/exporters/`: lezen het analyseresultaat (scan, hosts, graaf), herberekenen niets.

## 7. Identificatie van diensten en rollen

### Herkende protocollen

| Protocol | Sonde | Verzamelde details |
|---|---|---|
| HTTP / HTTPS | `httpx` | `Server`-banner, authenticatieheaders |
| TLS | `cryptography` (onderhandeld certificaat, `CERT_NONE` inbegrepen) | Versie, cipher, onderwerp/uitgever van het certificaat |
| SSH | Ruwe banner | Software en versie (bijv. `OpenSSH 10.4`) |
| VNC (RFB) | Door de server aangekondigde beveiligingscodes | Ondersteunde authenticatietypen |
| Generiek | Ruwe banner op een niet herkende open poort | Voorzichtige extractie, geen agressieve heuristiek |

### Afgeleide rollen

Afgeleid uit het **werkelijk onderhandelde** protocol, nooit uit een aanname op basis van het poortnummer:

| Rol | Voorwaarde | Vertrouwen |
|---|---|---|
| `webserver` | HTTP/HTTPS-protocol bevestigd | `INFERRED` |
| `shelltoegang` | SSH-protocol bevestigd | `CORROBORATED` |
| `grafische toegang` | VNC-protocol bevestigd | `CORROBORATED` |
| `database` | Poort binnen het bereik van het systeemprofiel `db` | `INFERRED` |

### Bekende WAF-handtekeningen

Herkend via een declaratieve header (`server`, `x-sdk`) — aanwezigheid **gedeclareerd door het doel**, nooit onafhankelijk geverifieerd: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (ter informatie vermeld, strikt genomen geen applicatie-WAF).

## 8. Architectuurgraaf

Uitsluitend gereconstrueerd uit de herkomst die elke geaccepteerde host al meedraagt (`discovered_from`/`discovery_source`/`discovery_confidence`) — geen nieuw netwerkverzoek, geen nieuwe analyse van de ruwe aanwijzingen.

### Geproduceerde relaties

| Relatie | Ontdekkingsbron | Betekenis |
|---|---|---|
| `proxy_to` | `header` | Het hoofddoel (of een al geaccepteerde host) is waarschijnlijk een proxy naar het ontdekte doel |
| `redirect_to` | `redirection` | Waargenomen HTTP-omleiding naar het ontdekte doel |
| `linked_to` | `certificate` of `html_link` | De meest neutrale relatie — gedeelde infrastructuur/applicatie, zonder bewering over de richting van het verkeer |

`backend_of` (de omgekeerde rand van een `proxy_to`) wordt bewust niet geproduceerd — dat zou dubbele informatie zijn, geen nieuwe afleiding.

### Weergave

- **TUI** (details van een analyse) en **JSON-/tekstexports**: lijst van randen (bron, relatie, doel, vertrouwen) — een terminal is niet de plek voor een rijke grafische weergave.
- **HTML-export**: een **echt SVG-diagram** (knooppunten = cirkels, randen = gelabelde pijlen), gelaagde opmaak berekend vanaf het hoofddoel, grootte evenredig aan het aantal ontdekte machines — nooit een zware afhankelijkheid voor graafopmaak; de graaf blijft door zijn opzet klein (begrensd door de veiligheidsgrenzen van [§4](#4-ontdekking-van-doelen-en-veiligheidsgrenzen)).

## 9. Vertrouwensbeleid

Elk verzameld veld draagt een van deze niveaus:

| Niveau | Betekenis |
|---|---|
| `VERIFIED` | Direct waargenomen protocolfeit dat het doel niet kan vervalsen (bijv. gesloten poort bevestigd door een TCP-RST, werkelijk onderhandelde TLS-versie). |
| `DECLARED` | Waarde die het doel zelf aankondigt in een veld dat het volledig beheert (bijv. `Server`-banner, `X-Backend-Server`-header) — aannemelijk maar naar believen te vervalsen. |
| `CORROBORATED` | Een `DECLARED`-waarde bevestigd door een onafhankelijke aanwijzing (bijv. SSH-rol, omdat het protocol werkelijk onderhandeld is). |
| `INFERRED` | Afgeleid uit een patroon/heuristiek, zonder uitdrukkelijke declaratie van het doel (bijv. HTML-link). |
| `UNKNOWN` | Geen bruikbare aanwijzing, of actief verborgen door het doel. |

## 10. Bescherming tegen vervalste waarden

Omega-deep vertrouwt geen enkel door het doel zelf gedeclareerd gegeven zonder dat uitdrukkelijk aan te geven — en de ontdekking van doelen is het gevoeligste deel van het project: een kwaadwillend doel *zou* een valse `X-Backend-Server` kunnen aankondigen om de ontdekking naar een IP-adres naar keuze te sturen. Twee structurele beschermingen, onafhankelijk van elkaar:
- Geen enkel van een doel afgeleid gegeven is ooit `VERIFIED` enkel omdat het wordt aangekondigd — een `Server`-banner of een `X-Backend-Server`-header blijft `DECLARED`, hoe aannemelijk ook.
- De perimetergrens ([§4](#4-ontdekking-van-doelen-en-veiligheidsgrenzen)) begrenst waarheen een aangekondigd doel kan leiden (hetzelfde privé-`/24`, behalve bij uitdrukkelijke configuratie), en de bevestiging door de gebruiker bepaalt of het überhaupt wordt gescand — een vals doel buiten de perimeter wordt niet eens voorgesteld; een doel binnen de perimeter blijft vóór elke scan aan uitdrukkelijke bevestiging onderworpen.

## 11. Compatibiliteit met terminals

De TUI (Textual) detecteert automatisch de mogelijkheden van de terminal (emulator, grootte) en past zijn structurele stijlblad daarop aan (`complete`/`standard`/`reduced`/`mono`), zonder handmatige optie. De CLI-modus blijft altijd platte tekst, onafhankelijk van de terminal. Beleid dat de hele suite `omega-` deelt (`omega-lib`, `terminal/policies.py`).

### Profiel volgens de gedetecteerde emulator

| Emulator | Beginprofiel |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, moderne SSH | `reduced` |
| Linux-TTY, oudere SSH | `mono` |
| Niet herkende emulator | `reduced` (standaard terugvaloptie) |

### Profiel volgens de grootte van de terminal

| Minimale grootte (kolommen × regels) | Profielplafond |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| kleiner | `mono` |

Het uiteindelijke profiel is **het strengste van de twee** (emulator en grootte) — een Ghostty op volledig scherm, verkleind tot 70 kolommen, zakt terug naar `mono`, ook al zou zijn emulator `complete` toestaan. Live te vernieuwen met de toets `r`.

## 12. Exports

Tekst- en HTML-rapporten worden geschreven in de taal die in de Instellingen gekozen is („Taal van de exports”, standaard die van de interface); JSON blijft data en wordt niet vertaald. De rapporten worden standaard aangemaakt in `var/exports/` (runtimepad verankerd in de projectmap, `$OMEGA_DEEP_VAR_DIR` om het te overschrijven), of op het opgegeven pad (`--output` in de CLI, dialoogvenster in de TUI). Duidelijke bestandsnaam met tijdstempel: `analyse-{profiel}-{datum}.ext`, `analyse-custom-{datum}.ext` voor een persoonlijk profiel.

### JSON, de bron van waarheid

Volledige structuur van de analyse (`Scan` + `Host[]` + `ArchitectureGraph`), strikt JSON-serialiseerbaar, vertrouwensniveaus inbegrepen.

### Tekst, compact leesbaar rapport

Leesbaar buiten de terminal, zonder ANSI-codes — graaf als lijst van randen.

### HTML, zelfstandig webrapport

5 thema's naar keuze (`--theme` in de CLI, keuzelijst in de TUI; volgt standaard het actieve interfacethema als er een equivalent bestaat). Eigen opmaak: container, informatieraster, statistiekvakken per poortstatus, gekleurde badges, **SVG-diagram van de architectuurgraaf** (zie [§8](#8-architectuurgraaf)) — dezelfde visuele familie als `omega-scan`/`omega-check`.

## 13. Geschiedenis en vergelijking

Elke analyse wordt opgeslagen (SQLite, `var/db/omega-deep.db`): één `scan_id` omvat het hoofddoel **en** alle ontdekte/geaccepteerde hosts, plus de gereconstrueerde graaf. Geschiedenis raadpleegbaar per hoofddoel (met een aparte kolom voor het aantal ontdekte doelen), details van een eerdere analyse (hosts + graaf), vergelijking tussen twee analyses (poortstatus van alleen het **hoofddoel** — ontdekkingsgrafen vergelijken zou een mogelijke uitbreiding zijn, voorlopig niet nodig) en opnieuw uitvoeren van een analyse op hetzelfde hoofddoel zonder het opnieuw in te voeren.

## 14. Tests

```bash
source .venv/bin/activate
lint-imports        # controleert de Dependency Rule
pytest -q           # 191 tests
ruff check src tests
mypy -p omega_deep
```

Structuur: `tests/unit/` (domein en applicatie, zonder echte I/O), `tests/integration/` (echte SQLite/bestanden, nagebootste HTTP-server `pytest-httpserver`, TLS via `trustme`), `tests/tui/` (navigatie via `Pilot`, structureel — geen zelf geclaimde visuele controle).

## 15. Buiten de reikwijdte

- CVE-scans
- Actieve detectie van SQLi, XSS, RCE
- Herkenning van het besturingssysteem
- Low-level scantechnieken in nmap-stijl (SYN-scan, ruwe pakketten)
- Crawling
- Fuzzing
- Brute force
- Een ontdekt doel scannen zonder uitdrukkelijke bevestiging — nooit, in geen enkele modus
- Ontdekking buiten het privésubnet van het oorspronkelijke doel zonder uitdrukkelijke configuratie
- Webdashboard

---

> Omega-deep — Ontdekken, in kaart brengen, kwalificeren, rapporteren.
> Een architectuur gereconstrueerd met expliciet vertrouwen, nooit een aanname vermomd als feit.
