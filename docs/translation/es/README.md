<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencia MIT (ver el archivo LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-deep.png" alt="Omega-Deep" width="512">
</div>

# 🖧 OMEGA-DEEP

**Análisis de arquitectura multiobjetivo (descubrimiento + salvaguardas + grafo)**

> Desarrollado por [kraynux](https://github.com/kraynux) para [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Página oficial: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Capturas: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfaz e informes exportados disponibles en **17 idiomas** — ver [Idiomas de la interfaz](#idiomas-de-la-interfaz).  
**Idiomas:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** hace todo lo que hace `omega-check` sobre un objetivo único (escaneo de puertos, identificación de servicios, roles, WAF, TLS) y añade el **descubrimiento de objetivos adicionales** a partir de los indicios que deja el objetivo ya escaneado (cabeceras, redirecciones, certificado, enlaces HTML), bajo **salvaguardas estrictas** y una **validación explícita del usuario** antes de escanear cualquier objetivo descubierto, y después **reconstruye un grafo de arquitectura** (quién habla con quién, con qué confianza). Herramienta de la suite `omega-`, estructurada en Clean Architecture — ver `docs/ARCHITECTURE.md` para todos los detalles técnicos.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/es/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/es/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/es/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/es/omega-deep/D.png" width="24%" />
</p>

## 1. Visión y alcance

Omega-deep responde a una pregunta que omega-check no se plantea: *detrás de esta IP, ¿qué más hay?* Un proxy inverso que anuncia su backend, un certificado que cubre varios hosts, una página que apunta a un servicio vecino — otros tantos indicios que omega-deep sigue, con prudencia, nunca por su cuenta.

### Lo que hace Omega-deep

- Escanea un objetivo raíz exactamente como omega-check (perfil del sistema o perfil personal guardado).
- Descubre objetivos candidatos a partir de los indicios que deja cada host ya escaneado: cabeceras HTTP (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), redirección (`Location`), certificado TLS (SAN), enlaces HTML — ver [§4](#4-descubrimiento-de-objetivos-y-salvaguardas).
- **Nunca** escanea un objetivo descubierto sin validación explícita, objetivo por objetivo — el silencio nunca es una aceptación.
- Limita el descubrimiento con salvaguardas estrictas: profundidad máxima, número máximo de objetivos adicionales, subred permitida (por defecto, el mismo rango privado que la raíz).
- Reconstruye un **grafo de arquitectura** a partir de la procedencia de cada objetivo aceptado (`proxy_to`, `redirect_to`, `linked_to`), con un nivel de confianza por relación — ver [§8](#8-grafo-de-arquitectura).
- Presenta el resultado en TUI (Textual) o en CLI scriptable, con las mismas tres exportaciones que omega-check (JSON, texto, HTML con 5 temas) — el grafo es allí un **diagrama dibujado de verdad** en HTML, no una tabla.
- Asigna a cada información recogida (servicio o descubrimiento) un nivel de confianza explícito — ver [§9](#9-política-de-confianza).
- Conserva un historial persistente de análisis, repetible y comparable en el tiempo.

### Lo que Omega-deep no hace

- Escaneo activo de vulnerabilidades: nada de SQLi, XSS ni RCE.
- Escaneo de CVE.
- Identificación del sistema operativo.
- Técnicas de escaneo de bajo nivel al estilo nmap (SYN scan, paquetes en bruto) — solo conexión TCP de aplicación.
- Herramienta de fuerza bruta o de fuzzing.
- Escanear un objetivo descubierto sin confirmación explícita del usuario — nunca, en ningún modo.
- Descubrimiento más allá de la subred privada del objetivo inicial, salvo configuración explícita (`--subnet`).
- Panel web.

## 2. Instalación

### Requisitos

- Python 3.10+
- Conexión a Internet, para las dependencias

### Instalación

```bash
[ -d omega-deep ] && echo "ℹ️ Ya extraído aquí, paso omitido." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea el entorno virtual `.venv` si aún no existe.
2. Instala las dependencias (`vendor/omega-lib/` y luego `pip install -e .`; `pyproject.toml` sigue siendo la única fuente de verdad).
3. Hace ejecutables `omega-deep.sh` e `install.sh`.
4. Añade el alias `deep` a `~/.bashrc` y `~/.zshrc` (sin duplicado si ya está presente).

### Dependencias

Declaradas en `pyproject.toml` (ya sin `requirements.txt`):
- `omega-lib`: biblioteca compartida de la suite (`ConfidenceLevel`, temas, detección del terminal) — incluida en `vendor/omega-lib/`
- `textual`: interfaz TUI, temas, adaptación automática al terminal
- `httpx`: sondas HTTP/HTTPS (servicio y descubrimiento)
- `cryptography`: lectura del certificado TLS negociado
- `jinja2`: plantillas para la exportación HTML
- Dependencias de desarrollo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Uso

### Modo interactivo (TUI)

Recomendado para el uso diario — se lanza sin argumentos:

```bash
./omega-deep.sh
```
si ha creado el alias, escriba simplemente `deep` en el terminal:
```bash
deep
```

Recorrido: pantalla de inicio (se cierra con una tecla o un clic) → menú principal (Analizar / Perfiles / Historial / Ajustes / Ayuda) → introducción del objetivo raíz, elección del perfil y de las salvaguardas de descubrimiento (profundidad máxima, número máximo de objetivos, subred permitida) → análisis (indicador indeterminado y registro de las operaciones de red en directo) → en cada lote de objetivos descubiertos, pantalla de validación (una línea por objetivo, con origen/confianza/prueba visibles, conmutador aceptar/rechazar — nada marcado por defecto) → detalle del análisis (hosts, puertos/servicios/roles, grafo, exportación) → historial/comparación/repetición y ajustes desde el menú principal. La adaptación al terminal (colores, tamaño, degradación estructural) es automática.

#### Atajos de teclado

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Moverse entre los elementos de una pantalla |
| `Tab` / `Mayús+Tab` | Moverse entre los campos de un formulario |
| `Esc` | Volver a la pantalla anterior (confirmación de salida en la pantalla de inicio) |
| `t` | Tema siguiente (aplicado de inmediato, sin confirmación) |
| `r` | Actualizar la detección del terminal |
| `a` | Mostrar la ayuda |
| `q` | Salir (con confirmación) |

### Idiomas de la interfaz

La interfaz está disponible en 17 idiomas: francés, inglés, español, portugués (Brasil), italiano, alemán, neerlandés, polaco, ruso, chino simplificado, vietnamita, tailandés, indonesio, japonés, coreano, hindi y árabe. La elección se hace en Ajustes («Langue / Language») y se aplica tras reiniciar la interfaz; la variable `OMEGA_DEEP_LANG` (por ejemplo `OMEGA_DEEP_LANG=es ./omega-deep.sh`) fuerza un idioma durante una sesión. Lanzado desde omega-suite, omega-deep adopta el idioma de la suite. En una consola de texto Linux (TTY), los idiomas de escritura no latina se muestran en inglés durante la sesión. La línea de comandos sigue en francés.

### Contacto y soporte

La ayuda (tecla `a`) ofrece una pantalla **Contacto y soporte**: *Invitar a un café* (página PayPal del desarrollador), *Contactar con el soporte* (dirección de correo y formulario de contacto del sitio, mostrados en claro), *Declararme usuario (anónimo)* y *Buscar actualizaciones*. La declaración es voluntaria, está desactivada por defecto y se envía una sola vez: solo sirve para contar a los usuarios y, si se desea, su continente o su país (listas cerradas, nunca texto libre). Envía una clave elegida al azar, el nombre del programa (`omega-deep`) y su versión; nunca un nombre, un nombre de máquina, un ajuste, un objetivo ni un resultado. La dirección IP no se registra en las declaraciones, pero, como en cualquier visita, pasa por los controles de seguridad y el registro del servidor de recepción. Retirada en cualquier momento desde la misma pantalla (*Dejar de declararme*). La búsqueda de actualizaciones solo lee la lista de versiones publicadas en el sitio, y nunca sin un clic.

### Modo scriptable (CLI)

Cualquier subcomando activa el modo CLI:

```bash
# Analizar un objetivo (escaneo raíz + descubrimiento multiobjetivo)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Historial (filtrable por objetivo raíz)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Detalle de un análisis (texto, JSON o HTML) — 5 temas de exportación a elegir
./omega-deep.sh show <scan_id> --format html --theme omega-base --output informe.html

# Comparar dos análisis (estado de los puertos del objetivo raíz)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Perfiles de puertos personales
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "Mi perfil"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

En CLI, los objetivos descubiertos se validan mediante una pregunta interactiva por objetivo (`Scanner <cible> ? [o/N]`, en francés como el resto de la línea de comandos), con el detalle de la prueba mostrado antes de cada pregunta. `--auto-validate` lo acepta todo sin revisión (**desaconsejado**, se muestra un aviso); en un entorno no interactivo (sin TTY y sin `--auto-validate`), todo objetivo descubierto se rechaza por defecto en lugar de escanearse sin confirmación.

### Formatos de objetivo aceptados

```text
192.168.1.10                IPv4
example.org                 Nombre de host
http://example.org          URL HTTP  (esquema eliminado antes de la resolución)
https://example.org:8443    URL HTTPS con puerto  (esquema y puerto eliminados)
```

El esquema y el puerto, si los hay, se eliminan antes de la resolución DNS (`domain/targets/validation.py::normalize_target_input`) — pegar una URL completa funciona, solo se conserva el host. Los objetivos *descubiertos* se normalizan del mismo modo, pero nunca se escanean sin validación (ver [§4](#4-descubrimiento-de-objetivos-y-salvaguardas)).

## 4. Descubrimiento de objetivos y salvaguardas

### Fuentes de indicios

| Fuente | Origen | Confianza |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | Cabecera `Location` de una respuesta HTTP | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) del certificado TLS negociado | `DECLARED` |
| `html_link` | Enlaces (`<a href>`) que sirve la página | `INFERRED` |

Un valor `DECLARED` sigue siendo una autodeclaración del objetivo (falsificable) — ver [§10](#10-protección-contra-valores-falsificados). `html_link` es, a propósito, la fuente más débil: un simple enlace no declara ninguna relación de infraestructura.

### Salvaguardas (siempre activas, nunca desactivables)

- **Perímetro**: un objetivo candidato debe ser una IP privada en el mismo `/24` que el objetivo raíz, salvo `--subnet` explícito (en cuyo caso solo cuenta la pertenencia a la subred indicada, aunque cubra IP públicas — es la configuración explícita la que autoriza la excepción). Un nombre de host sin resolver nunca es aceptado por este filtro (resolverlo para comprobarlo ya sería una acción de red fuera del alcance de esta verificación).
- **Profundidad**: `--max-depth` (3 por defecto) — A → B → C → D como máximo.
- **Número de objetivos**: `--max-targets` (10 por defecto) — en todas las profundidades.

### Validación (nunca un escaneo sin confirmación)

Cada objetivo propuesto sigue `PROPOSED → PRESENTED → ACCEPTED` o `REJECTED`. La regla es **a prueba de fallos**: todo objetivo que nunca se haya aceptado explícitamente (silencio, cierre de pantalla, interrupción, tiempo agotado, ausencia de TTY) se trata como rechazado — nunca al revés. En la TUI, una pantalla propia lista los objetivos de un lote con prueba y confianza, un conmutador aceptar/rechazar por línea, «aceptar todo»/«rechazar todo», y un rechazo total por defecto con Esc. En CLI, una pregunta por objetivo; `--auto-validate` (desaconsejado) es la única forma de eludir la interactividad.

## 5. Perfiles de escaneo

| Perfil | Descripción | Fijado |
|---|---|---|
| `minimal` | Escaneo ultrarrápido: SSH + HTTP + HTTPS (22, 80, 443) | sí |
| `classic` | Servicios clásicos de Internet/LAN | sí |
| `web` | Servicios web y alternativos | no |
| `db` | Bases de datos y servicios de datos | no |
| `remote` | Accesos remotos — shell, escritorio, RustDesk | no |
| `mail` | Servicios de correo | no |
| `dns` | Servicios DNS | no |
| `iot` | Equipos IoT, cámaras, routers, domótica | no |
| `dev` | Entornos de desarrollo/laboratorio | no |
| `docker` | Docker, Swarm y servicios habituales en contenedores | no |
| `complet` | **Generado al vuelo**: unión ordenada y sin duplicados de todos los perfiles anteriores | no |
| *perfil personal* | Creado en la pantalla **Perfiles** (TUI) o con `profile create` (CLI), listado junto a los perfiles del sistema, con el prefijo `* ` en la TUI | no |

El perfil se aplica al objetivo raíz **y** a cada objetivo descubierto aceptado — no hay un perfil distinto por host. Detalle completo, reglas de validación y gestión de los perfiles personales: `docs/PROFILES.md`.

## 6. Arquitectura

Omega-deep está estructurado en **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), alineada con la plantilla de la suite `omega-` (ver `omega-scan`/`omega-check`) y verificada por `import-linter` en cada cambio. Todos los detalles están en **`docs/ARCHITECTURE.md`**.

Vista general muy breve:

```text
src/omega_deep/
├── domain/          Lógica de negocio pura: escaneos, objetivos, servicios, perfiles, informes,
│                    discovery (objetivos propuestos, máquina de estados de validación),
│                    architecture (grafo, reglas de relación)
├── application/     Casos de uso (commands/queries) — entre ellos discover_targets,
│                    validate_targets, reconstruct_architecture (nuevos respecto a omega-check)
├── ports/           Contratos que espera la aplicación (sondas, entre ellas discovery_prober,
│                    repositorios, exportadores...)
├── infrastructure/  Implementaciones concretas (socket/httpx/cryptography, SQLite,
│                    renderizado SVG del grafo — Textual NO está aquí)
├── interfaces/      tui/ (Textual) y cli/ (scriptable), con paridad funcional estricta
├── app/             Ensamblaje (DependencyContainer, bootstrap, ciclo de vida)
├── core/, shared/   Vocabulario transversal, utilidades no de negocio
└── plugins/         Estructura preparada, vacía (ningún eje de extensión confirmado)
```

Reglas de diseño:
- `domain/services/policies.py`: clasifica los indicios ya recogidos, nunca hace red.
- `domain/discovery/policies.py`: salvaguardas de perímetro/profundidad/número — lógica pura, comprobable sin red.
- `domain/architecture/service.py`: reconstruye el grafo a partir de la procedencia que ya lleva cada `Host`, no repite ninguna petición.
- `infrastructure/network/` e `infrastructure/discovery/`: hacen red (sockets, `httpx`, `cryptography`), nunca juzgan.
- `interfaces/`: muestra, no contiene ninguna lógica de negocio — la pantalla de validación de objetivos descubiertos llama a `validate_targets`, no implementa ella misma la regla a prueba de fallos.
- `infrastructure/exporters/`: leen el resultado del análisis (escaneo, hosts, grafo), no recalculan nada.

## 7. Identificación de servicios y roles

### Protocolos detectados

| Protocolo | Sonda | Detalle recogido |
|---|---|---|
| HTTP / HTTPS | `httpx` | Banner `Server`, cabeceras de autenticación |
| TLS | `cryptography` (certificado negociado, `CERT_NONE` incluido) | Versión, cifrado, sujeto/emisor del certificado |
| SSH | Banner en bruto | Software y versión (p. ej. `OpenSSH 10.4`) |
| VNC (RFB) | Códigos de seguridad anunciados por el servidor | Tipos de autenticación admitidos |
| Genérico | Banner en bruto en un puerto abierto no reconocido | Extracción prudente, sin heurística agresiva |

### Roles inferidos

Deducidos del protocolo **realmente negociado**, nunca de una suposición por el número de puerto:

| Rol | Condición | Confianza |
|---|---|---|
| `servidor web` | Protocolo HTTP/HTTPS confirmado | `INFERRED` |
| `acceso shell` | Protocolo SSH confirmado | `CORROBORATED` |
| `acceso gráfico` | Protocolo VNC confirmado | `CORROBORATED` |
| `base de datos` | Puerto dentro del rango del perfil del sistema `db` | `INFERRED` |

### Firmas WAF conocidas

Detectadas mediante una cabecera declarativa (`server`, `x-sdk`) — presencia **declarada por el objetivo**, nunca verificada de forma independiente: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (listado a título indicativo, no es estrictamente un WAF de aplicación).

## 8. Grafo de arquitectura

Se reconstruye únicamente a partir de la procedencia que ya lleva cada host aceptado (`discovered_from`/`discovery_source`/`discovery_confidence`) — ninguna nueva petición de red, ningún reanálisis de los indicios en bruto.

### Relaciones producidas

| Relación | Fuente de descubrimiento | Significado |
|---|---|---|
| `proxy_to` | `header` | El objetivo raíz (o un host ya aceptado) es probablemente un proxy hacia el objetivo descubierto |
| `redirect_to` | `redirection` | Redirección HTTP observada hacia el objetivo descubierto |
| `linked_to` | `certificate` o `html_link` | La relación más neutra — infraestructura/aplicación compartida, sin afirmar ninguna dirección de flujo |

`backend_of` (la arista inversa de un `proxy_to`) no se produce a propósito — sería información duplicada, no una nueva deducción.

### Representación

- **TUI** (detalle de un análisis) y **exportaciones JSON/texto**: lista de aristas (origen, relación, destino, confianza) — un terminal no es el lugar para una representación gráfica rica.
- **Exportación HTML**: un **diagrama SVG de verdad** (nodos = círculos, aristas = flechas con etiqueta), maquetación por capas calculada desde el objetivo raíz, tamaño proporcional al número de máquinas descubiertas — nunca una dependencia pesada de maquetación de grafos; el grafo sigue siendo pequeño por construcción (limitado por las salvaguardas del [§4](#4-descubrimiento-de-objetivos-y-salvaguardas)).

## 9. Política de confianza

Cada campo recogido lleva uno de estos niveles:

| Nivel | Significado |
|---|---|
| `VERIFIED` | Hecho de protocolo observado directamente, que el objetivo no puede falsificar (p. ej.: puerto cerrado confirmado por un RST TCP, versión TLS realmente negociada). |
| `DECLARED` | Valor autoanunciado por el objetivo en un campo que controla por completo (p. ej.: banner `Server`, cabecera `X-Backend-Server`) — plausible pero falsificable a voluntad. |
| `CORROBORATED` | Un valor `DECLARED` confirmado por un indicio independiente (p. ej.: rol SSH, al haberse negociado realmente el protocolo). |
| `INFERRED` | Deducido de un patrón/heurística, sin declaración explícita del objetivo (p. ej.: enlace HTML). |
| `UNKNOWN` | Ningún indicio aprovechable, u ocultado activamente por el objetivo. |

## 10. Protección contra valores falsificados

Omega-deep no confía en ningún dato autodeclarado por el objetivo sin señalarlo explícitamente — y el descubrimiento de objetivos es la parte más sensible del proyecto: un objetivo malicioso *podría* anunciar un `X-Backend-Server` falso para orientar el descubrimiento hacia una IP de su elección. Dos protecciones estructurales, independientes entre sí:
- Ninguna información derivada de un objetivo es nunca `VERIFIED` por el mero hecho de anunciarse — un banner `Server` o una cabecera `X-Backend-Server` siguen siendo `DECLARED`, por plausibles que sean.
- La salvaguarda de perímetro ([§4](#4-descubrimiento-de-objetivos-y-salvaguardas)) limita adónde puede llevar un objetivo anunciado (mismo `/24` privado, salvo configuración explícita), y la validación del usuario limita si se escanea siquiera — un objetivo falso fuera del perímetro ni siquiera se propone; un objetivo dentro del perímetro sigue sujeto a confirmación explícita antes de cualquier escaneo.

## 11. Compatibilidad con terminales

La TUI (Textual) detecta automáticamente las capacidades del terminal (emulador, tamaño) y adapta en consecuencia su hoja de estilo estructural (`complete`/`standard`/`reduced`/`mono`), sin opción manual. El modo CLI siempre sigue en texto simple, independiente del terminal. Política compartida por toda la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Perfil según el emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH antiguo | `mono` |
| Emulador no reconocido | `reduced` (valor de reserva por defecto) |

### Perfil según el tamaño del terminal

| Tamaño mínimo (columnas × líneas) | Tope de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| por debajo | `mono` |

El perfil final es **el más restrictivo de los dos** (emulador y tamaño) — un Ghostty a pantalla completa redimensionado a 70 columnas baja a `mono`, aunque su emulador permitiría `complete`. Se puede actualizar en directo con la tecla `r`.

## 12. Exportaciones

Los informes de texto y HTML se escriben en el idioma elegido en Ajustes («Idioma de las exportaciones», por defecto el de la interfaz); el JSON sigue siendo un dato, sin traducir. Los informes se generan por defecto en `var/exports/` (ruta de ejecución anclada en la carpeta del proyecto, `$OMEGA_DEEP_VAR_DIR` para cambiarla), o en la ruta indicada (`--output` en CLI, cuadro de diálogo en la TUI). Nombre de archivo explícito y con fecha: `analyse-{perfil}-{fecha}.ext`, `analyse-custom-{fecha}.ext` para un perfil personal.

### JSON, fuente de verdad

Estructura completa del análisis (`Scan` + `Host[]` + `ArchitectureGraph`), estrictamente serializable en JSON, niveles de confianza incluidos.

### Texto, informe legible compacto

Legible fuera del terminal, sin códigos ANSI — grafo como lista de aristas.

### HTML, informe web autónomo

5 temas a elegir (`--theme` en CLI, selector en la TUI; sigue por defecto el tema activo de la interfaz cuando existe un equivalente). Maquetación propia: contenedor, cuadrícula de información, recuadros de estadísticas por estado de puerto, insignias de colores, **diagrama SVG del grafo de arquitectura** (ver [§8](#8-grafo-de-arquitectura)) — misma familia visual que `omega-scan`/`omega-check`.

## 13. Historial y comparación

Cada análisis se guarda (SQLite, `var/db/omega-deep.db`): un `scan_id` lleva el objetivo raíz **y** todos los hosts descubiertos/aceptados, además del grafo reconstruido. Historial consultable por objetivo raíz (con una columna dedicada al número de objetivos descubiertos), detalle de un análisis anterior (hosts + grafo), comparación entre dos análisis (estado de los puertos del **objetivo raíz** únicamente — comparar los grafos de descubrimiento sería una extensión posible, no necesaria por ahora) y repetición de un análisis sobre el mismo objetivo raíz sin volver a introducirlo.

## 14. Pruebas

```bash
source .venv/bin/activate
lint-imports        # comprueba la Dependency Rule
pytest -q           # 191 pruebas
ruff check src tests
mypy -p omega_deep
```

Estructura: `tests/unit/` (dominio y aplicación, sin E/S real), `tests/integration/` (SQLite/archivos reales, servidor HTTP ficticio `pytest-httpserver`, TLS mediante `trustme`), `tests/tui/` (navegación mediante `Pilot`, estructural — sin verificación visual autoproclamada).

## 15. Fuera de alcance

- Escaneo de CVE
- Detección activa de SQLi, XSS, RCE
- Identificación del sistema operativo
- Técnicas de escaneo de bajo nivel al estilo nmap (SYN scan, paquetes en bruto)
- Rastreo (crawling)
- Fuzzing
- Fuerza bruta
- Escanear un objetivo descubierto sin confirmación explícita — nunca, en ningún modo
- Descubrimiento fuera de la subred privada del objetivo inicial sin configuración explícita
- Panel web

---

> Omega-deep — Descubrir, cartografiar, calificar, informar.
> Una arquitectura reconstruida con una confianza explícita, nunca una suposición disfrazada de hecho.
