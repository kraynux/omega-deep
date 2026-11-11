<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licença MIT (ver o arquivo LICENSE) -->
<div align="center">
  <img src="../../assets/omega-deep.png" alt="Omega-Deep" width="384">
</div>

# 🖧 OMEGA-DEEP

**Análise de arquitetura com vários alvos (descoberta + salvaguardas + grafo)**

> Desenvolvido por [kraynux](https://github.com/kraynux) para [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Página oficial: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Capturas de tela: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface e relatórios exportados disponíveis em **17 idiomas** — veja [Idiomas da interface](#idiomas-da-interface).  
**Idiomas:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** faz tudo o que o `omega-check` faz em um alvo único (escaneamento de portas, identificação de serviços, papéis, WAF, TLS) e acrescenta a **descoberta de alvos adicionais** a partir dos indícios deixados pelo alvo já escaneado (cabeçalhos, redirecionamentos, certificado, links HTML), sob **salvaguardas rígidas** e uma **validação explícita do usuário** antes de escanear qualquer alvo descoberto, e depois **reconstrói um grafo de arquitetura** (quem fala com quem, com qual confiança). Ferramenta da suíte `omega-`, estruturada em Clean Architecture — veja `docs/ARCHITECTURE.md` para todos os detalhes técnicos.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pt-BR/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pt-BR/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pt-BR/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pt-BR/omega-deep/D.png" width="24%" />
</p>

## 1. Visão e escopo

O Omega-deep responde a uma pergunta que o omega-check não faz: *por trás deste IP, o que mais existe?* Um proxy reverso que anuncia seu backend, um certificado que cobre vários hosts, uma página que aponta para um serviço vizinho — indícios que o omega-deep segue, com cautela, nunca por conta própria.

### O que o Omega-deep faz

- Escaneia um alvo raiz exatamente como o omega-check (perfil do sistema ou perfil pessoal salvo).
- Descobre alvos candidatos a partir dos indícios deixados por cada host já escaneado: cabeçalhos HTTP (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), redirecionamento (`Location`), certificado TLS (SAN), links HTML — veja [§4](#4-descoberta-de-alvos-e-salvaguardas).
- **Nunca** escaneia um alvo descoberto sem validação explícita, alvo por alvo — o silêncio nunca é uma aceitação.
- Limita a descoberta com salvaguardas rígidas: profundidade máxima, número máximo de alvos adicionais, sub-rede permitida (por padrão, a mesma faixa privada da raiz).
- Reconstrói um **grafo de arquitetura** a partir da procedência de cada alvo aceito (`proxy_to`, `redirect_to`, `linked_to`), com um nível de confiança por relação — veja [§8](#8-grafo-de-arquitetura).
- Apresenta o resultado em TUI (Textual) ou em CLI scriptável, com as mesmas três exportações do omega-check (JSON, texto, HTML com 5 temas) — ali o grafo é um **diagrama desenhado de verdade** em HTML, não uma tabela.
- Atribui a cada informação coletada (serviço ou descoberta) um nível de confiança explícito — veja [§9](#9-política-de-confiança).
- Mantém um histórico persistente de análises, repetível e comparável ao longo do tempo.

### O que o Omega-deep não faz

- Varredura ativa de vulnerabilidades: nada de SQLi, XSS ou RCE.
- Varredura de CVE.
- Identificação do sistema operacional.
- Técnicas de varredura de baixo nível no estilo nmap (SYN scan, pacotes brutos) — apenas conexão TCP de aplicação.
- Ferramenta de força bruta ou de fuzzing.
- Escanear um alvo descoberto sem confirmação explícita do usuário — nunca, em nenhum modo.
- Descoberta além da sub-rede privada do alvo inicial, salvo configuração explícita (`--subnet`).
- Painel web.

## 2. Instalação

### Pré-requisitos

- Python 3.10+
- Conexão com a Internet, para as dependências

### Instalação

```bash
[ -d omega-deep ] && echo "ℹ️ Já extraído aqui, etapa ignorada." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Cria o ambiente virtual `.venv` se ele ainda não existir.
2. Instala as dependências (`vendor/omega-lib/` e depois `pip install -e .`; `pyproject.toml` continua sendo a única fonte de verdade).
3. Torna `omega-deep.sh` e `install.sh` executáveis.
4. Adiciona o alias `deep` a `~/.bashrc` e `~/.zshrc` (sem duplicar se já existir).

### Dependências

Declaradas em `pyproject.toml` (sem mais `requirements.txt`):
- `omega-lib`: biblioteca compartilhada da suíte (`ConfidenceLevel`, temas, detecção do terminal) — incluída em `vendor/omega-lib/`
- `textual`: interface TUI, temas, adaptação automática ao terminal
- `httpx`: sondas HTTP/HTTPS (serviço e descoberta)
- `cryptography`: leitura do certificado TLS negociado
- `jinja2`: templates para a exportação HTML
- Dependências de desenvolvimento (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Uso

### Modo interativo (TUI)

Recomendado para o uso diário — iniciado sem argumentos:

```bash
./omega-deep.sh
```
se você criou o alias, basta digitar `deep` no terminal:
```bash
deep
```

Percurso: tela de abertura (fecha com uma tecla ou um clique) → menu principal (Analisar / Perfis / Histórico / Configurações / Ajuda) → informar o alvo raiz, escolher o perfil e as salvaguardas de descoberta (profundidade máxima, número máximo de alvos, sub-rede permitida) → análise (indicador indeterminado e registro das operações de rede ao vivo) → a cada lote de alvos descobertos, uma tela de validação (uma linha por alvo, com origem/confiança/prova visíveis, alternância aceitar/recusar — nada marcado por padrão) → detalhe da análise (hosts, portas/serviços/papéis, grafo, exportação) → histórico/comparação/repetição e configurações a partir do menu principal. A adaptação ao terminal (cores, tamanho, degradação estrutural) é automática.

#### Atalhos de teclado

| Tecla | Ação |
|---|---|
| `↑` / `↓` | Navegar entre os itens de uma tela |
| `Tab` / `Shift+Tab` | Navegar entre os campos de um formulário |
| `Esc` | Voltar à tela anterior (confirmação de saída na tela inicial) |
| `t` | Próximo tema (aplicado na hora, sem confirmação) |
| `r` | Atualizar a detecção do terminal |
| `a` | Mostrar a ajuda |
| `q` | Sair (com confirmação) |

### Idiomas da interface

A interface está disponível em 17 idiomas: francês, inglês, espanhol, português (Brasil), italiano, alemão, holandês, polonês, russo, chinês simplificado, vietnamita, tailandês, indonésio, japonês, coreano, hindi e árabe. A escolha é feita em Configurações («Langue / Language») e vale após reiniciar a interface; a variável `OMEGA_DEEP_LANG` (por exemplo `OMEGA_DEEP_LANG=pt-BR ./omega-deep.sh`) força um idioma durante uma sessão. Iniciado pelo omega-suite, o omega-deep usa o idioma da suíte. Em um console de texto Linux (TTY), os idiomas de escrita não latina aparecem em inglês durante a sessão. A linha de comando continua em francês.

### Contato e suporte

A ajuda (tecla `a`) oferece uma tela **Contato e suporte**: *Pagar um café* (página PayPal do desenvolvedor), *Contatar o suporte* (endereço de e-mail e formulário de contato do site, exibidos em claro), *Declarar-me usuário (anônimo)* e *Verificar atualizações*. A declaração é voluntária, desativada por padrão e enviada uma única vez: serve apenas para contar os usuários e, se desejado, seu continente ou país (listas fechadas, nunca texto livre). Ela envia uma chave sorteada ao acaso, o nome do software (`omega-deep`) e sua versão; nunca um nome, um nome de máquina, uma configuração, um alvo ou um resultado. O endereço IP não é registrado nas declarações, mas, como em qualquer visita, passa pelos controles de segurança e pelo registro do servidor de recepção. Retirada a qualquer momento na mesma tela (*Não me declarar mais*). A verificação de atualizações apenas lê a lista de versões publicadas no site, e nunca sem um clique.

### Modo scriptável (CLI)

Qualquer subcomando ativa o modo CLI:

```bash
# Analisar um alvo (escaneamento raiz + descoberta de vários alvos)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Histórico (filtrável por alvo raiz)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Detalhe de uma análise (texto, JSON ou HTML) — 5 temas de exportação à escolha
./omega-deep.sh show <scan_id> --format html --theme omega-base --output relatorio.html

# Comparar duas análises (estado das portas do alvo raiz)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Perfis de portas pessoais
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "Meu perfil"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

Na CLI, os alvos descobertos são validados por uma pergunta interativa por alvo (`Scanner <cible> ? [o/N]`, em francês como o resto da linha de comando), com o detalhe da prova exibido antes de cada pergunta. `--auto-validate` aceita tudo sem revisão (**não recomendado**, um aviso é exibido); em um ambiente não interativo (sem TTY e sem `--auto-validate`), todo alvo descoberto é recusado por padrão em vez de ser escaneado sem confirmação.

### Formatos de alvo aceitos

```text
192.168.1.10                IPv4
example.org                 Nome de host
http://example.org          URL HTTP  (esquema removido antes da resolução)
https://example.org:8443    URL HTTPS com porta  (esquema e porta removidos)
```

O esquema e a porta, se houver, são removidos antes da resolução DNS (`domain/targets/validation.py::normalize_target_input`) — colar uma URL inteira funciona, só o host é mantido. Os alvos *descobertos* são normalizados da mesma forma, mas nunca são escaneados sem validação (veja [§4](#4-descoberta-de-alvos-e-salvaguardas)).

## 4. Descoberta de alvos e salvaguardas

### Fontes de indícios

| Fonte | Origem | Confiança |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | Cabeçalho `Location` de uma resposta HTTP | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) do certificado TLS negociado | `DECLARED` |
| `html_link` | Links (`<a href>`) servidos pela página | `INFERRED` |

Um valor `DECLARED` continua sendo uma autodeclaração do alvo (falsificável) — veja [§10](#10-proteção-contra-valores-falsificados). `html_link` é, de propósito, a fonte mais fraca: um simples link não declara nenhuma relação de infraestrutura.

### Salvaguardas (sempre ativas, nunca desativáveis)

- **Perímetro**: um alvo candidato deve ser um IP privado no mesmo `/24` do alvo raiz, salvo `--subnet` explícito (nesse caso só conta a pertença à sub-rede indicada, mesmo que ela cubra IPs públicos — é a configuração explícita que autoriza a exceção). Um nome de host não resolvido nunca é aceito por este filtro (resolvê-lo para verificar já seria uma ação de rede fora do alcance desta verificação).
- **Profundidade**: `--max-depth` (padrão 3) — A → B → C → D no máximo.
- **Número de alvos**: `--max-targets` (padrão 10) — em todas as profundidades.

### Validação (nunca um escaneamento sem confirmação)

Cada alvo proposto segue `PROPOSED → PRESENTED → ACCEPTED` ou `REJECTED`. A regra é **à prova de falhas**: todo alvo nunca aceito explicitamente (silêncio, tela fechada, interrupção, tempo esgotado, ausência de TTY) é tratado como recusado — nunca o contrário. Na TUI, uma tela dedicada lista os alvos de um lote com prova e confiança, alternância aceitar/recusar por linha, «aceitar tudo»/«recusar tudo» e recusa total por padrão com Esc. Na CLI, uma pergunta por alvo; `--auto-validate` (não recomendado) é a única forma de contornar a interatividade.

## 5. Perfis de escaneamento

| Perfil | Descrição | Fixado |
|---|---|---|
| `minimal` | Escaneamento ultrarrápido: SSH + HTTP + HTTPS (22, 80, 443) | sim |
| `classic` | Serviços clássicos de Internet/LAN | sim |
| `web` | Serviços web e alternativos | não |
| `db` | Bancos de dados e serviços de dados | não |
| `remote` | Acessos remotos — shell, área de trabalho, RustDesk | não |
| `mail` | Serviços de e-mail | não |
| `dns` | Serviços DNS | não |
| `iot` | Equipamentos IoT, câmeras, roteadores, automação residencial | não |
| `dev` | Ambientes de desenvolvimento/laboratório | não |
| `docker` | Docker, Swarm e serviços comuns em contêineres | não |
| `complet` | **Gerado na hora**: união ordenada e sem duplicatas de todos os perfis acima | não |
| *perfil pessoal* | Criado na tela **Perfis** (TUI) ou com `profile create` (CLI), listado junto aos perfis do sistema, com o prefixo `* ` na TUI | não |

O perfil se aplica ao alvo raiz **e** a cada alvo descoberto aceito — não há perfil diferente por host. Detalhe completo, regras de validação e gestão dos perfis pessoais: `docs/PROFILES.md`.

## 6. Arquitetura

O Omega-deep é estruturado em **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), alinhada ao modelo da suíte `omega-` (veja `omega-scan`/`omega-check`) e verificada pelo `import-linter` a cada alteração. Todos os detalhes estão em **`docs/ARCHITECTURE.md`**.

Visão geral bem curta:

```text
src/omega_deep/
├── domain/          Lógica de negócio pura: escaneamentos, alvos, serviços, perfis, relatórios,
│                    discovery (alvos propostos, máquina de estados de validação),
│                    architecture (grafo, regras de relação)
├── application/     Casos de uso (commands/queries) — entre eles discover_targets,
│                    validate_targets, reconstruct_architecture (novos em relação ao omega-check)
├── ports/           Contratos esperados pela aplicação (sondas, entre elas discovery_prober,
│                    repositórios, exportadores...)
├── infrastructure/  Implementações concretas (socket/httpx/cryptography, SQLite,
│                    renderização SVG do grafo — o Textual NÃO está aqui)
├── interfaces/      tui/ (Textual) e cli/ (scriptável), com paridade funcional estrita
├── app/             Montagem (DependencyContainer, bootstrap, ciclo de vida)
├── core/, shared/   Vocabulário transversal, utilitários fora do negócio
└── plugins/         Estrutura pronta, vazia (nenhum eixo de extensão confirmado)
```

Regras de design:
- `domain/services/policies.py`: classifica os indícios já coletados, nunca faz rede.
- `domain/discovery/policies.py`: salvaguardas de perímetro/profundidade/número — lógica pura, testável sem rede.
- `domain/architecture/service.py`: reconstrói o grafo a partir da procedência já trazida por cada `Host`, não refaz nenhuma requisição.
- `infrastructure/network/` e `infrastructure/discovery/`: fazem rede (sockets, `httpx`, `cryptography`), nunca julgam.
- `interfaces/`: exibe, não contém nenhuma lógica de negócio — a tela de validação dos alvos descobertos chama `validate_targets`, não implementa ela mesma a regra à prova de falhas.
- `infrastructure/exporters/`: leem o resultado da análise (escaneamento, hosts, grafo), não recalculam nada.

## 7. Identificação de serviços e papéis

### Protocolos detectados

| Protocolo | Sonda | Detalhe coletado |
|---|---|---|
| HTTP / HTTPS | `httpx` | Banner `Server`, cabeçalhos de autenticação |
| TLS | `cryptography` (certificado negociado, `CERT_NONE` incluído) | Versão, cifra, sujeito/emissor do certificado |
| SSH | Banner bruto | Software e versão (ex. `OpenSSH 10.4`) |
| VNC (RFB) | Códigos de segurança anunciados pelo servidor | Tipos de autenticação suportados |
| Genérico | Banner bruto em porta aberta não reconhecida | Extração cautelosa, sem heurística agressiva |

### Papéis inferidos

Deduzidos do protocolo **realmente negociado**, nunca de uma suposição pelo número da porta:

| Papel | Condição | Confiança |
|---|---|---|
| `servidor web` | Protocolo HTTP/HTTPS confirmado | `INFERRED` |
| `acesso shell` | Protocolo SSH confirmado | `CORROBORATED` |
| `acesso gráfico` | Protocolo VNC confirmado | `CORROBORATED` |
| `banco de dados` | Porta dentro da faixa do perfil do sistema `db` | `INFERRED` |

### Assinaturas WAF conhecidas

Detectadas por meio de um cabeçalho declarativo (`server`, `x-sdk`) — presença **declarada pelo alvo**, nunca verificada de forma independente: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (listado a título indicativo, não é propriamente um WAF de aplicação).

## 8. Grafo de arquitetura

Reconstruído apenas a partir da procedência já trazida por cada host aceito (`discovered_from`/`discovery_source`/`discovery_confidence`) — nenhuma nova requisição de rede, nenhuma reanálise dos indícios brutos.

### Relações produzidas

| Relação | Fonte de descoberta | Significado |
|---|---|---|
| `proxy_to` | `header` | O alvo raiz (ou um host já aceito) provavelmente é um proxy para o alvo descoberto |
| `redirect_to` | `redirection` | Redirecionamento HTTP observado para o alvo descoberto |
| `linked_to` | `certificate` ou `html_link` | A relação mais neutra — infraestrutura/aplicação compartilhada, sem afirmar direção de fluxo |

`backend_of` (a aresta inversa de um `proxy_to`) não é produzido de propósito — seria informação duplicada, não uma nova dedução.

### Renderização

- **TUI** (detalhe de uma análise) e **exportações JSON/texto**: lista de arestas (origem, relação, destino, confiança) — um terminal não é o lugar para uma renderização gráfica rica.
- **Exportação HTML**: um **diagrama SVG de verdade** (nós = círculos, arestas = setas com rótulo), layout em camadas calculado a partir do alvo raiz, tamanho proporcional ao número de máquinas descobertas — nunca uma dependência pesada de layout de grafos; o grafo permanece pequeno por construção (limitado pelas salvaguardas do [§4](#4-descoberta-de-alvos-e-salvaguardas)).

## 9. Política de confiança

Cada campo coletado traz um destes níveis:

| Nível | Significado |
|---|---|
| `VERIFIED` | Fato de protocolo observado diretamente, que o alvo não pode falsificar (ex.: porta fechada confirmada por um RST TCP, versão TLS realmente negociada). |
| `DECLARED` | Valor autoanunciado pelo alvo em um campo que ele controla totalmente (ex.: banner `Server`, cabeçalho `X-Backend-Server`) — plausível, mas falsificável à vontade. |
| `CORROBORATED` | Um valor `DECLARED` confirmado por um indício independente (ex.: papel SSH, já que o protocolo foi de fato negociado). |
| `INFERRED` | Deduzido de um padrão/heurística, sem declaração explícita do alvo (ex.: link HTML). |
| `UNKNOWN` | Nenhum indício utilizável, ou ocultado ativamente pelo alvo. |

## 10. Proteção contra valores falsificados

O Omega-deep não confia em nenhum dado autodeclarado pelo alvo sem sinalizá-lo explicitamente — e a descoberta de alvos é a parte mais sensível do projeto: um alvo malicioso *poderia* anunciar um `X-Backend-Server` mentiroso para direcionar a descoberta para um IP de sua escolha. Duas proteções estruturais, independentes uma da outra:
- Nenhuma informação derivada de um alvo é jamais `VERIFIED` pelo simples fato de ser anunciada — um banner `Server` ou um cabeçalho `X-Backend-Server` continua `DECLARED`, por mais plausível que seja.
- A salvaguarda de perímetro ([§4](#4-descoberta-de-alvos-e-salvaguardas)) limita para onde um alvo anunciado pode levar (mesmo `/24` privado, salvo configuração explícita), e a validação do usuário limita se ele é sequer escaneado — um alvo mentiroso fora do perímetro nem chega a ser proposto; um alvo dentro do perímetro continua sujeito a confirmação explícita antes de qualquer escaneamento.

## 11. Compatibilidade com terminais

A TUI (Textual) detecta automaticamente as capacidades do terminal (emulador, tamanho) e adapta sua folha de estilo estrutural de acordo (`complete`/`standard`/`reduced`/`mono`), sem opção manual. O modo CLI continua sempre em texto simples, independente do terminal. Política compartilhada por toda a suíte `omega-` (`omega-lib`, `terminal/policies.py`).

### Perfil conforme o emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH antigo | `mono` |
| Emulador não reconhecido | `reduced` (alternativa padrão) |

### Perfil conforme o tamanho do terminal

| Tamanho mínimo (colunas × linhas) | Teto de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| abaixo | `mono` |

O perfil final é **o mais restritivo dos dois** (emulador e tamanho) — um Ghostty em tela cheia redimensionado para 70 colunas desce para `mono`, mesmo que seu emulador permitisse `complete`. Atualizável ao vivo com a tecla `r`.

## 12. Exportações

Os relatórios de texto e HTML são escritos no idioma escolhido em Configurações («Idioma das exportações», por padrão o da interface); o JSON continua sendo um dado, não traduzido. Os relatórios são gerados em `var/exports/` por padrão (caminho de execução ancorado na pasta do projeto, `$OMEGA_DEEP_VAR_DIR` para alterá-lo), ou no caminho indicado (`--output` na CLI, caixa de diálogo na TUI). Nome de arquivo explícito e com data: `analyse-{perfil}-{data}.ext`, `analyse-custom-{data}.ext` para um perfil pessoal.

### JSON, fonte de verdade

Estrutura completa da análise (`Scan` + `Host[]` + `ArchitectureGraph`), estritamente serializável em JSON, níveis de confiança incluídos.

### Texto, relatório legível compacto

Legível fora do terminal, sem códigos ANSI — grafo como lista de arestas.

### HTML, relatório web autônomo

5 temas à escolha (`--theme` na CLI, seletor na TUI; segue por padrão o tema ativo da interface quando existe um equivalente). Layout próprio: contêiner, grade de informações, quadros de estatísticas por estado de porta, selos coloridos, **diagrama SVG do grafo de arquitetura** (veja [§8](#8-grafo-de-arquitetura)) — mesma família visual de `omega-scan`/`omega-check`.

## 13. Histórico e comparação

Cada análise é salva (SQLite, `var/db/omega-deep.db`): um `scan_id` traz o alvo raiz **e** todos os hosts descobertos/aceitos, além do grafo reconstruído. Histórico consultável por alvo raiz (com uma coluna dedicada ao número de alvos descobertos), detalhe de uma análise anterior (hosts + grafo), comparação entre duas análises (estado das portas do **alvo raiz** apenas — comparar os grafos de descoberta seria uma extensão possível, não necessária por enquanto) e repetição de uma análise no mesmo alvo raiz sem redigitá-lo.

## 14. Testes

```bash
source .venv/bin/activate
lint-imports        # verifica a Dependency Rule
pytest -q           # 191 testes
ruff check src tests
mypy -p omega_deep
```

Estrutura: `tests/unit/` (domínio e aplicação, sem E/S real), `tests/integration/` (SQLite/arquivos reais, servidor HTTP falso `pytest-httpserver`, TLS via `trustme`), `tests/tui/` (navegação via `Pilot`, estrutural — sem verificação visual autodeclarada).

## 15. Fora do escopo

- Varredura de CVE
- Detecção ativa de SQLi, XSS, RCE
- Identificação do sistema operacional
- Técnicas de varredura de baixo nível no estilo nmap (SYN scan, pacotes brutos)
- Rastreamento (crawling)
- Fuzzing
- Força bruta
- Escanear um alvo descoberto sem confirmação explícita — nunca, em nenhum modo
- Descoberta fora da sub-rede privada do alvo inicial sem configuração explícita
- Painel web

---

> Omega-deep — Descobrir, mapear, qualificar, relatar.
> Uma arquitetura reconstruída com confiança explícita, nunca uma suposição disfarçada de fato.
