<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-deep.png" alt="Omega-Deep" width="512">
</div>

# 🖧 OMEGA-DEEP

**Multi-target architecture analysis (discovery + safeguards + graph)**

> Built by [kraynux](https://github.com/kraynux) for [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Official page: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface and exported reports available in **17 languages** — see [Interface languages](#interface-languages).  
**Languages:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** does everything `omega-check` does on a single target (port scan, service identification, roles, WAF, TLS) and adds **discovery of further targets** from the clues left by the target already scanned (headers, redirects, certificate, HTML links), under **strict safeguards** and **explicit user validation** before any discovered target is scanned, then **rebuilds an architecture graph** (who talks to whom, with what confidence). A tool of the `omega-` suite, structured in Clean Architecture — see `docs/ARCHITECTURE.md` for the full technical details.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-deep/D.png" width="24%" />
</p>

## 1. Vision and scope

Omega-deep answers a question omega-check does not ask: *behind this IP, what else is there?* A reverse proxy announcing its backend, a certificate covering several hosts, a page pointing to a neighboring service — so many clues that omega-deep follows, carefully, never on its own.

### What Omega-deep does

- Scans a root target exactly like omega-check (system profile, or saved personal profile).
- Discovers candidate targets from the clues left by each host already scanned: HTTP headers (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), redirect (`Location`), TLS certificate (SAN), HTML links — see [§4](#4-target-discovery-and-safeguards).
- **Never** scans a discovered target without explicit validation, target by target — silence is never acceptance.
- Bounds discovery with strict safeguards: maximum depth, maximum number of extra targets, allowed subnet (same private range as the root by default).
- Rebuilds an **architecture graph** from the provenance of each accepted target (`proxy_to`, `redirect_to`, `linked_to`), with a confidence level per relation — see [§8](#8-architecture-graph).
- Presents the result in a TUI (Textual) or a scriptable CLI, with the same three exports as omega-check (JSON, text, HTML with 5 themes) — the graph there is a **real drawn diagram** in HTML, not a table.
- Gives every collected piece of information (service or discovery) an explicit confidence level — see [§9](#9-confidence-policy).
- Keeps a persistent history of analyses that can be replayed and compared over time.

### What Omega-deep does not do

- Active vulnerability scanning: no SQLi, XSS or RCE.
- CVE scanning.
- Operating system fingerprinting.
- Low-level nmap-style scanning techniques (SYN scan, raw packets) — application-level TCP connection only.
- Brute force or fuzzing tool.
- Scanning a discovered target without explicit user confirmation — never, in any mode.
- Discovery beyond the private subnet of the initial target, unless explicitly configured (`--subnet`).
- Web dashboard.

## 2. Installation

### Requirements

- Python 3.10+
- Internet connection, for the dependencies

### Installation

```bash
[ -d omega-deep ] && echo "ℹ️ Already extracted here, step skipped." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it does not already exist.
2. Installs the dependencies (`vendor/omega-lib/` then `pip install -e .`; `pyproject.toml` remains the single source of truth).
3. Makes `omega-deep.sh` and `install.sh` executable.
4. Adds the `deep` alias to `~/.bashrc` and `~/.zshrc` (no duplicate if already present).

### Dependencies

Declared in `pyproject.toml` (no more `requirements.txt`):
- `omega-lib`: the suite's shared library (`ConfidenceLevel`, themes, terminal detection) — vendored in `vendor/omega-lib/`
- `textual`: TUI interface, themes, automatic adaptation to the terminal
- `httpx`: HTTP/HTTPS probes (service and discovery)
- `cryptography`: reading of the negotiated TLS certificate
- `jinja2`: templating for the HTML export
- Development dependencies (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Usage

### Interactive mode (TUI)

Recommended for everyday use — launched without arguments:

```bash
./omega-deep.sh
```
if you created the alias, just type `deep` in the terminal:
```bash
deep
```

Flow: splash screen (closes on a key press or a click) → main menu (Analyze / Profiles / History / Settings / Help) → input of the root target, choice of profile and discovery safeguards (max depth, max number of targets, allowed subnet) → analysis (indeterminate gauge and live log of network operations) → for each batch of discovered targets, a validation screen (one row per target, with source/confidence/evidence shown, accept/reject toggle — nothing checked by default) → analysis details (hosts, ports/services/roles, graph, export) → history/comparison/replay and settings from the main menu. Adaptation to the terminal (colors, size, structural degradation) is automatic.

#### Keyboard shortcuts

| Key | Action |
|---|---|
| `↑` / `↓` | Move between the items of a screen |
| `Tab` / `Shift+Tab` | Move between the fields of a form |
| `Esc` | Back to the previous screen (exit confirmation on the home screen) |
| `t` | Next theme (applied immediately, no confirmation) |
| `r` | Refresh terminal detection |
| `a` | Show help |
| `q` | Quit (with confirmation) |

### Interface languages

The interface is available in 17 languages: French, English, Spanish, Portuguese (Brazil), Italian, German, Dutch, Polish, Russian, Simplified Chinese, Vietnamese, Thai, Indonesian, Japanese, Korean, Hindi and Arabic. The choice is made in Settings ("Langue / Language") and takes effect after the interface restarts; the `OMEGA_DEEP_LANG` variable (for example `OMEGA_DEEP_LANG=en ./omega-deep.sh`) forces a language for one session. When launched from omega-suite, omega-deep uses the suite's language. On a Linux text console (TTY), languages with a non-Latin script are shown in English for the session. The command line stays in French.

### Contact and support

Help (`a` key) offers a **Contact and support** screen: *Buy me a coffee* (the developer's PayPal page), *Contact support* (email address and the site's contact form, shown in plain text), *Declare myself as a user (anonymous)* and *Check for updates*. The declaration is voluntary, off by default and sent only once: it is used only to count users and, if you wish, their continent or country (closed lists, never free text). It sends a randomly drawn key, the software name (`omega-deep`) and its version; never a name, a machine name, a setting, a target or a result. The IP address is not stored in the declarations, but, like any visit, it goes through the security checks and the log of the receiving server. You can withdraw at any time from the same screen (*Stop declaring me*). The update check only reads the list of versions published on the site, and never without a click.

### Scriptable mode (CLI)

Any subcommand triggers CLI mode:

```bash
# Analyze a target (root scan + multi-target discovery)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# History (can be filtered by root target)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Analysis details (text, JSON or HTML) — choice of 5 export themes
./omega-deep.sh show <scan_id> --format html --theme omega-base --output report.html

# Compare two analyses (port state of the root target)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Personal port profiles
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "My profile"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

In the CLI, discovered targets are validated through one interactive question per target (`Scanner <cible> ? [o/N]`, in French like the rest of the command line), with the evidence shown before each question. `--auto-validate` accepts everything without review (**not recommended**, a warning is shown); in a non-interactive environment (no TTY, `--auto-validate` absent), every discovered target is rejected by default rather than scanned without confirmation.

### Accepted target formats

```text
192.168.1.10                IPv4
example.org                 Hostname
http://example.org          HTTP URL  (scheme removed before resolution)
https://example.org:8443    HTTPS URL with port  (scheme and port removed)
```

Any scheme and port are removed before DNS resolution (`domain/targets/validation.py::normalize_target_input`) — pasting a whole URL works, only the host is kept. *Discovered* targets are normalized the same way but are never scanned without validation (see [§4](#4-target-discovery-and-safeguards)).

## 4. Target discovery and safeguards

### Clue sources

| Source | Origin | Confidence |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | `Location` header of an HTTP response | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) of the negotiated TLS certificate | `DECLARED` |
| `html_link` | Links (`<a href>`) served by the page | `INFERRED` |

A `DECLARED` value remains a self-declaration of the target (forgeable) — see [§10](#10-protection-against-forged-values). `html_link` is deliberately the weakest source: a mere link declares no infrastructure relation.

### Safeguards (always active, never disableable)

- **Perimeter**: a candidate target must be a private IP in the same `/24` as the root target, unless `--subnet` is given explicitly (in which case only membership of the given subnet counts, even if it covers public IPs — the explicit configuration is what authorizes the exception). An unresolved hostname is never accepted by this filter (resolving it to check would already be a network action beyond the scope of this check).
- **Depth**: `--max-depth` (default 3) — A → B → C → D at most.
- **Number of targets**: `--max-targets` (default 10) — across all depths.

### Validation (never a scan without confirmation)

Each proposed target goes `PROPOSED → PRESENTED → ACCEPTED` or `REJECTED`. The rule is **fail-safe**: any target never explicitly accepted (silence, screen closed, interruption, timeout, no TTY) is treated as rejected — never the other way round. In the TUI, a dedicated screen lists the targets of a batch with evidence and confidence, an accept/reject toggle per row, "accept all"/"reject all", and full rejection by default on Esc. In the CLI, one question per target; `--auto-validate` (not recommended) is the only way to bypass interactivity.

## 5. Scan profiles

| Profile | Description | Pinned |
|---|---|---|
| `minimal` | Ultra-fast scan: SSH + HTTP + HTTPS (22, 80, 443) | yes |
| `classic` | Classic Internet/LAN services | yes |
| `web` | Web services and alternatives | no |
| `db` | Databases and data services | no |
| `remote` | Remote access — shell, desktop, RustDesk | no |
| `mail` | Mail services | no |
| `dns` | DNS services | no |
| `iot` | IoT devices, cameras, routers, home automation | no |
| `dev` | Development/lab environments | no |
| `docker` | Docker, Swarm and common containerized services | no |
| `complet` | **Generated on the fly**: sorted, deduplicated union of all the profiles above | no |
| *personal profile* | Created in the **Profiles** screen (TUI) or with `profile create` (CLI), listed alongside the system profiles, prefixed with `* ` in the TUI | no |

The profile applies to the root target **and** to every accepted discovered target — no different profile per host. Full details, validation rules and management of personal profiles: `docs/PROFILES.md`.

## 6. Architecture

Omega-deep is structured in **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), aligned with the `omega-` suite template (see `omega-scan`/`omega-check`) and verified by `import-linter` on every change. The full details live in **`docs/ARCHITECTURE.md`**.

Very short overview:

```text
src/omega_deep/
├── domain/          Pure business logic: scans, targets, services, profiles, reports,
│                    discovery (proposed targets, validation state machine),
│                    architecture (graph, relation rules)
├── application/     Use cases (commands/queries) — including discover_targets,
│                    validate_targets, reconstruct_architecture (new vs. omega-check)
├── ports/           Contracts expected by the application (probers, including discovery_prober,
│                    repositories, exporters...)
├── infrastructure/  Concrete implementations (socket/httpx/cryptography, SQLite,
│                    SVG rendering of the graph — Textual is NOT here)
├── interfaces/      tui/ (Textual) and cli/ (scriptable), with strict feature parity
├── app/             Assembly (DependencyContainer, bootstrap, lifecycle)
├── core/, shared/   Cross-cutting vocabulary, non-business utilities
└── plugins/         Structure in place, empty (no confirmed extension axis)
```

Design rules:
- `domain/services/policies.py`: classifies the clues already collected, never does networking.
- `domain/discovery/policies.py`: perimeter/depth/count safeguards — pure logic, testable without a network.
- `domain/architecture/service.py`: rebuilds the graph from the provenance already carried by each `Host`, makes no new request.
- `infrastructure/network/` and `infrastructure/discovery/`: do networking (sockets, `httpx`, `cryptography`), never judge.
- `interfaces/`: displays, contains no business logic — the validation screen for discovered targets calls `validate_targets`, it does not implement the fail-safe rule itself.
- `infrastructure/exporters/`: read the analysis result (scan, hosts, graph), recompute nothing.

## 7. Service identification and roles

### Detected protocols

| Protocol | Probe | Collected details |
|---|---|---|
| HTTP / HTTPS | `httpx` | `Server` banner, authentication headers |
| TLS | `cryptography` (negotiated certificate, `CERT_NONE` included) | Version, cipher, certificate subject/issuer |
| SSH | Raw banner | Software and version (e.g. `OpenSSH 10.4`) |
| VNC (RFB) | Security codes announced by the server | Supported authentication types |
| Generic | Raw banner on an unrecognized open port | Careful extraction, no aggressive heuristic |

### Inferred roles

Deduced from the protocol **actually negotiated**, never from a port-number assumption:

| Role | Condition | Confidence |
|---|---|---|
| `web server` | HTTP/HTTPS protocol confirmed | `INFERRED` |
| `shell access` | SSH protocol confirmed | `CORROBORATED` |
| `graphical access` | VNC protocol confirmed | `CORROBORATED` |
| `database` | Port within the range of the `db` system profile | `INFERRED` |

### Known WAF signatures

Detected through a declarative header (`server`, `x-sdk`) — presence **declared by the target**, never independently verified: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (listed for information, not strictly an application WAF).

## 8. Architecture graph

Rebuilt solely from the provenance already carried by each accepted host (`discovered_from`/`discovery_source`/`discovery_confidence`) — no new network request, no re-analysis of the raw clues.

### Relations produced

| Relation | Discovery source | Meaning |
|---|---|---|
| `proxy_to` | `header` | The root target (or an already accepted host) is probably a proxy to the discovered target |
| `redirect_to` | `redirection` | HTTP redirect observed to the discovered target |
| `linked_to` | `certificate` or `html_link` | The most neutral relation — shared infrastructure/application, with no flow direction asserted |

`backend_of` (the reverse edge of a `proxy_to`) is deliberately not produced — it would be duplicated information, not a new deduction.

### Rendering

- **TUI** (analysis details) and **JSON/text exports**: list of edges (source, relation, target, confidence) — a terminal is not the place for rich graphical rendering.
- **HTML export**: a **real SVG diagram** (nodes = circles, edges = labeled arrows), layered layout computed from the root target, size proportional to the number of discovered machines — never a heavy graph-layout dependency; the graph stays small by construction (bounded by the safeguards of [§4](#4-target-discovery-and-safeguards)).

## 9. Confidence policy

Each collected field carries one of these levels:

| Level | Meaning |
|---|---|
| `VERIFIED` | Protocol fact observed directly, which the target cannot forge (e.g. closed port confirmed by a TCP RST, TLS version actually negotiated). |
| `DECLARED` | Value self-announced by the target in a field it fully controls (e.g. `Server` banner, `X-Backend-Server` header) — plausible but forgeable at will. |
| `CORROBORATED` | A `DECLARED` value confirmed by an independent clue (e.g. SSH role, the protocol having actually been negotiated). |
| `INFERRED` | Deduced from a pattern/heuristic, with no explicit declaration from the target (e.g. HTML link). |
| `UNKNOWN` | No usable clue, or actively hidden by the target. |

## 10. Protection against forged values

Omega-deep trusts no data self-declared by the target without flagging it explicitly — and target discovery is the most sensitive part of the project: a malicious target *could* announce a lying `X-Backend-Server` to steer discovery toward an IP of its choosing. Two structural protections, independent of each other:
- No information derived from a target is ever `VERIFIED` merely because it is announced — a `Server` banner or an `X-Backend-Server` header stays `DECLARED`, however plausible.
- The perimeter safeguard ([§4](#4-target-discovery-and-safeguards)) bounds where an announced target can lead (same private `/24`, unless explicitly configured), and user validation bounds whether it is scanned at all — a lying target outside the perimeter is never even proposed; a target inside the perimeter remains subject to explicit confirmation before any scan.

## 11. Terminal compatibility

The TUI (Textual) automatically detects the terminal's capabilities (emulator, size) and adapts its structural stylesheet accordingly (`complete`/`standard`/`reduced`/`mono`), with no manual flag. CLI mode always stays plain text, independent of the terminal. Policy shared by the whole `omega-` suite (`omega-lib`, `terminal/policies.py`).

### Profile according to the detected emulator

| Emulator | Initial profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modern SSH | `reduced` |
| Linux TTY, legacy SSH | `mono` |
| Unrecognized emulator | `reduced` (default fallback) |

### Profile according to the terminal size

| Minimum size (columns × rows) | Profile ceiling |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| below | `mono` |

The final profile is **the more restrictive of the two** (emulator and size) — a full-screen Ghostty resized to 70 columns drops to `mono`, even though its emulator would allow `complete`. Refreshable live with the `r` key.

## 12. Exports

Text and HTML reports are written in the language chosen in Settings ("Export language", by default the interface language); JSON stays data and is not translated. Reports are generated in `var/exports/` by default (runtime path anchored on the project folder, `$OMEGA_DEEP_VAR_DIR` to override it), or at the given path (`--output` in the CLI, a dialog in the TUI). Explicit, timestamped file name: `analyse-{profile}-{date}.ext`, `analyse-custom-{date}.ext` for a personal profile.

### JSON, the source of truth

Full structure of the analysis (`Scan` + `Host[]` + `ArchitectureGraph`), strictly JSON-serializable, confidence levels included.

### Text, compact human-readable report

Readable outside a terminal, without ANSI codes — graph as a list of edges.

### HTML, self-contained web report

5 themes to choose from (`--theme` in the CLI, a selector in the TUI; follows the active interface theme by default when an equivalent exists). Dedicated layout: container, info grid, statistics boxes per port state, colored badges, **SVG diagram of the architecture graph** (see [§8](#8-architecture-graph)) — same visual family as `omega-scan`/`omega-check`.

## 13. History and comparison

Each analysis is persisted (SQLite, `var/db/omega-deep.db`): one `scan_id` carries the root target **and** every discovered/accepted host, plus the rebuilt graph. History can be browsed by root target (with a dedicated column for the number of discovered targets), details of a past analysis (hosts + graph), comparison between two analyses (port state of the **root target** only — comparing discovery graphs would be a possible extension, not needed so far), and replay of an analysis on the same root target without re-entering it.

## 14. Tests

```bash
source .venv/bin/activate
lint-imports        # checks the Dependency Rule
pytest -q           # 191 tests
ruff check src tests
mypy -p omega_deep
```

Structure: `tests/unit/` (domain and application, without real I/O), `tests/integration/` (real SQLite/files, fake HTTP server `pytest-httpserver`, TLS through `trustme`), `tests/tui/` (navigation via `Pilot`, structural — no self-claimed visual verification).

## 15. Out of scope

- CVE scanning
- Active detection of SQLi, XSS, RCE
- Operating system fingerprinting
- Low-level nmap-style scanning techniques (SYN scan, raw packets)
- Crawling
- Fuzzing
- Brute force
- Scanning a discovered target without explicit confirmation — never, in any mode
- Discovery outside the private subnet of the initial target without explicit configuration
- Web dashboard

---

> Omega-deep — Discover, map, qualify, report.
> An architecture rebuilt with explicit confidence, never a guess dressed up as fact.
