<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licenza MIT (vedi il file LICENSE) -->
<div align="center">
  <img src="../../assets/omega-deep.png" alt="Omega-Deep" width="384">
</div>

# 🖧 OMEGA-DEEP

**Analisi di architettura su più destinazioni (scoperta + salvaguardie + grafo)**

> Realizzato da [kraynux](https://github.com/kraynux) per [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Pagina ufficiale: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Anteprima: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfaccia e report esportati disponibili in **17 lingue** — vedi [Lingue dell'interfaccia](#lingue-dellinterfaccia).  
**Lingue:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** fa tutto ciò che fa `omega-check` su una destinazione singola (scansione delle porte, identificazione dei servizi, ruoli, WAF, TLS) e aggiunge la **scoperta di destinazioni ulteriori** a partire dagli indizi lasciati dalla destinazione già analizzata (intestazioni, reindirizzamenti, certificato, link HTML), sotto **salvaguardie rigorose** e una **convalida esplicita dell'utente** prima di analizzare qualsiasi destinazione scoperta, poi **ricostruisce un grafo di architettura** (chi parla con chi, con quale fiducia). Strumento della suite `omega-`, strutturato in Clean Architecture — vedi `docs/ARCHITECTURE.md` per tutti i dettagli tecnici.

## 1. Visione e perimetro

Omega-deep risponde a una domanda che omega-check non si pone: *dietro questo IP, cos'altro c'è?* Un reverse proxy che annuncia il proprio backend, un certificato che copre più host, una pagina che punta a un servizio vicino — altrettanti indizi che omega-deep segue, con prudenza, mai da solo.

### Cosa fa Omega-deep

- Analizza una destinazione radice esattamente come omega-check (profilo di sistema o profilo personale salvato).
- Scopre destinazioni candidate dagli indizi lasciati da ogni host già analizzato: intestazioni HTTP (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), reindirizzamento (`Location`), certificato TLS (SAN), link HTML — vedi [§4](#4-scoperta-delle-destinazioni-e-salvaguardie).
- **Non** analizza **mai** una destinazione scoperta senza convalida esplicita, destinazione per destinazione — il silenzio non è mai un'accettazione.
- Limita la scoperta con salvaguardie rigorose: profondità massima, numero massimo di destinazioni aggiuntive, sottorete consentita (per impostazione predefinita lo stesso intervallo privato della radice).
- Ricostruisce un **grafo di architettura** dalla provenienza di ogni destinazione accettata (`proxy_to`, `redirect_to`, `linked_to`), con un livello di fiducia per relazione — vedi [§8](#8-grafo-di-architettura).
- Presenta il risultato in TUI (Textual) o in CLI scriptabile, con le stesse tre esportazioni di omega-check (JSON, testo, HTML con 5 temi) — lì il grafo è un **vero diagramma disegnato** in HTML, non una tabella.
- Attribuisce a ogni informazione raccolta (servizio o scoperta) un livello di fiducia esplicito — vedi [§9](#9-politica-di-fiducia).
- Conserva una cronologia persistente delle analisi, ripetibile e confrontabile nel tempo.

### Cosa non fa Omega-deep

- Scansione attiva delle vulnerabilità: niente SQLi, XSS o RCE.
- Scansione di CVE.
- Rilevamento del sistema operativo.
- Tecniche di scansione a basso livello in stile nmap (SYN scan, pacchetti grezzi) — solo connessione TCP applicativa.
- Strumento di forza bruta o di fuzzing.
- Analizzare una destinazione scoperta senza conferma esplicita dell'utente — mai, in nessuna modalità.
- Scoperta oltre la sottorete privata della destinazione iniziale, salvo configurazione esplicita (`--subnet`).
- Dashboard web.

## 2. Installazione

### Prerequisiti

- Python 3.10+
- Connessione a Internet, per le dipendenze

### Installazione

```bash
[ -d omega-deep ] && echo "ℹ️ Già estratto qui, passaggio saltato." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea l'ambiente virtuale `.venv` se non esiste già.
2. Installa le dipendenze (`vendor/omega-lib/` poi `pip install -e .`; `pyproject.toml` resta l'unica fonte di verità).
3. Rende eseguibili `omega-deep.sh` e `install.sh`.
4. Aggiunge l'alias `deep` a `~/.bashrc` e `~/.zshrc` (senza duplicati se già presente).

### Dipendenze

Dichiarate in `pyproject.toml` (niente più `requirements.txt`):
- `omega-lib`: libreria condivisa della suite (`ConfidenceLevel`, temi, rilevamento del terminale) — inclusa in `vendor/omega-lib/`
- `textual`: interfaccia TUI, temi, adattamento automatico al terminale
- `httpx`: sonde HTTP/HTTPS (servizio e scoperta)
- `cryptography`: lettura del certificato TLS negoziato
- `jinja2`: template per l'esportazione HTML
- Dipendenze di sviluppo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Utilizzo

### Modalità interattiva (TUI)

Consigliata per l'uso quotidiano — avviata senza argomenti:

```bash
./omega-deep.sh
```
se hai creato l'alias, digita semplicemente `deep` nel terminale:
```bash
deep
```

Percorso: schermata iniziale (si chiude con un tasto o un clic) → menu principale (Analizza / Profili / Cronologia / Impostazioni / Aiuto) → inserimento della destinazione radice, scelta del profilo e delle salvaguardie di scoperta (profondità massima, numero massimo di destinazioni, sottorete consentita) → analisi (indicatore indeterminato e registro delle operazioni di rete in tempo reale) → a ogni gruppo di destinazioni scoperte, una schermata di convalida (una riga per destinazione, con fonte/fiducia/prova visibili, interruttore accetta/rifiuta — nulla selezionato per impostazione predefinita) → dettaglio dell'analisi (host, porte/servizi/ruoli, grafo, esportazione) → cronologia/confronto/ripetizione e impostazioni dal menu principale. L'adattamento al terminale (colori, dimensioni, degradazione strutturale) è automatico.

#### Scorciatoie da tastiera

| Tasto | Azione |
|---|---|
| `↑` / `↓` | Spostarsi tra gli elementi di una schermata |
| `Tab` / `Maiusc+Tab` | Spostarsi tra i campi di un modulo |
| `Esc` | Tornare alla schermata precedente (conferma di uscita nella schermata iniziale) |
| `t` | Tema successivo (applicato subito, senza conferma) |
| `r` | Aggiornare il rilevamento del terminale |
| `a` | Mostrare l'aiuto |
| `q` | Uscire (con conferma) |

### Lingue dell'interfaccia

L'interfaccia è disponibile in 17 lingue: francese, inglese, spagnolo, portoghese (Brasile), italiano, tedesco, olandese, polacco, russo, cinese semplificato, vietnamita, thailandese, indonesiano, giapponese, coreano, hindi e arabo. La scelta si fa nelle Impostazioni («Langue / Language») e vale dopo il riavvio dell'interfaccia; la variabile `OMEGA_DEEP_LANG` (per esempio `OMEGA_DEEP_LANG=it ./omega-deep.sh`) impone una lingua per una sessione. Avviato da omega-suite, omega-deep usa la lingua della suite. In una console di testo Linux (TTY), le lingue con scrittura non latina vengono mostrate in inglese per la sessione. La riga di comando resta in francese.

### Modalità scriptabile (CLI)

Qualsiasi sottocomando attiva la modalità CLI:

```bash
# Analizzare una destinazione (scansione radice + scoperta su più destinazioni)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Cronologia (filtrabile per destinazione radice)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Dettaglio di un'analisi (testo, JSON o HTML) — 5 temi di esportazione a scelta
./omega-deep.sh show <scan_id> --format html --theme omega-base --output report.html

# Confrontare due analisi (stato delle porte della destinazione radice)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Profili di porte personali
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "Il mio profilo"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

In CLI, la convalida delle destinazioni scoperte avviene con una domanda interattiva per destinazione (`Scanner <cible> ? [o/N]`, in francese come il resto della riga di comando), con il dettaglio della prova mostrato prima di ogni domanda. `--auto-validate` accetta tutto senza revisione (**sconsigliato**, viene mostrato un avviso); in un ambiente non interattivo (senza TTY e senza `--auto-validate`), ogni destinazione scoperta viene rifiutata per impostazione predefinita invece di essere analizzata senza conferma.

### Formati di destinazione accettati

```text
192.168.1.10                IPv4
example.org                 Nome host
http://example.org          URL HTTP  (schema rimosso prima della risoluzione)
https://example.org:8443    URL HTTPS con porta  (schema e porta rimossi)
```

Lo schema e l'eventuale porta vengono rimossi prima della risoluzione DNS (`domain/targets/validation.py::normalize_target_input`) — incollare un URL intero funziona, viene conservato solo l'host. Le destinazioni *scoperte* vengono normalizzate allo stesso modo, ma non vengono mai analizzate senza convalida (vedi [§4](#4-scoperta-delle-destinazioni-e-salvaguardie)).

## 4. Scoperta delle destinazioni e salvaguardie

### Fonti di indizi

| Fonte | Origine | Fiducia |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | Intestazione `Location` di una risposta HTTP | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) del certificato TLS negoziato | `DECLARED` |
| `html_link` | Link (`<a href>`) serviti dalla pagina | `INFERRED` |

Un valore `DECLARED` resta un'autodichiarazione della destinazione (falsificabile) — vedi [§10](#10-protezione-contro-i-valori-falsificati). `html_link` è volutamente la fonte più debole: un semplice link non dichiara alcuna relazione di infrastruttura.

### Salvaguardie (sempre attive, mai disattivabili)

- **Perimetro**: una destinazione candidata deve essere un IP privato nello stesso `/24` della destinazione radice, salvo `--subnet` esplicito (nel qual caso conta solo l'appartenenza alla sottorete indicata, anche se copre IP pubblici — è la configurazione esplicita ad autorizzare l'eccezione). Un nome host non risolto non viene mai accettato da questo filtro (risolverlo per verificarlo sarebbe già un'azione di rete fuori dalla portata di questo controllo).
- **Profondità**: `--max-depth` (predefinito 3) — al massimo A → B → C → D.
- **Numero di destinazioni**: `--max-targets` (predefinito 10) — su tutte le profondità.

### Convalida (mai una scansione senza conferma)

Ogni destinazione proposta segue `PROPOSED → PRESENTED → ACCEPTED` oppure `REJECTED`. La regola è **a prova di errore**: ogni destinazione mai accettata esplicitamente (silenzio, chiusura della schermata, interruzione, timeout, assenza di TTY) viene trattata come rifiutata — mai il contrario. In TUI, una schermata dedicata elenca le destinazioni di un gruppo con prova e fiducia, un interruttore accetta/rifiuta per riga, «accetta tutto»/«rifiuta tutto» e un rifiuto totale predefinito con Esc. In CLI, una domanda per destinazione; `--auto-validate` (sconsigliato) è l'unico modo per aggirare l'interattività.

## 5. Profili di scansione

| Profilo | Descrizione | Fissato |
|---|---|---|
| `minimal` | Scansione rapidissima: SSH + HTTP + HTTPS (22, 80, 443) | sì |
| `classic` | Servizi classici Internet/LAN | sì |
| `web` | Servizi web e alternative | no |
| `db` | Database e servizi di dati | no |
| `remote` | Accessi remoti — shell, desktop, RustDesk | no |
| `mail` | Servizi di posta | no |
| `dns` | Servizi DNS | no |
| `iot` | Dispositivi IoT, telecamere, router, domotica | no |
| `dev` | Ambienti di sviluppo/laboratorio | no |
| `docker` | Docker, Swarm e servizi comuni in container | no |
| `complet` | **Generato al volo**: unione ordinata e senza duplicati di tutti i profili qui sopra | no |
| *profilo personale* | Creato nella schermata **Profili** (TUI) o con `profile create` (CLI), elencato insieme ai profili di sistema, con il prefisso `* ` in TUI | no |

Il profilo si applica alla destinazione radice **e** a ogni destinazione scoperta accettata — nessun profilo diverso per host. Dettaglio completo, regole di validazione e gestione dei profili personali: `docs/PROFILES.md`.

## 6. Architettura

Omega-deep è strutturato in **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), allineata al modello della suite `omega-` (vedi `omega-scan`/`omega-check`) e verificata da `import-linter` a ogni modifica. Tutti i dettagli sono in **`docs/ARCHITECTURE.md`**.

Panoramica molto breve:

```text
src/omega_deep/
├── domain/          Logica di business pura: scansioni, destinazioni, servizi, profili, report,
│                    discovery (destinazioni proposte, macchina a stati di convalida),
│                    architecture (grafo, regole di relazione)
├── application/     Casi d'uso (commands/queries) — tra cui discover_targets,
│                    validate_targets, reconstruct_architecture (nuovi rispetto a omega-check)
├── ports/           Contratti attesi dall'applicazione (sonde, tra cui discovery_prober,
│                    repository, esportatori...)
├── infrastructure/  Implementazioni concrete (socket/httpx/cryptography, SQLite,
│                    resa SVG del grafo — Textual NON è qui)
├── interfaces/      tui/ (Textual) e cli/ (scriptabile), con parità funzionale rigorosa
├── app/             Assemblaggio (DependencyContainer, bootstrap, ciclo di vita)
├── core/, shared/   Vocabolario trasversale, utilità non di business
└── plugins/         Struttura predisposta, vuota (nessun asse di estensione confermato)
```

Regole di progettazione:
- `domain/services/policies.py`: classifica gli indizi già raccolti, non fa mai rete.
- `domain/discovery/policies.py`: salvaguardie di perimetro/profondità/numero — logica pura, testabile senza rete.
- `domain/architecture/service.py`: ricostruisce il grafo dalla provenienza già portata da ogni `Host`, non rifà alcuna richiesta.
- `infrastructure/network/` e `infrastructure/discovery/`: fanno rete (socket, `httpx`, `cryptography`), non giudicano mai.
- `interfaces/`: mostra, non contiene alcuna logica di business — la schermata di convalida delle destinazioni scoperte chiama `validate_targets`, non implementa da sé la regola a prova di errore.
- `infrastructure/exporters/`: leggono il risultato dell'analisi (scansione, host, grafo), non ricalcolano nulla.

## 7. Identificazione dei servizi e ruoli

### Protocolli rilevati

| Protocollo | Sonda | Dettaglio raccolto |
|---|---|---|
| HTTP / HTTPS | `httpx` | Banner `Server`, intestazioni di autenticazione |
| TLS | `cryptography` (certificato negoziato, `CERT_NONE` incluso) | Versione, cifrario, soggetto/emittente del certificato |
| SSH | Banner grezzo | Software e versione (es. `OpenSSH 10.4`) |
| VNC (RFB) | Codici di sicurezza annunciati dal server | Tipi di autenticazione supportati |
| Generico | Banner grezzo su porta aperta non riconosciuta | Estrazione prudente, nessuna euristica aggressiva |

### Ruoli dedotti

Ricavati dal protocollo **realmente negoziato**, mai da una supposizione basata sul numero di porta:

| Ruolo | Condizione | Fiducia |
|---|---|---|
| `server web` | Protocollo HTTP/HTTPS confermato | `INFERRED` |
| `accesso shell` | Protocollo SSH confermato | `CORROBORATED` |
| `accesso grafico` | Protocollo VNC confermato | `CORROBORATED` |
| `database` | Porta nell'intervallo del profilo di sistema `db` | `INFERRED` |

### Firme WAF note

Rilevate tramite un'intestazione dichiarativa (`server`, `x-sdk`) — presenza **dichiarata dalla destinazione**, mai verificata in modo indipendente: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (elencato a titolo indicativo, non è propriamente un WAF applicativo).

## 8. Grafo di architettura

Ricostruito unicamente dalla provenienza già portata da ogni host accettato (`discovered_from`/`discovery_source`/`discovery_confidence`) — nessuna nuova richiesta di rete, nessuna nuova analisi degli indizi grezzi.

### Relazioni prodotte

| Relazione | Fonte di scoperta | Significato |
|---|---|---|
| `proxy_to` | `header` | La destinazione radice (o un host già accettato) è verosimilmente un proxy verso la destinazione scoperta |
| `redirect_to` | `redirection` | Reindirizzamento HTTP osservato verso la destinazione scoperta |
| `linked_to` | `certificate` o `html_link` | La relazione più neutra — infrastruttura/applicazione condivisa, senza affermare una direzione di flusso |

`backend_of` (l'arco inverso di un `proxy_to`) volutamente non viene prodotto — sarebbe un'informazione duplicata, non una nuova deduzione.

### Resa

- **TUI** (dettaglio di un'analisi) ed **esportazioni JSON/testo**: elenco degli archi (origine, relazione, destinazione, fiducia) — un terminale non è il posto per una resa grafica ricca.
- **Esportazione HTML**: un **vero diagramma SVG** (nodi = cerchi, archi = frecce etichettate), impaginazione a livelli calcolata dalla destinazione radice, dimensione proporzionale al numero di macchine scoperte — mai una pesante dipendenza di layout di grafi; il grafo resta piccolo per costruzione (limitato dalle salvaguardie del [§4](#4-scoperta-delle-destinazioni-e-salvaguardie)).

## 9. Politica di fiducia

Ogni campo raccolto porta uno di questi livelli:

| Livello | Significato |
|---|---|
| `VERIFIED` | Fatto di protocollo osservato direttamente, che la destinazione non può falsificare (es.: porta chiusa confermata da un RST TCP, versione TLS realmente negoziata). |
| `DECLARED` | Valore autodichiarato dalla destinazione in un campo che controlla interamente (es.: banner `Server`, intestazione `X-Backend-Server`) — plausibile ma falsificabile a piacere. |
| `CORROBORATED` | Un valore `DECLARED` confermato da un indizio indipendente (es.: ruolo SSH, essendo il protocollo realmente negoziato). |
| `INFERRED` | Dedotto da uno schema/euristica, senza dichiarazione esplicita della destinazione (es.: link HTML). |
| `UNKNOWN` | Nessun indizio utilizzabile, oppure nascosto attivamente dalla destinazione. |

## 10. Protezione contro i valori falsificati

Omega-deep non si fida di alcun dato autodichiarato dalla destinazione senza segnalarlo esplicitamente — e la scoperta delle destinazioni è la parte più delicata del progetto: una destinazione malevola *potrebbe* annunciare un `X-Backend-Server` falso per orientare la scoperta verso un IP di sua scelta. Due protezioni strutturali, indipendenti l'una dall'altra:
- Nessuna informazione derivata da una destinazione è mai `VERIFIED` per il solo fatto di essere annunciata — un banner `Server` o un'intestazione `X-Backend-Server` resta `DECLARED`, per quanto plausibile.
- La salvaguardia di perimetro ([§4](#4-scoperta-delle-destinazioni-e-salvaguardie)) limita dove può portare una destinazione annunciata (stesso `/24` privato, salvo configurazione esplicita), e la convalida dell'utente limita se viene analizzata o meno — una destinazione falsa fuori dal perimetro non viene nemmeno proposta; una destinazione nel perimetro resta soggetta a conferma esplicita prima di qualsiasi scansione.

## 11. Compatibilità con i terminali

La TUI (Textual) rileva automaticamente le capacità del terminale (emulatore, dimensioni) e adatta di conseguenza il suo foglio di stile strutturale (`complete`/`standard`/`reduced`/`mono`), senza opzioni manuali. La modalità CLI resta sempre in testo semplice, indipendente dal terminale. Politica condivisa da tutta la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Profilo secondo l'emulatore rilevato

| Emulatore | Profilo iniziale |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH datato | `mono` |
| Emulatore non riconosciuto | `reduced` (ripiego predefinito) |

### Profilo secondo le dimensioni del terminale

| Dimensione minima (colonne × righe) | Tetto del profilo |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| al di sotto | `mono` |

Il profilo finale è **il più restrittivo dei due** (emulatore e dimensioni) — un Ghostty a schermo intero ridimensionato a 70 colonne scende a `mono`, anche se il suo emulatore consentirebbe `complete`. Aggiornabile in tempo reale con il tasto `r`.

## 12. Esportazioni

I report testo e HTML vengono scritti nella lingua scelta nelle Impostazioni («Lingua delle esportazioni», per impostazione predefinita quella dell'interfaccia); il JSON resta un dato, non tradotto. I report vengono generati in `var/exports/` per impostazione predefinita (percorso di esecuzione ancorato alla cartella del progetto, `$OMEGA_DEEP_VAR_DIR` per sovrascriverlo), oppure nel percorso indicato (`--output` in CLI, finestra di dialogo in TUI). Nome di file esplicito e con data e ora: `analyse-{profilo}-{data}.ext`, `analyse-custom-{data}.ext` per un profilo personale.

### JSON, fonte di verità

Struttura completa dell'analisi (`Scan` + `Host[]` + `ArchitectureGraph`), rigorosamente serializzabile in JSON, livelli di fiducia inclusi.

### Testo, report leggibile compatto

Leggibile fuori dal terminale, senza codici ANSI — grafo come elenco di archi.

### HTML, report web autonomo

5 temi a scelta (`--theme` in CLI, selettore in TUI; segue per impostazione predefinita il tema attivo dell'interfaccia quando esiste un equivalente). Impaginazione dedicata: contenitore, griglia di informazioni, riquadri di statistiche per stato della porta, badge colorati, **diagramma SVG del grafo di architettura** (vedi [§8](#8-grafo-di-architettura)) — stessa famiglia visiva di `omega-scan`/`omega-check`.

## 13. Cronologia e confronto

Ogni analisi viene salvata (SQLite, `var/db/omega-deep.db`): un `scan_id` porta la destinazione radice **e** tutti gli host scoperti/accettati, oltre al grafo ricostruito. Cronologia consultabile per destinazione radice (con una colonna dedicata al numero di destinazioni scoperte), dettaglio di un'analisi passata (host + grafo), confronto tra due analisi (stato delle porte della sola **destinazione radice** — confrontare i grafi di scoperta sarebbe un'estensione possibile, non necessaria per ora) e ripetizione di un'analisi sulla stessa destinazione radice senza reinserirla.

## 14. Test

```bash
source .venv/bin/activate
lint-imports        # verifica la Dependency Rule
pytest -q           # 191 test
ruff check src tests
mypy -p omega_deep
```

Struttura: `tests/unit/` (dominio e applicazione, senza I/O reale), `tests/integration/` (SQLite/file reali, server HTTP fittizio `pytest-httpserver`, TLS tramite `trustme`), `tests/tui/` (navigazione via `Pilot`, strutturale — nessuna verifica visiva autodichiarata).

## 15. Fuori perimetro

- Scansione di CVE
- Rilevamento attivo di SQLi, XSS, RCE
- Rilevamento del sistema operativo
- Tecniche di scansione a basso livello in stile nmap (SYN scan, pacchetti grezzi)
- Crawling
- Fuzzing
- Forza bruta
- Analizzare una destinazione scoperta senza conferma esplicita — mai, in nessuna modalità
- Scoperta fuori dalla sottorete privata della destinazione iniziale senza configurazione esplicita
- Dashboard web

---

> Omega-deep — Scoprire, mappare, qualificare, riferire.
> Un'architettura ricostruita con una fiducia esplicita, mai una supposizione travestita da fatto.
