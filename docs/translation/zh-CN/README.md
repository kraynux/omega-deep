<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（见 LICENSE 文件） -->
<div align="center">
  <img src="../../assets/omega-deep.png" alt="Omega-Deep" width="384">
</div>

# 🖧 OMEGA-DEEP

**多目标架构分析（发现 + 安全限制 + 关系图）**

> 由 [kraynux](https://github.com/kraynux) 为 [Omega-Server](https://kraynux.snake-mackarel.ts.net) 打造   

官方页面：[OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; 截图：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 界面和导出的报告提供 **17 种语言** — 见[界面语言](#界面语言)。  
**语言：**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** 具备 `omega-check` 在单一目标上的全部能力（端口扫描、服务识别、角色、WAF、TLS），并在此基础上，根据已扫描目标留下的线索（响应头、重定向、证书、HTML 链接）**发现更多目标**——始终处于**严格的安全限制**之下，并在扫描任何新发现目标之前**由用户明确确认**——随后**重建一张架构关系图**（谁与谁通信、可信度如何）。它是 `omega-` 套件中的一个工具，采用 Clean Architecture 构建 — 完整技术细节见 `docs/ARCHITECTURE.md`。

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-deep/D.png" width="24%" />
</p>

## 1. 愿景与范围

Omega-deep 回答了 omega-check 不会提出的问题：*这个 IP 背后还有什么？* 一个公布其后端的反向代理、一张覆盖多个主机的证书、一个指向邻近服务的页面——这些都是 omega-deep 会谨慎跟进的线索，但绝不会擅自行动。

### Omega-deep 能做什么

- 以与 omega-check 完全相同的方式扫描根目标（系统配置或已保存的个人配置）。
- 根据每个已扫描主机留下的线索发现候选目标：HTTP 响应头（`X-Forwarded-Host`、`X-Real-IP`、`X-Backend-Server`、`Via`）、重定向（`Location`）、TLS 证书（SAN）、HTML 链接 — 见 [§4](#4-目标发现与安全限制)。
- **绝不**在未经明确确认的情况下扫描新发现的目标，逐个目标确认——沉默绝不等于同意。
- 用严格的安全限制约束发现过程：最大深度、额外目标的最大数量、允许的子网（默认与根目标属于同一私有网段）。
- 根据每个已接受目标的来源重建**架构关系图**（`proxy_to`、`redirect_to`、`linked_to`），每条关系都带有可信度 — 见 [§8](#8-架构关系图)。
- 在 TUI（Textual）或可脚本化的 CLI 中呈现结果，提供与 omega-check 相同的三种导出（JSON、文本、带 5 种主题的 HTML）— 在 HTML 中，关系图是**真正绘制出来的图表**，而不是表格。
- 为收集到的每条信息（服务或发现）标注明确的可信度 — 见 [§9](#9-可信度策略)。
- 保留持久的分析历史，可重放，并可随时间对比。

### Omega-deep 不做什么

- 主动漏洞扫描：不做 SQLi、XSS 或 RCE。
- CVE 扫描。
- 操作系统指纹识别。
- nmap 式的底层扫描技术（SYN 扫描、原始数据包）— 仅使用应用层 TCP 连接。
- 暴力破解或模糊测试工具。
- 未经用户明确确认就扫描新发现的目标——任何模式下都不会。
- 在初始目标的私有子网之外进行发现，除非明确配置（`--subnet`）。
- Web 仪表盘。

## 2. 安装

### 前提条件

- Python 3.10+
- 互联网连接，用于安装依赖

### 安装

```bash
[ -d omega-deep ] && echo "ℹ️ 此处已解压，跳过此步骤。" || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`：

1. 如果虚拟环境 `.venv` 尚不存在，则创建它。
2. 安装依赖（先 `vendor/omega-lib/`，再 `pip install -e .`；`pyproject.toml` 仍是唯一的权威来源）。
3. 使 `omega-deep.sh` 和 `install.sh` 可执行。
4. 将别名 `deep` 添加到 `~/.bashrc` 和 `~/.zshrc`（已存在时不会重复添加）。

### 依赖

在 `pyproject.toml` 中声明（不再有 `requirements.txt`）：
- `omega-lib`：套件的共享库（`ConfidenceLevel`、主题、终端检测）— 内置于 `vendor/omega-lib/`
- `textual`：TUI 界面、主题、自动适配终端
- `httpx`：HTTP/HTTPS 探测（服务识别与发现）
- `cryptography`：读取协商得到的 TLS 证书
- `jinja2`：HTML 导出的模板
- 开发依赖（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`trustme`、`ruff`、`mypy`、`import-linter`

## 3. 使用

### 交互模式（TUI）

推荐日常使用 — 不带参数启动：

```bash
./omega-deep.sh
```
如果已创建别名，只需在终端输入 `deep`：
```bash
deep
```

流程：启动画面（按任意键或点击关闭）→ 主菜单（分析 / 配置 / 历史 / 设置 / 帮助）→ 输入根目标，选择配置和发现的安全限制（最大深度、最大目标数、允许的子网）→ 分析（不确定进度条和实时网络操作日志）→ 每发现一批目标，就会出现确认屏幕（每个目标一行，显示来源/可信度/证据，可切换接受/拒绝——默认不勾选任何项）→ 分析详情（主机、端口/服务/角色、关系图、导出）→ 从主菜单进入历史/对比/重放和设置。对终端的适配（颜色、尺寸、结构降级）是自动的。

#### 键盘快捷键

| 按键 | 操作 |
|---|---|
| `↑` / `↓` | 在屏幕元素之间移动 |
| `Tab` / `Shift+Tab` | 在表单字段之间移动 |
| `Esc` | 返回上一屏（在主屏上会确认是否退出） |
| `t` | 下一个主题（立即应用，无需确认） |
| `r` | 刷新终端检测 |
| `a` | 显示帮助 |
| `q` | 退出（需确认） |

### 界面语言

界面提供 17 种语言：法语、英语、西班牙语、葡萄牙语（巴西）、意大利语、德语、荷兰语、波兰语、俄语、简体中文、越南语、泰语、印尼语、日语、韩语、印地语和阿拉伯语。在设置中选择（“Langue / Language”），重启界面后生效；变量 `OMEGA_DEEP_LANG`（例如 `OMEGA_DEEP_LANG=zh-CN ./omega-deep.sh`）可在一次会话中强制使用某种语言。从 omega-suite 启动时，omega-deep 使用套件的语言。在 Linux 文本控制台（TTY）上，非拉丁文字的语言在本次会话中以英语显示。命令行保持法语。

### 联系与支持

帮助（`a` 键）提供 **联系与支持** 界面：*请我喝杯咖啡*（开发者的 PayPal 页面）、*联系支持*（明文显示的电子邮件地址和网站联系表单）、*登记为用户（匿名）* 和 *检查更新*。 登记是自愿的，默认关闭，且只发送一次：仅用于统计用户数量，以及（如您愿意）其所在的大洲或国家（封闭列表，绝无自由文本）。它发送一个随机生成的密钥、软件名称（`omega-deep`）及其版本；绝不发送姓名、机器名称、设置、目标或结果。IP 地址不会记录在登记中，但与任何访问一样，会经过接收服务器的安全检查和日志。 可随时在同一界面撤回（*不再登记我*）。 检查更新仅读取网站上已发布版本的列表，且从不在未点击的情况下进行。

### 脚本模式（CLI）

任何子命令都会进入 CLI 模式：

```bash
# 分析一个目标（根目标扫描 + 多目标发现）
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# 历史（可按根目标筛选）
./omega-deep.sh history --target 192.168.1.10 --limit 20

# 分析详情（文本、JSON 或 HTML）— 5 种导出主题可选
./omega-deep.sh show <scan_id> --format html --theme omega-base --output report.html

# 对比两次分析（根目标的端口状态）
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# 个人端口配置
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "我的配置"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

在 CLI 中，新发现的目标通过逐个目标的交互式提问来确认（`Scanner <cible> ? [o/N]`，与命令行其他部分一样为法语），每次提问前都会显示证据详情。`--auto-validate` 会不经审查地全部接受（**不推荐**，会显示警告）；在非交互环境中（没有 TTY，也没有 `--auto-validate`），所有新发现的目标默认被拒绝，而不是在未经确认的情况下被扫描。

### 可接受的目标格式

```text
192.168.1.10                IPv4
example.org                 主机名
http://example.org          HTTP URL（解析前去掉协议）
https://example.org:8443    带端口的 HTTPS URL（去掉协议和端口）
```

协议和端口（如有）会在 DNS 解析前去掉（`domain/targets/validation.py::normalize_target_input`）— 粘贴完整 URL 也能用，只保留主机部分。*新发现的*目标也按同样方式规范化，但未经确认绝不会被扫描（见 [§4](#4-目标发现与安全限制)）。

## 4. 目标发现与安全限制

### 线索来源

| 来源 | 出处 | 可信度 |
|---|---|---|
| `header` | `X-Forwarded-Host`、`X-Real-IP`、`X-Backend-Server`、`Via` | `DECLARED` |
| `redirection` | HTTP 响应的 `Location` 头 | `DECLARED` |
| `certificate` | 协商得到的 TLS 证书中的 SAN（Subject Alternative Names） | `DECLARED` |
| `html_link` | 页面提供的链接（`<a href>`） | `INFERRED` |

`DECLARED` 值仍然只是目标的自我声明（可伪造）— 见 [§10](#10-防范伪造的值)。`html_link` 被刻意设为最弱的来源：一个普通链接并不声明任何基础设施关系。

### 安全限制（始终生效，不可关闭）

- **范围**：候选目标必须是与根目标处于同一 `/24` 内的私有 IP，除非明确指定了 `--subnet`（此时只看是否属于给定子网，即使它包含公网 IP——正是明确的配置允许了这一例外）。尚未解析的主机名绝不会被此过滤器接受（为了检查而去解析它，本身就已是超出此项检查范围的网络操作）。
- **深度**：`--max-depth`（默认 3）— 最多 A → B → C → D。
- **目标数量**：`--max-targets`（默认 10）— 所有深度合计。

### 确认（未经确认绝不扫描）

每个被提议的目标都经历 `PROPOSED → PRESENTED → ACCEPTED` 或 `REJECTED`。规则是**失败即安全**：任何从未被明确接受的目标（沉默、关闭屏幕、中断、超时、没有 TTY）都按拒绝处理——绝不会反过来。在 TUI 中，一个专用屏幕列出一批目标及其证据和可信度，每行可切换接受/拒绝，提供“全部接受”/“全部拒绝”，按 Esc 默认全部拒绝。在 CLI 中，每个目标一个问题；`--auto-validate`（不推荐）是绕过交互的唯一方式。

## 5. 扫描配置

| 配置 | 说明 | 已固定 |
|---|---|---|
| `minimal` | 超快速扫描：SSH + HTTP + HTTPS（22、80、443） | 是 |
| `classic` | 常见的互联网/局域网服务 | 是 |
| `web` | Web 服务及备用端口 | 否 |
| `db` | 数据库和数据服务 | 否 |
| `remote` | 远程访问 — Shell、桌面、RustDesk | 否 |
| `mail` | 邮件服务 | 否 |
| `dns` | DNS 服务 | 否 |
| `iot` | 物联网设备、摄像头、路由器、智能家居 | 否 |
| `dev` | 开发/实验环境 | 否 |
| `docker` | Docker、Swarm 及常见容器化服务 | 否 |
| `complet` | **即时生成**：以上所有配置排序去重后的并集 | 否 |
| *个人配置* | 在**配置**屏幕（TUI）中或用 `profile create`（CLI）创建，与系统配置列在一起，在 TUI 中以 `* ` 为前缀 | 否 |

配置同时适用于根目标**和**每个已接受的新发现目标——不会为每个主机使用不同的配置。完整细节、校验规则和个人配置的管理：`docs/PROFILES.md`。

## 6. 架构

Omega-deep 采用 **Clean Architecture** 构建（domain / application / infrastructure / interfaces / ports / core / app / plugins / shared），与 `omega-` 套件的模板保持一致（见 `omega-scan`/`omega-check`），每次修改都由 `import-linter` 验证。完整细节见 **`docs/ARCHITECTURE.md`**。

非常简短的概览：

```text
src/omega_deep/
├── domain/          纯业务逻辑：扫描、目标、服务、配置、报告、
│                    discovery（提议的目标、确认状态机）、
│                    architecture（关系图、关系规则）
├── application/     用例（commands/queries）— 包括 discover_targets、
│                    validate_targets、reconstruct_architecture（相对 omega-check 新增）
├── ports/           应用所需的契约（探测器，包括 discovery_prober、
│                    仓储、导出器……）
├── infrastructure/  具体实现（socket/httpx/cryptography、SQLite、
│                    关系图的 SVG 渲染 — Textual 不在这里）
├── interfaces/      tui/（Textual）和 cli/（可脚本化），功能严格对等
├── app/             装配（DependencyContainer、bootstrap、生命周期）
├── core/, shared/   通用词汇、非业务工具
└── plugins/         结构已就位，为空（尚无确定的扩展方向）
```

设计规则：
- `domain/services/policies.py`：对已收集的线索进行分类，从不访问网络。
- `domain/discovery/policies.py`：范围/深度/数量的安全限制——纯逻辑，无需网络即可测试。
- `domain/architecture/service.py`：根据每个 `Host` 已携带的来源重建关系图，不发起任何新请求。
- `infrastructure/network/` 和 `infrastructure/discovery/`：负责网络访问（套接字、`httpx`、`cryptography`），从不做判断。
- `interfaces/`：只负责显示，不包含任何业务逻辑——新发现目标的确认屏幕调用 `validate_targets`，并不自行实现“失败即安全”的规则。
- `infrastructure/exporters/`：读取分析结果（扫描、主机、关系图），不重新计算任何东西。

## 7. 服务识别与角色

### 检测的协议

| 协议 | 探测方式 | 收集的细节 |
|---|---|---|
| HTTP / HTTPS | `httpx` | `Server` 横幅、认证相关响应头 |
| TLS | `cryptography`（协商得到的证书，包括 `CERT_NONE`） | 版本、加密套件、证书主体/颁发者 |
| SSH | 原始横幅 | 软件和版本（如 `OpenSSH 10.4`） |
| VNC (RFB) | 服务器公布的安全类型代码 | 支持的认证类型 |
| 通用 | 未识别开放端口上的原始横幅 | 谨慎提取，不使用激进的启发式规则 |

### 推断的角色

根据**实际协商**的协议推断，绝不凭端口号猜测：

| 角色 | 条件 | 可信度 |
|---|---|---|
| `Web 服务器` | 已确认 HTTP/HTTPS 协议 | `INFERRED` |
| `Shell 访问` | 已确认 SSH 协议 | `CORROBORATED` |
| `图形访问` | 已确认 VNC 协议 | `CORROBORATED` |
| `数据库` | 端口位于系统配置 `db` 的范围内 | `INFERRED` |

### 已知 WAF 签名

通过声明式响应头（`server`、`x-sdk`）检测 — 其存在**由目标自行声明**，从不进行独立验证：Cloudflare、Sucuri、Akamai、Imperva Incapsula、AWS ELB（仅作参考列出，严格来说不是应用层 WAF）。

## 8. 架构关系图

仅根据每个已接受主机已携带的来源（`discovered_from`/`discovery_source`/`discovery_confidence`）重建——不发起新的网络请求，也不重新分析原始线索。

### 生成的关系

| 关系 | 发现来源 | 含义 |
|---|---|---|
| `proxy_to` | `header` | 根目标（或某个已接受的主机）很可能是通往新发现目标的代理 |
| `redirect_to` | `redirection` | 观察到指向新发现目标的 HTTP 重定向 |
| `linked_to` | `certificate` 或 `html_link` | 最中性的关系——共享基础设施/应用，不断言流量方向 |

刻意不生成 `backend_of`（`proxy_to` 的反向边）——那只是重复信息，而不是新的推断。

### 呈现

- **TUI**（分析详情）和 **JSON/文本导出**：边的列表（来源、关系、目标、可信度）——终端并不适合丰富的图形呈现。
- **HTML 导出**：一张**真正的 SVG 图表**（节点 = 圆，边 = 带标签的箭头），从根目标出发计算分层布局，大小与发现的机器数量成正比——从不依赖沉重的图布局库；按设计关系图始终很小（受 [§4](#4-目标发现与安全限制) 的安全限制约束）。

## 9. 可信度策略

收集到的每个字段都带有以下级别之一：

| 级别 | 含义 |
|---|---|
| `VERIFIED` | 直接观察到的协议事实，目标无法伪造（如：由 TCP RST 确认的关闭端口、实际协商的 TLS 版本）。 |
| `DECLARED` | 目标在其完全控制的字段中自行声明的值（如 `Server` 横幅、`X-Backend-Server` 响应头）— 看似合理，但可被随意伪造。 |
| `CORROBORATED` | 一个 `DECLARED` 值被独立线索证实（如 SSH 角色，因为协议确实已协商）。 |
| `INFERRED` | 由模式/启发式规则推断，目标没有明确声明（如 HTML 链接）。 |
| `UNKNOWN` | 没有可用线索，或被目标主动隐藏。 |

## 10. 防范伪造的值

Omega-deep 不会在未明确标注的情况下信任任何由目标自行声明的数据——而目标发现是本项目最敏感的部分：恶意目标*可能*公布一个虚假的 `X-Backend-Server`，把发现过程引向它选定的 IP。为此有两道彼此独立的结构性防护：
- 任何源自目标的信息都不会仅仅因为被公布就成为 `VERIFIED`——`Server` 横幅或 `X-Backend-Server` 响应头无论看起来多么可信，都仍是 `DECLARED`。
- 范围限制（[§4](#4-目标发现与安全限制)）约束了被公布的目标能引向何处（同一私有 `/24`，除非明确配置），而用户确认决定它是否会被扫描——范围之外的虚假目标根本不会被提出；范围之内的目标在任何扫描之前仍需明确确认。

## 11. 终端兼容性

TUI（Textual）会自动检测终端的能力（模拟器、尺寸），并据此调整其结构样式表（`complete`/`standard`/`reduced`/`mono`），无需手动选项。CLI 模式始终是纯文本，与终端无关。该策略由整个 `omega-` 套件共享（`omega-lib`、`terminal/policies.py`）。

### 按检测到的模拟器确定的配置

| 模拟器 | 初始配置 |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm、urxvt、现代 SSH | `reduced` |
| Linux TTY、旧版 SSH | `mono` |
| 无法识别的模拟器 | `reduced`（默认回退） |

### 按终端尺寸确定的配置

| 最小尺寸（列 × 行） | 配置上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 更小 | `mono` |

最终配置为**两者中更严格的一个**（模拟器和尺寸）— 全屏的 Ghostty 若缩小到 70 列，会降为 `mono`，即使其模拟器允许 `complete`。可用 `r` 键实时刷新。

## 12. 导出

文本和 HTML 报告使用设置中选择的语言编写（“导出语言”，默认与界面相同）；JSON 作为数据保持不翻译。报告默认生成在 `var/exports/`（运行时路径锚定在项目目录，可用 `$OMEGA_DEEP_VAR_DIR` 覆盖），或生成在指定路径（CLI 中用 `--output`，TUI 中用对话框）。文件名清晰并带时间戳：`analyse-{配置}-{日期}.ext`，个人配置为 `analyse-custom-{日期}.ext`。

### JSON，权威来源

分析的完整结构（`Scan` + `Host[]` + `ArchitectureGraph`），严格可序列化为 JSON，包含可信度级别。

### 文本，紧凑的可读报告

在终端之外也可阅读，不含 ANSI 代码——关系图以边列表的形式呈现。

### HTML，独立的网页报告

5 种主题可选（CLI 中用 `--theme`，TUI 中用选择器；若有对应主题，默认跟随当前界面主题）。专门的布局：容器、信息网格、按端口状态的统计框、彩色徽章、**架构关系图的 SVG 图表**（见 [§8](#8-架构关系图)）— 与 `omega-scan`/`omega-check` 属于同一视觉风格。

## 13. 历史与对比

每次分析都会保存（SQLite，`var/db/omega-deep.db`）：一个 `scan_id` 包含根目标**以及**所有已发现/已接受的主机，外加重建的关系图。可按根目标查看历史（有专门一列显示发现的目标数），查看过往分析的详情（主机 + 关系图），对比两次分析（仅比较**根目标**的端口状态——对比发现关系图是可能的扩展，目前并不需要），以及对同一根目标重放分析而无需重新输入。

## 14. 测试

```bash
source .venv/bin/activate
lint-imports        # 检查 Dependency Rule
pytest -q           # 191 个测试
ruff check src tests
mypy -p omega_deep
```

结构：`tests/unit/`（领域和应用层，无真实 I/O），`tests/integration/`（真实 SQLite/文件、模拟 HTTP 服务器 `pytest-httpserver`、通过 `trustme` 的 TLS），`tests/tui/`（通过 `Pilot` 导航，结构性测试 — 不自称做了视觉验证）。

## 15. 范围之外

- CVE 扫描
- 主动检测 SQLi、XSS、RCE
- 操作系统指纹识别
- nmap 式的底层扫描技术（SYN 扫描、原始数据包）
- 爬取
- 模糊测试
- 暴力破解
- 未经明确确认就扫描新发现的目标——任何模式下都不会
- 未经明确配置就在初始目标的私有子网之外进行发现
- Web 仪表盘

---

> Omega-deep — 发现、绘图、定级、报告。
> 以明确可信度重建的架构，绝不是伪装成事实的猜测。
