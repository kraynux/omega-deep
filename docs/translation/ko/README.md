<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 라이선스 (LICENSE 파일 참조) -->
<div align="center">
  <img src="../../assets/omega-deep.png" alt="Omega-Deep" width="384">
</div>

# 🖧 OMEGA-DEEP

**다중 대상 아키텍처 분석 (발견 + 안전 제한 + 그래프)**

> [Omega-Server](https://kraynux.snake-mackarel.ts.net)를 위해 [kraynux](https://github.com/kraynux)가 개발   

공식 페이지: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; 미리보기: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 인터페이스와 내보낸 보고서는 **17개 언어**로 제공됩니다 — [인터페이스 언어](#인터페이스-언어) 참조.  
**언어:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep**은 `omega-check`가 단일 대상에서 하는 모든 일(포트 스캔, 서비스 식별, 역할, WAF, TLS)을 그대로 하면서, 이미 스캔한 대상이 남긴 단서(헤더, 리디렉션, 인증서, HTML 링크)로부터 **추가 대상을 발견**합니다. 이 과정은 **엄격한 안전 제한** 아래에서 이루어지며, 발견된 대상을 스캔하기 전에는 반드시 **사용자의 명시적 승인**을 받습니다. 그런 다음 **아키텍처 그래프를 재구성**합니다(누가 누구와 통신하는지, 어떤 신뢰도로). `omega-` 제품군의 도구이며 Clean Architecture로 구성되어 있습니다 — 기술적인 세부 사항은 모두 `docs/ARCHITECTURE.md`를 참조하세요.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ko/omega-deep/D.png" width="24%" />
</p>

## 1. 비전과 범위

Omega-deep은 omega-check가 던지지 않는 질문에 답합니다: *이 IP 뒤에는 또 무엇이 있는가?* 자신의 백엔드를 알리는 리버스 프록시, 여러 호스트를 포괄하는 인증서, 이웃 서비스를 가리키는 페이지 — 모두 omega-deep이 신중하게 따라가는 단서이며, 결코 혼자 판단해 움직이지 않습니다.

### Omega-deep이 하는 일

- 루트 대상을 omega-check와 똑같이 스캔합니다(시스템 프로필 또는 저장된 개인 프로필).
- 이미 스캔한 각 호스트가 남긴 단서로 후보 대상을 발견합니다: HTTP 헤더(`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), 리디렉션(`Location`), TLS 인증서(SAN), HTML 링크 — [§4](#4-대상-발견과-안전-제한) 참조.
- 발견된 대상을 대상별 명시적 승인 없이 **절대** 스캔하지 않습니다 — 침묵은 결코 동의가 아닙니다.
- 엄격한 안전 제한으로 발견 범위를 묶습니다: 최대 깊이, 추가 대상의 최대 수, 허용 서브넷(기본값은 루트와 같은 사설 대역).
- 승인된 각 대상의 출처(`proxy_to`, `redirect_to`, `linked_to`)로 **아키텍처 그래프**를 재구성하며, 관계마다 신뢰 수준을 붙입니다 — [§8](#8-아키텍처-그래프) 참조.
- 결과를 TUI(Textual) 또는 스크립트용 CLI로 보여 주며, omega-check와 같은 세 가지 내보내기(JSON, 텍스트, 5가지 테마의 HTML)를 제공합니다 — HTML에서 그래프는 표가 아니라 **실제로 그려진 다이어그램**입니다.
- 수집한 모든 정보(서비스든 발견이든)에 명시적인 신뢰 수준을 붙입니다 — [§9](#9-신뢰-정책) 참조.
- 분석 기록을 영구 보관하며, 다시 실행하고 시간에 따라 비교할 수 있습니다.

### Omega-deep이 하지 않는 일

- 능동적 취약점 스캔: SQLi, XSS, RCE 없음.
- CVE 스캔.
- 운영 체제 핑거프린팅.
- nmap 방식의 저수준 스캔 기법(SYN 스캔, 원시 패킷) — 애플리케이션 수준의 TCP 연결만 사용합니다.
- 무차별 대입이나 퍼징 도구.
- 사용자의 명시적 승인 없이 발견된 대상을 스캔하는 일 — 어떤 모드에서도 절대 하지 않습니다.
- 명시적으로 설정하지 않는 한(`--subnet`) 최초 대상의 사설 서브넷을 넘어서는 발견.
- 웹 대시보드.

## 2. 설치

### 요구 사항

- Python 3.10+
- 의존성을 위한 인터넷 연결

### 설치

```bash
[ -d omega-deep ] && echo "ℹ️ 이미 여기에 압축이 풀려 있어 이 단계를 건너뜁니다." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. 가상 환경 `.venv`가 아직 없으면 만듭니다.
2. 의존성을 설치합니다(`vendor/omega-lib/` 다음 `pip install -e .`; `pyproject.toml`이 유일한 기준 정보로 남습니다).
3. `omega-deep.sh`와 `install.sh`를 실행 가능하게 만듭니다.
4. 별칭 `deep`을 `~/.bashrc`와 `~/.zshrc`에 추가합니다(이미 있으면 중복하지 않습니다).

### 의존성

`pyproject.toml`에 선언(`requirements.txt`는 더 이상 없음):
- `omega-lib`: 제품군 공용 라이브러리(`ConfidenceLevel`, 테마, 터미널 감지) — `vendor/omega-lib/`에 포함
- `textual`: TUI 인터페이스, 테마, 터미널 자동 적응
- `httpx`: HTTP/HTTPS 프로브(서비스와 발견)
- `cryptography`: 협상된 TLS 인증서 읽기
- `jinja2`: HTML 내보내기용 템플릿
- 개발 의존성(`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. 사용법

### 대화형 모드 (TUI)

일상적인 사용에 권장 — 인수 없이 실행합니다:

```bash
./omega-deep.sh
```
별칭을 만들었다면 터미널에 `deep`만 입력하면 됩니다:
```bash
deep
```

흐름: 시작 화면(키를 누르거나 클릭하면 닫힘) → 메인 메뉴(분석 / 프로필 / 기록 / 설정 / 도움말) → 루트 대상 입력, 프로필과 발견 안전 제한(최대 깊이, 최대 대상 수, 허용 서브넷) 선택 → 분석(불확정 진행 표시와 실시간 네트워크 작업 로그) → 발견된 대상 묶음마다 승인 화면(대상당 한 줄, 출처/신뢰도/근거 표시, 승인/거부 전환 — 기본값은 아무것도 선택되지 않음) → 분석 상세(호스트, 포트/서비스/역할, 그래프, 내보내기) → 메인 메뉴에서 기록/비교/다시 실행과 설정. 터미널에 대한 적응(색상, 크기, 구조 단순화)은 자동입니다.

#### 단축키

| 키 | 동작 |
|---|---|
| `↑` / `↓` | 화면의 항목 사이 이동 |
| `Tab` / `Shift+Tab` | 양식의 필드 사이 이동 |
| `Esc` | 이전 화면으로 돌아가기(홈 화면에서는 종료 확인) |
| `t` | 다음 테마(확인 없이 즉시 적용) |
| `r` | 터미널 감지 새로 고침 |
| `a` | 도움말 표시 |
| `q` | 종료(확인 후) |

### 인터페이스 언어

인터페이스는 17개 언어로 제공됩니다: 프랑스어, 영어, 스페인어, 포르투갈어(브라질), 이탈리아어, 독일어, 네덜란드어, 폴란드어, 러시아어, 중국어 간체, 베트남어, 태국어, 인도네시아어, 일본어, 한국어, 힌디어, 아랍어. 설정(“Langue / Language”)에서 선택하며 인터페이스를 다시 시작한 뒤 적용됩니다. 변수 `OMEGA_DEEP_LANG`(예: `OMEGA_DEEP_LANG=ko ./omega-deep.sh`)으로 한 세션 동안 언어를 강제할 수 있습니다. omega-suite에서 실행하면 omega-deep은 제품군의 언어를 사용합니다. Linux 텍스트 콘솔(TTY)에서는 라틴 문자가 아닌 언어가 해당 세션 동안 영어로 표시됩니다. 명령줄은 프랑스어로 유지됩니다.

### 문의 및 지원

도움말(`a` 키)에는 **문의 및 지원** 화면이 있습니다: *커피 한 잔 사기*(개발자의 PayPal 페이지), *지원팀에 문의*(이메일 주소와 사이트의 문의 양식을 그대로 표시), *사용자로 등록(익명)*, *업데이트 확인*. 등록은 자발적이며 기본적으로 꺼져 있고 한 번만 전송됩니다. 사용자 수와, 원하면 사용자의 대륙 또는 국가(닫힌 목록, 자유 입력 없음)를 세는 데에만 쓰입니다. 무작위로 생성한 키, 소프트웨어 이름(`omega-deep`)과 버전만 보내며, 이름, 컴퓨터 이름, 설정, 대상, 결과는 절대 보내지 않습니다. IP 주소는 등록 정보에 저장되지 않지만, 모든 방문과 마찬가지로 수신 서버의 보안 검사와 로그를 거칩니다. 같은 화면에서 언제든지 철회할 수 있습니다(*등록 취소*). 업데이트 확인은 사이트에 게시된 버전 목록만 읽으며, 클릭하지 않으면 절대 실행되지 않습니다.

### 스크립트 모드 (CLI)

하위 명령을 지정하면 CLI 모드가 됩니다:

```bash
# 대상 분석(루트 스캔 + 다중 대상 발견)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# 기록(루트 대상별 필터 가능)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# 분석 상세(텍스트, JSON 또는 HTML) — 내보내기 테마 5가지 중 선택
./omega-deep.sh show <scan_id> --format html --theme omega-base --output report.html

# 두 분석 비교(루트 대상의 포트 상태)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# 개인 포트 프로필
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "내 프로필"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

CLI에서는 발견된 대상을 대상별 대화형 질문으로 승인합니다(`Scanner <cible> ? [o/N]`, 명령줄의 나머지와 마찬가지로 프랑스어). 질문마다 그 전에 근거의 세부 내용이 표시됩니다. `--auto-validate`는 검토 없이 모두 승인합니다(**권장하지 않음**, 경고가 표시됨). 비대화형 환경(TTY가 없고 `--auto-validate`도 없음)에서는 발견된 대상이 승인 없이 스캔되는 대신 기본적으로 모두 거부됩니다.

### 허용되는 대상 형식

```text
192.168.1.10                IPv4
example.org                 호스트 이름
http://example.org          HTTP URL  (이름 해석 전에 스킴 제거)
https://example.org:8443    포트가 있는 HTTPS URL  (스킴과 포트 제거)
```

스킴과 포트가 있으면 DNS 해석 전에 제거됩니다(`domain/targets/validation.py::normalize_target_input`) — URL 전체를 붙여 넣어도 동작하며, 호스트만 남습니다. *발견된* 대상도 같은 방식으로 정규화되지만, 승인 없이 스캔되는 일은 결코 없습니다([§4](#4-대상-발견과-안전-제한) 참조).

## 4. 대상 발견과 안전 제한

### 단서의 출처

| 출처 | 원천 | 신뢰도 |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | HTTP 응답의 `Location` 헤더 | `DECLARED` |
| `certificate` | 협상된 TLS 인증서의 SAN(Subject Alternative Names) | `DECLARED` |
| `html_link` | 페이지가 제공하는 링크(`<a href>`) | `INFERRED` |

`DECLARED` 값은 여전히 대상의 자기 신고일 뿐입니다(위조 가능) — [§10](#10-위조된-값에-대한-보호) 참조. `html_link`는 의도적으로 가장 약한 출처로 두었습니다: 단순한 링크는 어떤 인프라 관계도 선언하지 않기 때문입니다.

### 안전 제한(항상 켜져 있고 끌 수 없음)

- **범위**: 후보 대상은 루트 대상과 같은 `/24` 안의 사설 IP여야 합니다. 단, `--subnet`을 명시하면 지정한 서브넷에 속하는지만 따집니다(공인 IP를 포함하더라도 — 예외를 허용하는 것은 명시적인 설정 자체입니다). 해석되지 않은 호스트 이름은 이 필터를 결코 통과하지 못합니다(확인하려고 이름을 해석하는 것 자체가 이미 이 확인의 범위를 넘는 네트워크 작업이기 때문입니다).
- **깊이**: `--max-depth`(기본값 3) — 최대 A → B → C → D.
- **대상 수**: `--max-targets`(기본값 10) — 모든 깊이를 합산.

### 승인(승인 없이는 절대 스캔하지 않음)

제안된 각 대상은 `PROPOSED → PRESENTED → ACCEPTED` 또는 `REJECTED`를 거칩니다. 규칙은 **페일세이프**입니다: 한 번도 명시적으로 승인되지 않은 대상(침묵, 화면 닫기, 중단, 시간 초과, TTY 없음)은 모두 거부로 처리되며, 그 반대는 결코 없습니다. TUI에서는 전용 화면이 묶음의 대상을 근거와 신뢰도와 함께 나열하고, 줄마다 승인/거부 전환, “모두 승인”/“모두 거부”를 제공하며, Esc를 누르면 기본적으로 모두 거부합니다. CLI에서는 대상마다 질문 하나이며, `--auto-validate`(권장하지 않음)가 대화형 절차를 건너뛰는 유일한 방법입니다.

## 5. 스캔 프로필

| 프로필 | 설명 | 고정 |
|---|---|---|
| `minimal` | 초고속 스캔: SSH + HTTP + HTTPS (22, 80, 443) | 예 |
| `classic` | 일반적인 인터넷/LAN 서비스 | 예 |
| `web` | 웹 서비스와 대체 포트 | 아니요 |
| `db` | 데이터베이스와 데이터 서비스 | 아니요 |
| `remote` | 원격 접근 — 셸, 데스크톱, RustDesk | 아니요 |
| `mail` | 메일 서비스 | 아니요 |
| `dns` | DNS 서비스 | 아니요 |
| `iot` | IoT 장비, 카메라, 공유기, 홈 오토메이션 | 아니요 |
| `dev` | 개발/실험 환경 | 아니요 |
| `docker` | Docker, Swarm, 컨테이너에서 흔히 쓰는 서비스 | 아니요 |
| `complet` | **즉석 생성**: 위의 모든 프로필을 정렬하고 중복을 제거한 합집합 | 아니요 |
| *개인 프로필* | **프로필** 화면(TUI)이나 `profile create`(CLI)로 만들며, 시스템 프로필과 같은 곳에 표시되고 TUI에서는 앞에 `* `가 붙습니다 | 아니요 |

프로필은 루트 대상**과** 승인된 각 발견 대상에 적용됩니다 — 호스트마다 다른 프로필을 쓰지 않습니다. 전체 세부 사항, 검증 규칙, 개인 프로필 관리: `docs/PROFILES.md`.

## 6. 아키텍처

Omega-deep은 **Clean Architecture**(domain / application / infrastructure / interfaces / ports / core / app / plugins / shared)로 구성되어 있으며, `omega-` 제품군의 템플릿(`omega-scan`/`omega-check` 참조)에 맞추고 변경할 때마다 `import-linter`로 검증합니다. 전체 세부 사항은 **`docs/ARCHITECTURE.md`**에 있습니다.

아주 짧은 개요:

```text
src/omega_deep/
├── domain/          순수 업무 로직: 스캔, 대상, 서비스, 프로필, 보고서,
│                    discovery(제안된 대상, 승인 상태 기계),
│                    architecture(그래프, 관계 규칙)
├── application/     사용 사례(commands/queries) — discover_targets,
│                    validate_targets, reconstruct_architecture 포함(omega-check 대비 신규)
├── ports/           애플리케이션이 기대하는 계약(프로브, discovery_prober 포함,
│                    저장소, 내보내기 도구...)
├── infrastructure/  구체 구현(socket/httpx/cryptography, SQLite,
│                    그래프의 SVG 렌더링 — Textual은 여기에 없음)
├── interfaces/      tui/(Textual)와 cli/(스크립트용), 기능이 엄격히 동일
├── app/             조립(DependencyContainer, bootstrap, 수명 주기)
├── core/, shared/   공통 어휘, 업무 외 유틸리티
└── plugins/         구조만 마련됨, 비어 있음(확정된 확장 방향 없음)
```

설계 규칙:
- `domain/services/policies.py`: 이미 수집된 단서를 분류하며 네트워크에는 접근하지 않습니다.
- `domain/discovery/policies.py`: 범위/깊이/개수 안전 제한 — 네트워크 없이 테스트할 수 있는 순수 로직.
- `domain/architecture/service.py`: 각 `Host`가 이미 지닌 출처로 그래프를 재구성하며, 새 요청은 하지 않습니다.
- `infrastructure/network/`와 `infrastructure/discovery/`: 네트워크에 접근하며(소켓, `httpx`, `cryptography`) 판단하지 않습니다.
- `interfaces/`: 표시만 하며 업무 로직을 담지 않습니다 — 발견 대상 승인 화면은 `validate_targets`를 호출할 뿐, 페일세이프 규칙을 직접 구현하지 않습니다.
- `infrastructure/exporters/`: 분석 결과(스캔, 호스트, 그래프)를 읽기만 하며 아무것도 다시 계산하지 않습니다.

## 7. 서비스 식별과 역할

### 탐지하는 프로토콜

| 프로토콜 | 프로브 | 수집하는 세부 정보 |
|---|---|---|
| HTTP / HTTPS | `httpx` | `Server` 배너, 인증 헤더 |
| TLS | `cryptography`(협상된 인증서, `CERT_NONE` 포함) | 버전, 암호 스위트, 인증서 주체/발급자 |
| SSH | 원시 배너 | 소프트웨어와 버전(예: `OpenSSH 10.4`) |
| VNC (RFB) | 서버가 알리는 보안 코드 | 지원하는 인증 유형 |
| 일반 | 인식하지 못한 열린 포트의 원시 배너 | 신중한 추출, 공격적인 휴리스틱 없음 |

### 추정하는 역할

포트 번호에 대한 짐작이 아니라 **실제로 협상된** 프로토콜에서 도출합니다:

| 역할 | 조건 | 신뢰도 |
|---|---|---|
| `웹 서버` | HTTP/HTTPS 프로토콜 확인 | `INFERRED` |
| `셸 접근` | SSH 프로토콜 확인 | `CORROBORATED` |
| `그래픽 접근` | VNC 프로토콜 확인 | `CORROBORATED` |
| `데이터베이스` | 포트가 시스템 프로필 `db` 범위 안에 있음 | `INFERRED` |

### 알려진 WAF 시그니처

선언적 헤더(`server`, `x-sdk`)를 통해 탐지합니다 — 존재 여부는 **대상이 스스로 선언한 것**이며 독립적으로 검증하지 않습니다: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB(참고용으로 기재, 엄밀히는 애플리케이션 WAF가 아님).

## 8. 아키텍처 그래프

승인된 각 호스트가 이미 지닌 출처(`discovered_from`/`discovery_source`/`discovery_confidence`)만으로 재구성합니다 — 새로운 네트워크 요청도, 원시 단서의 재분석도 없습니다.

### 생성되는 관계

| 관계 | 발견 출처 | 의미 |
|---|---|---|
| `proxy_to` | `header` | 루트 대상(또는 이미 승인된 호스트)이 발견된 대상으로 가는 프록시일 가능성이 높음 |
| `redirect_to` | `redirection` | 발견된 대상으로의 HTTP 리디렉션이 관찰됨 |
| `linked_to` | `certificate` 또는 `html_link` | 가장 중립적인 관계 — 공유 인프라/애플리케이션, 흐름 방향은 단정하지 않음 |

`backend_of`(`proxy_to`의 역방향 간선)는 의도적으로 만들지 않습니다 — 새로운 추론이 아니라 중복된 정보이기 때문입니다.

### 표시 방식

- **TUI**(분석 상세)와 **JSON/텍스트 내보내기**: 간선 목록(출처, 관계, 대상, 신뢰도) — 터미널은 풍부한 그래픽 표현을 위한 곳이 아닙니다.
- **HTML 내보내기**: **진짜 SVG 다이어그램**(노드 = 원, 간선 = 레이블이 붙은 화살표), 루트 대상에서부터 계산한 계층형 배치, 크기는 발견된 머신 수에 비례 — 무거운 그래프 배치 라이브러리에 의존하지 않으며, 그래프는 설계상 항상 작게 유지됩니다([§4](#4-대상-발견과-안전-제한)의 안전 제한으로 묶이기 때문).

## 9. 신뢰 정책

수집된 각 필드에는 다음 수준 중 하나가 붙습니다:

| 수준 | 의미 |
|---|---|
| `VERIFIED` | 직접 관찰한 프로토콜상의 사실로, 대상이 위조할 수 없습니다(예: TCP RST로 확인한 닫힌 포트, 실제로 협상된 TLS 버전). |
| `DECLARED` | 대상이 완전히 통제하는 필드에서 스스로 알린 값(예: `Server` 배너, `X-Backend-Server` 헤더) — 그럴듯하지만 마음대로 위조할 수 있습니다. |
| `CORROBORATED` | 독립적인 단서로 확인된 `DECLARED` 값(예: SSH 역할, 프로토콜이 실제로 협상되었으므로). |
| `INFERRED` | 대상의 명시적 선언 없이 패턴/휴리스틱으로 추정한 값(예: HTML 링크). |
| `UNKNOWN` | 쓸 만한 단서가 없거나 대상이 의도적으로 숨긴 경우. |

## 10. 위조된 값에 대한 보호

Omega-deep은 대상이 스스로 선언한 데이터를 명시적으로 표시하지 않고는 신뢰하지 않습니다 — 그리고 대상 발견은 이 프로젝트에서 가장 민감한 부분입니다: 악의적인 대상은 거짓 `X-Backend-Server`를 알려 발견 과정을 자신이 고른 IP로 유도*할 수 있기* 때문입니다. 서로 독립적인 두 가지 구조적 보호 장치가 있습니다:
- 대상에서 비롯된 어떤 정보도 단지 알려졌다는 이유만으로 `VERIFIED`가 되지 않습니다 — `Server` 배너나 `X-Backend-Server` 헤더는 아무리 그럴듯해도 `DECLARED`로 남습니다.
- 범위 제한([§4](#4-대상-발견과-안전-제한))은 알려진 대상이 어디까지 이끌 수 있는지를 묶고(명시적 설정이 없으면 같은 사설 `/24`), 사용자 승인은 애초에 스캔할지 말지를 결정합니다 — 범위 밖의 거짓 대상은 제안조차 되지 않으며, 범위 안의 대상도 스캔 전에는 반드시 명시적 승인을 거쳐야 합니다.

## 11. 터미널 호환성

TUI(Textual)는 터미널의 능력(에뮬레이터, 크기)을 자동으로 감지하고 그에 맞게 구조 스타일시트(`complete`/`standard`/`reduced`/`mono`)를 조정합니다. 수동 옵션은 필요 없습니다. CLI 모드는 항상 일반 텍스트이며 터미널과 무관합니다. 이 정책은 `omega-` 제품군 전체가 공유합니다(`omega-lib`, `terminal/policies.py`).

### 감지된 에뮬레이터에 따른 프로필

| 에뮬레이터 | 초기 프로필 |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, 최신 SSH | `reduced` |
| Linux TTY, 구형 SSH | `mono` |
| 인식할 수 없는 에뮬레이터 | `reduced`(기본 대체값) |

### 터미널 크기에 따른 프로필

| 최소 크기(열 × 행) | 프로필 상한 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 그보다 작음 | `mono` |

최종 프로필은 **둘 중 더 엄격한 쪽**(에뮬레이터와 크기)입니다 — 전체 화면의 Ghostty를 70열로 줄이면, 에뮬레이터가 `complete`를 허용하더라도 `mono`로 내려갑니다. `r` 키로 바로 새로 고칠 수 있습니다.

## 12. 내보내기

텍스트와 HTML 보고서는 설정에서 고른 언어로 작성됩니다(“내보내기 언어”, 기본값은 인터페이스와 같음). JSON은 데이터로 남으며 번역되지 않습니다. 보고서는 기본적으로 `var/exports/`에 생성되며(실행 경로는 프로젝트 폴더에 고정, `$OMEGA_DEEP_VAR_DIR`로 변경 가능), 지정한 경로(CLI에서는 `--output`, TUI에서는 대화 상자)에 생성할 수도 있습니다. 명확하고 시각이 들어간 파일 이름: `analyse-{프로필}-{날짜}.ext`, 개인 프로필은 `analyse-custom-{날짜}.ext`.

### JSON, 기준 정보

분석의 전체 구조(`Scan` + `Host[]` + `ArchitectureGraph`), 엄격하게 JSON 직렬화 가능하며 신뢰 수준도 포함합니다.

### 텍스트, 간결하고 읽기 쉬운 보고서

터미널 밖에서도 읽을 수 있으며 ANSI 코드가 없습니다 — 그래프는 간선 목록으로 표시됩니다.

### HTML, 독립형 웹 보고서

테마 5가지 중 선택(CLI에서는 `--theme`, TUI에서는 선택기. 대응하는 테마가 있으면 기본적으로 현재 인터페이스 테마를 따름). 전용 레이아웃: 컨테이너, 정보 격자, 포트 상태별 통계 상자, 색상 배지, **아키텍처 그래프의 SVG 다이어그램**([§8](#8-아키텍처-그래프) 참조) — `omega-scan`/`omega-check`와 같은 시각적 계열입니다.

## 13. 기록과 비교

각 분석은 저장됩니다(SQLite, `var/db/omega-deep.db`): 하나의 `scan_id`에 루트 대상**과** 발견/승인된 모든 호스트, 그리고 재구성된 그래프가 담깁니다. 루트 대상별 기록 조회(발견된 대상 수 전용 열 포함), 지난 분석의 상세(호스트 + 그래프), 두 분석의 비교(**루트 대상**의 포트 상태만 — 발견 그래프의 비교는 가능한 확장이지만 지금은 필요하지 않음), 같은 루트 대상에 대해 다시 입력하지 않고 분석 다시 실행.

## 14. 테스트

```bash
source .venv/bin/activate
lint-imports        # Dependency Rule 검사
pytest -q           # 테스트 191개
ruff check src tests
mypy -p omega_deep
```

구조: `tests/unit/`(실제 I/O 없는 도메인과 애플리케이션), `tests/integration/`(실제 SQLite/파일, 가짜 HTTP 서버 `pytest-httpserver`, `trustme`를 통한 TLS), `tests/tui/`(`Pilot`을 통한 탐색, 구조적 — 시각 검증을 했다고 주장하지 않음).

## 15. 범위 밖

- CVE 스캔
- SQLi, XSS, RCE의 능동적 탐지
- 운영 체제 핑거프린팅
- nmap 방식의 저수준 스캔 기법(SYN 스캔, 원시 패킷)
- 크롤링
- 퍼징
- 무차별 대입
- 명시적 승인 없이 발견된 대상 스캔 — 어떤 모드에서도 절대 하지 않음
- 명시적 설정 없이 최초 대상의 사설 서브넷 밖에서 발견
- 웹 대시보드

---

> Omega-deep — 발견하고, 지도로 그리고, 평가하고, 보고한다.
> 신뢰도를 명시해 재구성한 아키텍처이지, 사실로 꾸민 짐작이 결코 아니다.
