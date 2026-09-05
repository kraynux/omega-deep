<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencia MIT (consulta el archivo LICENSE) -->
<div align="center">
  <img src="docs/assets/omega-deep.png" alt="Omega-Deep" width="256">
</div>

# 🖧 OMEGA-DEEP

**Análisis de arquitectura multiobjetivo (descubrimiento + salvaguardas + grafo)**

> Desarrollado por **kraynux** para **Omega-server**  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Página oficial: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Vista previa: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**Idiomas:**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)

---

**Omega-deep** retoma todo lo que hace `omega-check` sobre un objetivo único (escaneo de puertos, identificación de servicios, roles, WAF y TLS) y añade el **descubrimiento de objetivos adicionales** a partir de los indicios dejados por el objetivo ya escaneado (cabeceras, redirecciones, certificado y enlaces HTML), bajo **salvaguardas estrictas** y con **validación explícita del usuario** antes de escanear cualquier objetivo descubierto. Después **reconstruye un grafo de arquitectura**: quién se comunica con quién y con qué nivel de confianza. Es la quinta herramienta de la suite `omega-` (después de `omega-fire`, `omega-stress`, `omega-scan` y `omega-check`), estructurada según Clean Architecture; consulta `docs/ARCHITECTURE.md` para ver el detalle técnico completo.

## 1. Visión y alcance

Omega-deep responde a una pregunta que omega-check no plantea: *¿qué hay detrás de esta IP?* Un proxy inverso que anuncia su backend, un certificado que cubre varios hosts o una página que enlaza con un servicio vecino son indicios que omega-deep sigue con prudencia, pero nunca utiliza para escanear automáticamente.

### Qué hace Omega-deep

- Escanea un objetivo raíz exactamente como omega-check (perfil del sistema o perfil personal guardado).
- Descubre objetivos candidatos a partir de los indicios dejados por cada host ya escaneado: cabeceras HTTP (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), redirecciones (`Location`), certificado TLS (SAN) y enlaces HTML; consulta [§4](#4-descubrimiento-de-objetivos-y-salvaguardas).
- **Nunca** escanea un objetivo descubierto sin validación explícita, objetivo por objetivo: el silencio nunca equivale a aceptación.
- Limita el descubrimiento mediante salvaguardas estrictas: profundidad máxima, número máximo de objetivos adicionales y subred permitida (por defecto, el mismo rango privado que el objetivo raíz).
- Reconstruye un **grafo de arquitectura** a partir del origen de cada objetivo aceptado (`proxy_to`, `redirect_to`, `linked_to`), con un nivel de confianza por relación; consulta [§8](#8-grafo-de-arquitectura).
- Presenta el resultado en TUI (Textual) o CLI programable, con las mismas tres exportaciones que omega-check (JSON, texto y HTML con 5 temas); en HTML el grafo es un **diagrama real dibujado**, no una tabla.
- Califica cada dato recopilado (servicio o descubrimiento) con un nivel de confianza explícito; consulta [§9](#9-política-de-confianza).
- Conserva un historial persistente de los análisis, que se puede volver a ejecutar y comparar con el tiempo.

### Qué no hace Omega-deep

- No realiza escaneo activo de vulnerabilidades, SQLi, XSS ni RCE.
- No escanea CVE.
- No identifica el sistema operativo.
- No utiliza técnicas de escaneo de bajo nivel como nmap (SYN scan, paquetes sin procesar): únicamente conexiones TCP de nivel aplicativo.
- No es una herramienta de bruteforce ni fuzzing.
- No escanea un objetivo descubierto sin confirmación explícita del usuario, nunca y bajo ningún modo.
- No descubre más allá de la subred privada del objetivo inicial, salvo configuración explícita (`--subnet`).
- No proporciona un dashboard web.

## 2. Instalación

### Requisitos

- Python 3.10+
- Conexión a Internet para las dependencias

### Instalación

```bash
[ -d omega-deep ] && echo "ℹ️ Ya está extraído aquí; se omite el paso." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea el entorno virtual `.venv` si todavía no existe.
2. Instala las dependencias (`vendor/omega-lib/` y después `pip install -e .`; `pyproject.toml` sigue siendo la única fuente de verdad).
3. Hace ejecutables `omega-deep.sh` e `install.sh`.
4. Añade el alias `deep` a `~/.bashrc` y `~/.zshrc`, sin duplicarlo si ya existe.

### Dependencias

Declaradas en `pyproject.toml` (ya no existe `requirements.txt`):
- `omega-lib`: biblioteca compartida de la suite (`ConfidenceLevel`, temas y detección del terminal), incluida en `vendor/omega-lib/`.
- `textual`: interfaz TUI, temas y adaptación automática al terminal.
- `httpx`: sondas HTTP/HTTPS para servicios y descubrimiento.
- `cryptography`: lectura del certificado TLS negociado.
- `jinja2`: plantillas para la exportación HTML.
- Dependencias de desarrollo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`.

## 3. Uso

### Modo interactivo (TUI)

Recomendado para el uso diario; se inicia sin argumentos:

```bash
./omega-deep.sh
```

Si has creado el alias, basta con escribir en el terminal:

```bash
deep
```

Flujo: pantalla de inicio (se cierra con una tecla o un clic) → menú principal (Analizar / Perfiles / Historial / Ajustes / Ayuda) → introducción del objetivo raíz, selección del perfil y de las salvaguardas de descubrimiento (profundidad máxima, número máximo de objetivos y subred permitida) → análisis (indicador indeterminado y operaciones de red en directo) → para cada lote de objetivos descubiertos, pantalla de validación (una línea por objetivo, con origen/confianza/prueba; selector aceptar/rechazar, sin ninguna casilla marcada por defecto) → detalle del análisis (hosts, puertos/servicios/roles, grafo y exportación) → historial, comparación, repetición y ajustes desde el menú principal. La adaptación al terminal (colores, tamaño y degradación estructural) es automática.

#### Atajos de teclado

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Navegar entre los elementos de una pantalla |
| `Tab` / `Mayús+Tab` | Navegar entre los campos de un formulario |
| `Esc` | Volver a la pantalla anterior (confirmación de salida en la pantalla de inicio) |
| `t` | Siguiente tema (se aplica inmediatamente, sin confirmación) |
| `r` | Actualizar la detección del terminal |
| `a` | Mostrar la ayuda |
| `q` | Salir con confirmación |

### Modo programable (CLI)

Cualquier subcomando activa el modo CLI:

```bash
# Analizar un objetivo (escaneo raíz + descubrimiento multiobjetivo)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Historial (filtrable por objetivo raíz)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Detalle de un análisis (texto, JSON o HTML), con 5 temas de exportación disponibles
./omega-deep.sh show <scan_id> --format html --theme omega-base --output rapport.html

# Comparar dos análisis (estado de los puertos del objetivo raíz)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Perfiles personales de puertos
./omega-deep.sh profile list
./omega-deep.sh profile create labo --ports 22,80,443 --description "Mi perfil"
./omega-deep.sh profile edit labo --ports 22,80,443,8080
./omega-deep.sh profile pin labo
./omega-deep.sh profile unpin labo
./omega-deep.sh profile delete labo
```

En CLI, la validación de los objetivos descubiertos se realiza mediante una pregunta interactiva por objetivo (`¿Escanear <objetivo>? [s/N]`), mostrando antes la prueba correspondiente. `--auto-validate` acepta todo sin revisión (**no recomendado**, se muestra una advertencia); en un entorno no interactivo (sin TTY y sin `--auto-validate`), todos los objetivos descubiertos se rechazan por defecto en vez de escanearse sin confirmación.

### Formatos de objetivo aceptados

```text
192.168.1.10                IPv4
example.org                 Nombre de host
http://example.org          URL HTTP (se elimina el esquema antes de resolver)
https://example.org:8443    URL HTTPS con puerto (se eliminan esquema y puerto)
```

El esquema y el puerto opcionales se eliminan antes de la resolución DNS (`domain/targets/validation.py::normalize_target_input`): se puede pegar una URL completa y solo se conserva el host. Los objetivos *descubiertos* se normalizan de la misma forma, pero nunca se escanean sin validación; consulta [§4](#4-descubrimiento-de-objetivos-y-salvaguardas).

## 4. Descubrimiento de objetivos y salvaguardas

### Fuentes de indicios

| Fuente | Origen | Confianza |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | Cabecera `Location` de una respuesta HTTP | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) del certificado TLS negociado | `DECLARED` |
| `html_link` | Enlaces (`<a href>`) servidos por la página | `INFERRED` |

Un valor `DECLARED` sigue siendo una autodeclaración del objetivo y puede falsificarse; consulta [§10](#10-protección-contra-valores-falsificados). `html_link` es deliberadamente la fuente más débil: un simple enlace no declara ninguna relación de infraestructura.

### Salvaguardas (siempre activas y no desactivables)

- **Ámbito**: el candidato debe ser una IP privada del mismo `/24` que el objetivo raíz, salvo que se indique `--subnet`. En ese caso solo cuenta la pertenencia a la subred indicada, incluso si incluye IP públicas: la excepción queda autorizada por la configuración explícita. Un nombre de host sin resolver nunca se acepta mediante este filtro.
- **Profundidad**: `--max-depth` (por defecto 3): como máximo A → B → C → D.
- **Número de objetivos**: `--max-targets` (por defecto 10), sumando todas las profundidades.

### Validación (nunca se escanea sin confirmación)

Cada objetivo propuesto sigue `PROPOSED → PRESENTED → ACCEPTED` o `REJECTED`. La regla **fail-safe** establece que todo objetivo que no haya sido aceptado explícitamente (silencio, cierre de pantalla, interrupción, tiempo de espera o ausencia de TTY) se trata como rechazado, nunca al contrario. En TUI, una pantalla específica enumera los objetivos del lote con su prueba y confianza, permite aceptar o rechazar cada línea, aceptar o rechazar todo y rechaza todo por defecto al pulsar Esc. En CLI hay una pregunta por objetivo; `--auto-validate` (no recomendado) es la única forma de evitar la interacción.

## 5. Perfiles de escaneo

| Perfil | Descripción | Fijado |
|---|---|---|
| `minimal` | Escaneo ultrarrápido: SSH + HTTP + HTTPS (22, 80, 443) | sí |
| `classic` | Servicios clásicos de Internet/LAN | sí |
| `web` | Servicios web y alternativas | no |
| `db` | Bases de datos y servicios de datos | no |
| `remote` | Acceso remoto: shell, escritorio y RustDesk | no |
| `mail` | Servicios de correo | no |
| `dns` | Servicios DNS | no |
| `iot` | Dispositivos IoT, cámaras, routers y domótica | no |
| `dev` | Entornos de desarrollo/laboratorio | no |
| `docker` | Docker, Swarm y servicios habituales en contenedores | no |
| `complet` | **Generado al vuelo**: unión ordenada y sin duplicados de todos los perfiles anteriores | no |
| *perfil personal* | Se crea en la pantalla **Perfiles** (TUI) o con `profile create` (CLI), aparece junto a los perfiles del sistema y lleva el prefijo `* ` en TUI | no |

El perfil se aplica al objetivo raíz **y** a cada objetivo descubierto aceptado: no hay un perfil distinto por host. Descripción completa, reglas de validación y gestión de perfiles personales: `docs/PROFILES.md`.

## 6. Arquitectura

Omega-deep está estructurado mediante **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), alineado con la plantilla de la suite `omega-` (consulta `omega-scan`/`omega-check`) y verificado por `import-linter` en cada modificación. El detalle completo se encuentra en **`docs/ARCHITECTURE.md`**.

Vista general breve:

```text
src/omega_deep/
├── domain/          Lógica de negocio pura: escaneos, objetivos, servicios, perfiles,
│                    informes, discovery (objetivos propuestos, máquina de estados
│                    de validación), architecture (grafo y reglas de relación)
├── application/     Casos de uso (commands/queries), incluidos discover_targets,
│                    validate_targets, reconstruct_architecture
│                    (nuevos respecto a omega-check)
├── ports/           Contratos esperados por la aplicación (probers, incluido
│                    discovery_prober, repositories, exporters...)
├── infrastructure/  Implementaciones concretas (socket/httpx/cryptography, SQLite,
│                    renderizado SVG del grafo; Textual NO está aquí)
├── interfaces/      tui/ (Textual) y cli/ (programable), con estricta paridad funcional
├── app/             Ensamblaje (DependencyContainer, bootstrap y ciclo de vida)
├── core/, shared/   Vocabulario transversal y utilidades no pertenecientes al dominio
└── plugins/         Estructura preparada y vacía (sin eje de extensión confirmado)
```

Reglas de diseño:
- `domain/services/policies.py`: clasifica los indicios ya recopilados y nunca hace red.
- `domain/discovery/policies.py`: salvaguardas de ámbito, profundidad y cantidad; lógica pura, comprobable sin red.
- `domain/architecture/service.py`: reconstruye el grafo a partir del origen ya almacenado en cada `Host`, sin repetir solicitudes.
- `infrastructure/network/` e `infrastructure/discovery/`: realizan operaciones de red (sockets, `httpx`, `cryptography`), pero nunca juzgan.
- `interfaces/`: muestran datos y no contienen lógica de negocio. La pantalla de validación llama a `validate_targets`, pero no implementa por sí misma la regla fail-safe.
- `infrastructure/exporters/`: leen el resultado del análisis (escaneo, hosts y grafo), sin recalcular nada.

## 7. Identificación de servicios y roles

### Protocolos detectados

| Protocolo | Sonda | Datos recopilados |
|---|---|---|
| HTTP / HTTPS | `httpx` | Banner `Server`, cabeceras de autenticación |
| TLS | `cryptography` (certificado negociado, incluido `CERT_NONE`) | Versión, cipher, sujeto/emisor del certificado |
| SSH | Banner sin procesar | Software y versión (por ejemplo, `OpenSSH 10.4`) |
| VNC (RFB) | Códigos de seguridad anunciados por el servidor | Tipos de autenticación compatibles |
| Genérico | Banner sin procesar en un puerto abierto no reconocido | Extracción prudente, sin heurística agresiva |

### Roles inferidos

Se deducen del protocolo **realmente negociado**, nunca de una suposición basada en el número de puerto:

| Rol | Condición | Confianza |
|---|---|---|
| `servidor web` | Protocolo HTTP/HTTPS confirmado | `INFERRED` |
| `acceso shell` | Protocolo SSH confirmado | `CORROBORATED` |
| `acceso gráfico` | Protocolo VNC confirmado | `CORROBORATED` |
| `base de datos` | El puerto pertenece al rango del perfil de sistema `db` | `INFERRED` |

### Firmas WAF conocidas

Se detectan mediante cabeceras declarativas (`server`, `x-sdk`). Su presencia es **declarada por el objetivo** y nunca se verifica de forma independiente: Cloudflare, Sucuri, Akamai, Imperva Incapsula y AWS ELB (incluido como referencia; estrictamente, no es un WAF de aplicación).

## 8. Grafo de arquitectura

Se reconstruye únicamente a partir del origen ya almacenado en cada host aceptado (`discovered_from`/`discovery_source`/`discovery_confidence`): no se realizan nuevas solicitudes de red ni se vuelven a analizar los indicios originales.

### Relaciones generadas

| Relación | Fuente de descubrimiento | Significado |
|---|---|---|
| `proxy_to` | `header` | El objetivo raíz (o un host ya aceptado) probablemente actúa como proxy hacia el objetivo descubierto |
| `redirect_to` | `redirection` | Se observó una redirección HTTP hacia el objetivo descubierto |
| `linked_to` | `certificate` o `html_link` | Relación más neutral: infraestructura/aplicación compartida, sin afirmar la dirección del flujo |

No se genera `backend_of` (la arista inversa de `proxy_to`) porque sería información duplicada y no una nueva deducción.

### Representación

- **TUI** (detalle del análisis) y **exportaciones JSON/texto**: lista de aristas (origen, relación, objetivo y confianza); un terminal no es el lugar adecuado para gráficos complejos.
- **Exportación HTML**: un **diagrama SVG real** (nodos = círculos; aristas = flechas etiquetadas), con disposición por capas calculada desde el objetivo raíz y tamaño proporcional al número de máquinas descubiertas. No se necesita una dependencia pesada de layout: el grafo es pequeño por construcción y está limitado por las salvaguardas de [§4](#4-descubrimiento-de-objetivos-y-salvaguardas).

## 9. Política de confianza

Cada campo recopilado recibe uno de estos niveles:

| Nivel | Significado |
|---|---|
| `VERIFIED` | Hecho protocolario observado directamente que el objetivo no puede falsificar (por ejemplo, un puerto cerrado confirmado por TCP RST o una versión TLS realmente negociada). |
| `DECLARED` | Valor anunciado por el objetivo en un campo que controla por completo (por ejemplo, el banner `Server` o la cabecera `X-Backend-Server`): plausible, pero falsificable. |
| `CORROBORATED` | Valor `DECLARED` confirmado por un indicio independiente (por ejemplo, un rol SSH cuyo protocolo se negoció realmente). |
| `INFERRED` | Deducción basada en un patrón o heurística, sin declaración explícita del objetivo (por ejemplo, un enlace HTML). |
| `UNKNOWN` | No hay indicios útiles o el objetivo los oculta activamente. |

## 10. Protección contra valores falsificados

Omega-deep no confía automáticamente en los datos autodeclarados por el objetivo y lo señala de forma explícita. El descubrimiento de objetivos es especialmente sensible: un objetivo malicioso *podría* anunciar un `X-Backend-Server` falso para dirigir el descubrimiento a una IP elegida. Se aplican dos protecciones estructurales independientes:
- Ninguna información derivada de un objetivo recibe `VERIFIED` simplemente por haber sido anunciada: un banner `Server` o una cabecera `X-Backend-Server` sigue siendo `DECLARED`, por muy plausible que parezca.
- La salvaguarda de ámbito ([§4](#4-descubrimiento-de-objetivos-y-salvaguardas)) limita adónde puede conducir un objetivo anunciado (el mismo `/24` privado, salvo configuración explícita), y la validación del usuario determina si se escanea. Un objetivo falso fuera del ámbito ni siquiera se propone; uno dentro del ámbito sigue requiriendo confirmación explícita.

## 11. Compatibilidad con terminales

La TUI (Textual) detecta automáticamente las capacidades del terminal (emulador y tamaño) y adapta en consecuencia su hoja de estilos estructural (`complete`/`standard`/`reduced`/`mono`), sin flags manuales. El modo CLI siempre usa texto simple y es independiente del terminal. La política es común a toda la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Perfil según el emulador

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH antiguo | `mono` |
| Emulador no reconocido | `reduced` (fallback predeterminado) |

### Perfil según el tamaño del terminal

| Tamaño mínimo (columnas × filas) | Límite de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| inferior | `mono` |

El perfil final es **el más restrictivo de los dos** (emulador y tamaño). Un Ghostty en pantalla completa reducido a 70 columnas bajará a `mono`, aunque su emulador permitiría `complete`. Se puede actualizar en directo con la tecla `r`.

## 12. Exportaciones

Los informes se generan por defecto en `var/exports/` (la ruta de ejecución se ancla al directorio del proyecto; se puede sobrescribir con `$OMEGA_DEEP_VAR_DIR`) o en la ruta indicada (`--output` en CLI, diálogo en TUI). El nombre de archivo es explícito e incluye la fecha: `analyse-{profil}-{date}.ext`; para un perfil personal, `analyse-custom-{date}.ext`.

### JSON, fuente de verdad

Estructura completa del análisis (`Scan` + `Host[]` + `ArchitectureGraph`), estrictamente serializable como JSON e incluyendo los niveles de confianza.

### Texto, informe humano compacto

Legible fuera del terminal, sin códigos ANSI; el grafo aparece como una lista de aristas.

### HTML, informe web autónomo

5 temas disponibles (`--theme` en CLI o selector en TUI; por defecto sigue el tema activo de la interfaz cuando existe un equivalente). Diseño específico: contenedor, cuadrícula de información, bloques estadísticos por estado de puerto, badges de colores y **diagrama SVG del grafo de arquitectura** (consulta [§8](#8-grafo-de-arquitectura)), con la misma familia visual que `omega-scan`/`omega-check`.

## 13. Historial y comparación

Cada análisis se guarda en SQLite (`var/db/omega-deep.db`): un `scan_id` contiene el objetivo raíz, todos los hosts descubiertos y aceptados, y el grafo reconstruido. El historial se puede consultar por objetivo raíz, con una columna dedicada al número de objetivos descubiertos; también se puede ver el detalle de un análisis anterior (hosts y grafo), comparar dos análisis (solo el estado de los puertos del **objetivo raíz**; comparar grafos de descubrimiento sería una ampliación posible, pero no necesaria actualmente) y repetir un análisis sobre el mismo objetivo raíz sin volver a introducirlo.

## 14. Pruebas

```bash
source .venv/bin/activate
lint-imports        # verifica la Dependency Rule
pytest -q           # 173 pruebas
ruff check src tests
mypy -p omega_deep
```

Estructura: `tests/unit/` (dominio y aplicación, sin I/O real), `tests/integration/` (SQLite/archivos reales, servidor HTTP ficticio `pytest-httpserver`, TLS mediante `trustme`) y `tests/tui/` (navegación con `Pilot`, comprobaciones estructurales; no se declara una verificación visual automática).

## 15. Fuera del alcance

- Escaneo de CVE.
- Detección activa de SQLi, XSS y RCE.
- Identificación del sistema operativo.
- Técnicas de escaneo de bajo nivel como nmap (SYN scan, paquetes sin procesar).
- Crawling.
- Fuzzing.
- Bruteforce.
- Escaneo de un objetivo descubierto sin confirmación explícita, nunca y bajo ningún modo.
- Descubrimiento fuera de la subred privada del objetivo inicial sin configuración explícita.
- Dashboard web.

---

> Omega-deep — descubrir, cartografiar, calificar e informar.  
> Una arquitectura reconstruida con confianza explícita, nunca una suposición disfrazada de hecho.
