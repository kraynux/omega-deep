<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->
<div align="center">
  <img src="docs/assets/omega-deep.png" alt="Omega-Deep" width="256">
</div>

# 🖧 OMEGA-DEEP

**Multi-target architecture analysis (discovery + safeguards + graph)**

> Developed by **kraynux** for **Omega-server**  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Official page: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**Languages:**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)

---

**Omega-deep** includes everything `omega-check` does for a single target (port scanning, service identification, roles, WAF, TLS) and adds **discovery of additional targets** from clues left by the target already scanned (headers, redirects, certificate, HTML links), under **strict safeguards** and with **explicit user validation** before any discovered target is scanned. It then **reconstructs an architecture graph** (who communicates with whom, and with what confidence). It is the fifth tool in the `omega-` suite (after `omega-fire`, `omega-stress`, `omega-scan`, and `omega-check`), structured according to Clean Architecture — see `docs/ARCHITECTURE.md` for complete technical details.

## 1. Vision and scope

Omega-deep answers a question omega-check does not ask: *what else is behind this IP?* A reverse proxy that reveals its backend, a certificate covering multiple hosts, or a page pointing to a neighboring service are all clues that omega-deep follows cautiously, never on its own.

### What Omega-deep does

- Scans a root target exactly like omega-check (system profile or saved personal profile).
- Discovers candidate targets from clues left by each already-scanned host: HTTP headers (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), redirects (`Location`), TLS certificates (SAN), and HTML links — see [§4](#4-target-discovery-and-safeguards).
- **Never** scans a discovered target without explicit, target-by-target validation — silence is never acceptance.
- Bounds discovery with strict safeguards: maximum depth, maximum number of additional targets, and an allowed subnet (by default, the same private range as the root target).
- Reconstructs an **architecture graph** from the provenance of each accepted target (`proxy_to`, `redirect_to`, `linked_to`), with a confidence level for each relation — see [§8](#8-architecture-graph).
- Presents results through the TUI (Textual) or a scriptable CLI, with the same three exports as omega-check (JSON, text, and HTML with 5 themes). In HTML, the graph is a **real drawn diagram**, not a table.
- Assigns every collected item (service information and discovery information) an explicit confidence level — see [§9](#9-confidence-policy).
- Keeps a persistent history of analyses that can be replayed and compared over time.

### What Omega-deep does not do

- Active vulnerability scanning; no SQLi, XSS, or RCE testing.
- CVE scanning.
- Operating-system fingerprinting.
- Low-level nmap-style scanning techniques (SYN scan, raw packets) — application-level TCP connections only.
- Brute-force or fuzzing tool functionality.
- Scanning a discovered target without explicit user confirmation — never, under any mode.
- Discovery beyond the private subnet of the initial target unless explicitly configured (`--subnet`).
- Web dashboard.

## 2. Installation

### Prerequisites

- Python 3.10+
- Internet connection for dependencies

### Installation

```bash
[ -d omega-deep ] && echo "ℹ️ Already extracted here, step skipped." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it does not already exist.
2. Installs the dependencies (`vendor/omega-lib/` followed by `pip install -e .`; `pyproject.toml` remains the single source of truth).
3. Makes `omega-deep.sh` and `install.sh` executable.
4. Adds the `deep` alias to `~/.bashrc` and `~/.zshrc` (without duplicates if already present).

### Dependencies

Declared in `pyproject.toml` (there is no longer a `requirements.txt`):
- `omega-lib`: shared suite library (`ConfidenceLevel`, themes, terminal detection) — vendored in `vendor/omega-lib/`
- `textual`: TUI, themes, and automatic terminal adaptation
- `httpx`: HTTP/HTTPS probes (service and discovery)
- `cryptography`: reading the negotiated TLS certificate
- `jinja2`: templating for HTML export
- Development dependencies (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Usage

### Interactive mode (TUI)

Recommended for daily use — launched without arguments:

```bash
./omega-deep.sh
```
If you created the alias, simply type `deep` in the terminal:
```bash
deep
```

Flow: start screen (closes on a key press or click) → main menu (Analyze / Profiles / History / Settings / Help) → root target input, profile selection, and discovery safeguards (maximum depth, maximum number of targets, allowed subnet) → analysis (indeterminate gauge and live network-operation log) → for each batch of discovered targets, validation screen (one line per target, source/confidence/evidence displayed, accept/reject toggle — no box selected by default) → analysis details (hosts, ports/services/roles, graph, export) → history/comparison/replay and settings from the main menu. Terminal adaptation (colors, size, structural degradation) is automatic.

#### Keyboard shortcuts

| Key | Action |
|---|---|
| `↑` / `↓` | Move between screen elements |
| `Tab` / `Shift+Tab` | Move between form fields |
| `Esc` | Return to the previous screen (exit confirmation on the home screen) |
| `t` | Next theme (applied immediately, without confirmation) |
| `r` | Refresh terminal detection |
| `a` | Display help |
| `q` | Quit (with confirmation) |

### Scriptable mode (CLI)

Any subcommand triggers CLI mode:

```bash
# Analyze a target (root scan + multi-target discovery)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# History (filterable by root target)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Analysis details (text, JSON, or HTML) — 5 export themes available
./omega-deep.sh show <scan_id> --format html --theme omega-base --output rapport.html

# Compare two analyses (root target port state)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Personal port profiles
./omega-deep.sh profile list
./omega-deep.sh profile create labo --ports 22,80,443 --description "My profile"
./omega-deep.sh profile edit labo --ports 22,80,443,8080
./omega-deep.sh profile pin labo
./omega-deep.sh profile unpin labo
./omega-deep.sh profile delete labo
```

In the CLI, discovered-target validation is performed through one interactive question per target (`Scan <target>? [y/N]`), with the evidence details displayed before each question. `--auto-validate` accepts everything without review (**not recommended**, warning displayed). In a non-interactive environment (no TTY and no `--auto-validate`), every discovered target is rejected by default rather than scanned without confirmation.

### Accepted target formats

```text
192.168.1.10                IPv4
example.org                 Hostname
http://example.org          HTTP URL (scheme removed before resolution)
https://example.org:8443    HTTPS URL with port (scheme and port removed)
```

The optional scheme and port are removed before DNS resolution (`domain/targets/validation.py::normalize_target_input`) — pasting a complete URL works; only the host is retained. *Discovered* targets are normalized in the same way, but are never scanned without validation (see [§4](#4-target-discovery-and-safeguards)).

## 4. Target discovery and safeguards

### Clue sources

| Source | Origin | Confidence |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | `Location` header from an HTTP response | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) from the negotiated TLS certificate | `DECLARED` |
| `html_link` | Links (`<a href>`) served by the page | `INFERRED` |

A `DECLARED` value remains a self-declaration by the target and can be falsified — see [§10](#10-protection-against-falsified-values). `html_link` is deliberately the weakest source: a simple link does not declare any infrastructure relationship.

### Safeguards (always active, never disableable)

- **Scope**: a candidate target must be a private IP in the same `/24` as the root target, unless `--subnet` is explicitly provided (in that case, only membership in the specified subnet matters, even if it includes public IPs — the explicit configuration authorizes the exception). An unresolved hostname is never accepted by this filter (resolving it to verify would already be a network action outside the scope of this check).
- **Depth**: `--max-depth` (default 3) — maximum A → B → C → D.
- **Target count**: `--max-targets` (default 10) — across all depths.

### Validation (never scan without confirmation)

Each proposed target follows `PROPOSED → PRESENTED → ACCEPTED` or `REJECTED`. The rule is **fail-safe**: any target that has not been explicitly accepted (silence, closing the screen, interruption, timeout, or missing TTY) is treated as rejected — never the reverse. In the TUI, a dedicated screen lists the targets in a batch with evidence and confidence, provides per-line accept/reject toggles, “accept all”/“reject all”, and rejects everything by default when `Esc` is pressed. In the CLI, there is one question per target; `--auto-validate` (not recommended) is the only way to bypass interactivity.

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
| `iot` | IoT equipment, cameras, routers, home automation | no |
| `dev` | Development/lab environments | no |
| `docker` | Docker, Swarm, and common container services | no |
| `complet` | **Generated on demand**: sorted, deduplicated union of all profiles above | no |
| *personal profile* | Created in the **Profiles** screen (TUI) or with `profile create` (CLI), listed alongside system profiles and prefixed with `* ` in the TUI | no |

The profile applies to the root target **and** to every accepted discovered target — there is no separate profile per host. Complete details, validation rules, and personal-profile management: `docs/PROFILES.md`.

## 6. Architecture

Omega-deep follows **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), aligned with the `omega-` suite template (see `omega-scan`/`omega-check`) and checked by `import-linter` after every change. Full details are in **`docs/ARCHITECTURE.md`**.

Very short overview:

```text
src/omega_deep/
├── domain/          Pure business logic: scans, targets, services, profiles, reports,
│                    discovery (proposed targets, validation state machine),
│                    architecture (graph, relation rules)
├── application/     Use cases (commands/queries), including discover_targets,
│                    validate_targets, reconstruct_architecture (new compared with omega-check)
├── ports/           Contracts expected by the application (probers, including discovery_prober,
│                    repositories, exporters...)
├── infrastructure/  Concrete implementations (socket/httpx/cryptography, SQLite,
│                    SVG graph rendering — Textual is NOT here)
├── interfaces/      tui/ (Textual) and cli/ (scriptable), with strict functional parity
├── app/             Assembly (DependencyContainer, bootstrap, lifecycle)
├── core/, shared/   Cross-cutting vocabulary, non-business utilities
└── plugins/         Structure in place, empty (no confirmed extension axis)
```

Design rules:
- `domain/services/policies.py`: classifies already-collected clues and never performs network access.
- `domain/discovery/policies.py`: scope/depth/count safeguards — pure logic, testable without networking.
- `domain/architecture/service.py`: reconstructs the graph from provenance already carried by each `Host`; it makes no further requests.
- `infrastructure/network/` and `infrastructure/discovery/`: perform networking (sockets, `httpx`, `cryptography`) and never make judgments.
- `interfaces/`: displays information and contains no business logic — the discovered-target validation screen calls `validate_targets`; it does not implement the fail-safe rule itself.
- `infrastructure/exporters/`: read the analysis result (scan, hosts, graph) and never recalculate anything.

## 7. Service identification and roles

### Detected protocols

| Protocol | Probe | Collected detail |
|---|---|---|
| HTTP / HTTPS | `httpx` | `Server` banner, authentication headers |
| TLS | `cryptography` (negotiated certificate, including `CERT_NONE`) | Version, cipher, certificate subject/issuer |
| SSH | Raw banner | Software and version (e.g. `OpenSSH 10.4`) |
| VNC (RFB) | Security codes announced by the server | Supported authentication types |
| Generic | Raw banner on an unrecognized open port | Conservative extraction, no aggressive heuristics |

### Inferred roles

Derived from the **actually negotiated** protocol, never from an assumed port number:

| Role | Condition | Confidence |
|---|---|---|
| `web server` | HTTP/HTTPS protocol confirmed | `INFERRED` |
| `shell access` | SSH protocol confirmed | `CORROBORATED` |
| `graphical access` | VNC protocol confirmed | `CORROBORATED` |
| `database` | Port within the `db` system-profile range | `INFERRED` |

### Known WAF signatures

Detected through declarative headers (`server`, `x-sdk`) — presence is **declared by the target** and never independently verified: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (listed for information, not strictly an application WAF).

## 8. Architecture graph

Reconstructed only from the provenance already carried by each accepted host (`discovered_from`/`discovery_source`/`discovery_confidence`) — no new network request and no re-analysis of raw clues.

### Produced relations

| Relation | Discovery source | Meaning |
|---|---|---|
| `proxy_to` | `header` | The root target (or an already accepted host) is likely a proxy to the discovered target |
| `redirect_to` | `redirection` | An HTTP redirect was observed toward the discovered target |
| `linked_to` | `certificate` or `html_link` | The most neutral relation — shared infrastructure/application, with no asserted flow direction |

`backend_of` (the reverse edge of `proxy_to`) is intentionally not produced — it would duplicate information rather than provide a new deduction.

### Rendering

- **TUI** (analysis details) and **JSON/text exports**: list of edges (source, relation, target, confidence) — a terminal is not the right place for rich graphical rendering.
- **HTML export**: a **real SVG diagram** (nodes = circles, edges = labeled arrows), with layered layout calculated from the root target and size proportional to the number of discovered machines — no heavy graph-layout dependency; the graph remains small by construction, bounded by the safeguards in [§4](#4-target-discovery-and-safeguards).

## 9. Confidence policy

Each collected field carries one of the following levels:

| Level | Meaning |
|---|---|
| `VERIFIED` | A protocol fact observed directly and not falsifiable by the target (for example, a port closed and confirmed by TCP RST, or the TLS version actually negotiated). |
| `DECLARED` | A value self-announced by the target in a field it fully controls (for example, a `Server` banner or `X-Backend-Server` header) — plausible but freely falsifiable. |
| `CORROBORATED` | A `DECLARED` value confirmed by an independent clue (for example, an SSH role confirmed by the protocol actually negotiated). |
| `INFERRED` | Deduced from a pattern or heuristic without an explicit declaration by the target (for example, an HTML link). |
| `UNKNOWN` | No usable clue, or information actively hidden by the target. |

## 10. Protection against falsified values

Omega-deep does not trust any self-declared data from a target without explicitly stating so — and target discovery is the most sensitive part of the project: a malicious target *could* announce a false `X-Backend-Server` to steer discovery toward an IP of its choice. Two independent structural protections are used:

- Information derived from a target is never marked `VERIFIED` merely because it was announced — a `Server` banner or `X-Backend-Server` header remains `DECLARED`, regardless of how plausible it appears.
- The scope safeguard ([§4](#4-target-discovery-and-safeguards)) limits where an announced target can lead (the same private `/24`, unless explicitly configured), while user validation determines whether it is scanned at all — a false target outside the scope is never even proposed; a target inside the scope still requires explicit confirmation before any scan.

## 11. Terminal compatibility

The Textual TUI automatically detects terminal capabilities (emulator, size) and adapts its structural stylesheet accordingly (`complete`/`standard`/`reduced`/`mono`), without a manual flag. CLI mode always remains plain text and independent of the terminal. This policy is shared by the entire `omega-` suite (`omega-lib`, `terminal/policies.py`).

### Profile by detected emulator

| Emulator | Initial profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modern SSH | `reduced` |
| Linux TTY, legacy SSH | `mono` |
| Unrecognized emulator | `reduced` (default fallback) |

### Profile by terminal size

| Minimum size (columns × rows) | Profile ceiling |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| below | `mono` |

The final profile is **the more restrictive of the two** (emulator and size) — a full-screen Ghostty resized to 70 columns drops to `mono`, even if its emulator would allow `complete`. It can be refreshed live with the `r` key.

## 12. Exports

Reports are generated in `var/exports/` by default (runtime path anchored to the project directory, `$OMEGA_DEEP_VAR_DIR` to override it), or at the path specified by `--output` in the CLI or by the dialog in the TUI. Explicit, timestamped filename: `analyse-{profile}-{date}.ext`, or `analyse-custom-{date}.ext` for a personal profile.

### JSON, source of truth

Complete analysis structure (`Scan` + `Host[]` + `ArchitectureGraph`), strictly JSON-serializable, including confidence levels.

### Text, compact human-readable report

Readable outside the terminal, without ANSI codes — graph represented as an edge list.

### HTML, standalone web report

5 themes available (`--theme` in the CLI, selector in the TUI; by default it follows the active interface theme when an equivalent exists). Dedicated layout: container, information grid, port-state statistics panels, colored badges, and an **SVG diagram of the architecture graph** (see [§8](#8-architecture-graph)) — in the same visual family as `omega-scan`/`omega-check`.

## 13. History and comparison

Each analysis is persisted (SQLite, `var/db/omega-deep.db`): a `scan_id` contains the root target **and** all discovered/accepted hosts, together with the reconstructed graph. History can be viewed by root target (with a dedicated column for the number of discovered targets), along with details of a past analysis (hosts + graph), comparison between two analyses (port state of the **root target** only — comparing discovery graphs would be a possible extension, but is not currently necessary), and replay of an analysis against the same root target without entering it again.

## 14. Tests

```bash
source .venv/bin/activate
lint-imports        # checks the Dependency Rule
pytest -q           # 173 tests
ruff check src tests
mypy -p omega_deep
```

Structure: `tests/unit/` (domain and application, without real I/O), `tests/integration/` (real SQLite/filesystem, fake HTTP server via `pytest-httpserver`, TLS through `trustme`), `tests/tui/` (navigation via `Pilot`, structural — no claimed automated visual verification).

## 15. Out of scope

- CVE scanning
- Active SQLi, XSS, or RCE detection
- Operating-system fingerprinting
- Low-level nmap-style scanning techniques (SYN scan, raw packets)
- Crawling
- Fuzzing
- Brute force
- Scanning a discovered target without explicit confirmation — never, under any mode
- Discovery outside the private subnet of the initial target without explicit configuration
- Web dashboard

---

> Omega-deep — Discover, map, qualify, report.
> An architecture reconstructed with explicit confidence, never an assumption disguised as a fact.