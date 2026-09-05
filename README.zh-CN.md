<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（见 LICENSE 文件） -->
<div align="center">
  <img src="docs/assets/omega-deep.png" alt="Omega-Deep" width="256">
</div>

# 🖧 OMEGA-DEEP

**多目标架构分析（发现 + 安全护栏 + 图谱）**

> 由 **kraynux** 为 **Omega-server** 开发  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

官方页面：[OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; 预览：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**语言：**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)

---

**Omega-deep** 在单个目标上实现了 `omega-check` 的全部功能（端口扫描、服务识别、角色识别、WAF 与 TLS），并根据已扫描目标留下的线索（请求头、重定向、证书和 HTML 链接）增加了**额外目标发现**功能。发现过程受到严格的**安全护栏**约束，并且在扫描任何发现的目标之前都必须获得**用户明确确认**。随后，工具会**重建架构图谱**，展示目标之间的通信关系及其可信度。它是 `omega-` 工具套件中的第五个工具（继 `omega-fire`、`omega-stress`、`omega-scan` 和 `omega-check` 之后），采用 Clean Architecture 组织；完整的技术说明请参阅 `docs/ARCHITECTURE.md`。

## 1. 愿景与范围

Omega-deep 回答了 omega-check 没有提出的问题：*这个 IP 后面还有什么？* 反向代理声明了自己的后端、证书覆盖了多个主机，或页面指向了相邻服务——这些都是 omega-deep 会谨慎跟踪的线索，但它绝不会据此自动扫描目标。

### Omega-deep 的功能

- 像 omega-check 一样扫描根目标（系统配置文件或已保存的个人配置文件）。
- 根据每个已扫描主机留下的线索发现候选目标：HTTP 请求头（`X-Forwarded-Host`、`X-Real-IP`、`X-Backend-Server`、`Via`）、重定向（`Location`）、TLS 证书（SAN）和 HTML 链接；参阅[§4](#4-目标发现与安全护栏)。
- **绝不会**在没有逐目标明确确认的情况下扫描发现的目标——沉默不代表接受。
- 通过严格护栏限制发现范围：最大深度、额外目标的最大数量和允许的子网（默认与根目标使用同一私有网段）。
- 根据每个已接受目标的来源（`proxy_to`、`redirect_to`、`linked_to`）重建**架构图谱**，并为每条关系标记可信度；参阅[§8](#8-架构图谱)。
- 通过 TUI（Textual）或可脚本化 CLI 输出结果，并提供与 omega-check 相同的三种导出格式（JSON、文本和包含 5 种主题的 HTML）；HTML 中的图谱是**真正绘制的图表**，而不是表格。
- 为每条收集到的信息（服务信息和发现信息）标记明确的可信度等级；参阅[§9](#9-可信度策略)。
- 持久化保存分析历史，并支持随时间重新运行和比较。

### Omega-deep 不做什么

- 不执行主动漏洞扫描，也不执行 SQLi、XSS 或 RCE 检测。
- 不扫描 CVE。
- 不进行操作系统指纹识别。
- 不使用类似 nmap 的低级扫描技术（SYN 扫描、原始数据包），只使用应用层 TCP 连接。
- 不是暴力破解或模糊测试工具。
- 在任何模式下都不会在没有用户明确确认的情况下扫描发现的目标。
- 除非显式配置 `--subnet`，否则不会超出初始目标的私有子网进行发现。
- 不提供 Web 控制面板。

## 2. 安装

### 前置要求

- Python 3.10+
- 用于安装依赖的 Internet 连接

### 安装

```bash
[ -d omega-deep ] && echo "ℹ️ 已在此处解压，跳过该步骤。" || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh` 会：

1. 在不存在时创建 `.venv` 虚拟环境。
2. 安装依赖（`vendor/omega-lib/`，然后执行 `pip install -e .`；`pyproject.toml` 仍是唯一可信来源）。
3. 为 `omega-deep.sh` 和 `install.sh` 添加执行权限。
4. 将 `deep` 别名添加到 `~/.bashrc` 和 `~/.zshrc`，如果已经存在则不会重复添加。

### 依赖

依赖声明位于 `pyproject.toml` 中（不再使用 `requirements.txt`）：
- `omega-lib`：套件共享库（`ConfidenceLevel`、主题和终端检测），内置于 `vendor/omega-lib/`。
- `textual`：TUI 界面、主题和终端自动适配。
- `httpx`：HTTP/HTTPS 服务和发现探测。
- `cryptography`：读取协商得到的 TLS 证书。
- `jinja2`：HTML 导出模板。
- 开发依赖（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`trustme`、`ruff`、`mypy`、`import-linter`。

## 3. 使用方法

### 交互模式（TUI）

推荐日常使用，直接无参数启动：

```bash
./omega-deep.sh
```

如果已经创建别名，也可以直接在终端中输入：

```bash
deep
```

操作流程：启动画面（按键或单击关闭）→ 主菜单（分析 / 配置文件 / 历史 / 设置 / 帮助）→ 输入根目标，选择配置文件和发现护栏（最大深度、目标最大数量和允许的子网）→ 分析（不确定进度条，并实时显示网络操作）→ 每发现一批目标，就显示确认画面（每个目标一行，显示来源/可信度/证据；接受或拒绝切换，默认不勾选任何目标）→ 分析详情（主机、端口/服务/角色、图谱和导出）→ 从主菜单访问历史、比较、重放和设置。终端适配（颜色、尺寸和结构降级）会自动完成。

#### 键盘快捷键

| 按键 | 操作 |
|---|---|
| `↑` / `↓` | 在屏幕元素之间移动 |
| `Tab` / `Shift+Tab` | 在表单字段之间移动 |
| `Esc` | 返回上一屏幕（在首页确认退出） |
| `t` | 切换到下一个主题（立即应用，无需确认） |
| `r` | 刷新终端检测 |
| `a` | 显示帮助 |
| `q` | 退出（需要确认） |

### 可脚本化模式（CLI）

任何子命令都会进入 CLI 模式：

```bash
# 分析目标（根目标扫描 + 多目标发现）
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# 历史（可按根目标过滤）
./omega-deep.sh history --target 192.168.1.10 --limit 20

# 查看分析详情（文本、JSON 或 HTML），可选择 5 种导出主题
./omega-deep.sh show <scan_id> --format html --theme omega-base --output rapport.html

# 比较两次分析（根目标的端口状态）
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# 个人端口配置文件
./omega-deep.sh profile list
./omega-deep.sh profile create labo --ports 22,80,443 --description "我的配置文件"
./omega-deep.sh profile edit labo --ports 22,80,443,8080
./omega-deep.sh profile pin labo
./omega-deep.sh profile unpin labo
./omega-deep.sh profile delete labo
```

在 CLI 中，每个发现的目标都会单独询问是否验证（`扫描 <目标>？[y/N]`），提问前会显示证据。`--auto-validate` 会跳过审查并接受全部目标（**不建议使用**，程序会显示警告）；在非交互环境中（没有 TTY 且未指定 `--auto-validate`），所有发现的目标都会默认拒绝，而不会在没有确认的情况下扫描。

### 支持的目标格式

```text
192.168.1.10                IPv4
example.org                 主机名
http://example.org          HTTP URL（解析前移除协议）
https://example.org:8443    带端口的 HTTPS URL（移除协议和端口）
```

在 DNS 解析前，会移除可能存在的协议和端口（`domain/targets/validation.py::normalize_target_input`）：可以粘贴完整 URL，最终只保留主机。*发现的*目标也会按相同方式规范化，但绝不会在未验证的情况下扫描；参阅[§4](#4-目标发现与安全护栏)。

## 4. 目标发现与安全护栏

### 线索来源

| 来源 | 来源细节 | 可信度 |
|---|---|---|
| `header` | `X-Forwarded-Host`、`X-Real-IP`、`X-Backend-Server`、`Via` | `DECLARED` |
| `redirection` | HTTP 响应的 `Location` 请求头 | `DECLARED` |
| `certificate` | 协商 TLS 证书的 SAN（Subject Alternative Names） | `DECLARED` |
| `html_link` | 页面提供的链接（`<a href>`） | `INFERRED` |

`DECLARED` 值仍然只是目标自我声明的内容，可能被伪造；参阅[§10](#10-防范伪造值)。`html_link` 刻意作为最弱来源：普通链接并不声明任何基础设施关系。

### 安全护栏（始终启用，无法禁用）

- **范围**：候选目标必须是与根目标位于同一个 `/24` 中的私有 IP，除非显式指定 `--subnet`。指定后只检查目标是否属于给定子网，即使该子网包含公网 IP 也一样——例外必须通过显式配置授权。无法解析的主机名不会被该过滤器接受。
- **深度**：`--max-depth`（默认 3），最多 A → B → C → D。
- **目标数量**：`--max-targets`（默认 10），所有深度合计。

### 验证（未经确认绝不扫描）

每个提议的目标都会经过 `PROPOSED → PRESENTED → ACCEPTED` 或 `REJECTED` 状态。**Fail-safe** 规则意味着：任何未被明确接受的目标（沉默、关闭屏幕、中断、超时或没有 TTY）都视为拒绝，绝不会反过来处理。在 TUI 中，专用界面会列出批次中的目标、证据和可信度，并允许逐行接受或拒绝、全部接受或全部拒绝；按 Esc 默认全部拒绝。在 CLI 中，每个目标都会单独提问；`--auto-validate`（不建议）是唯一绕过交互确认的方式。

## 5. 扫描配置文件

| 配置文件 | 描述 | 已固定 |
|---|---|---|
| `minimal` | 超快速扫描：SSH + HTTP + HTTPS（22、80、443） | 是 |
| `classic` | 经典 Internet/LAN 服务 | 是 |
| `web` | Web 服务及替代端口 | 否 |
| `db` | 数据库和数据服务 | 否 |
| `remote` | 远程访问：Shell、桌面和 RustDesk | 否 |
| `mail` | 邮件服务 | 否 |
| `dns` | DNS 服务 | 否 |
| `iot` | IoT 设备、摄像头、路由器和智能家居 | 否 |
| `dev` | 开发和实验环境 | 否 |
| `docker` | Docker、Swarm 和常见容器服务 | 否 |
| `complet` | **动态生成**：上述所有配置文件的排序去重并集 | 否 |
| *个人配置文件* | 在 **配置文件**（TUI）界面或通过 `profile create`（CLI）创建，与系统配置文件显示在同一位置；TUI 中以 `* ` 为前缀 | 否 |

配置文件同时应用于根目标**以及**每个已接受的发现目标——不会为每个主机使用不同配置文件。完整说明、验证规则和个人配置文件管理见：`docs/PROFILES.md`。

## 6. 架构

Omega-deep 采用 **Clean Architecture**（domain / application / infrastructure / interfaces / ports / core / app / plugins / shared）组织，与 `omega-` 套件模板（参见 `omega-scan`/`omega-check`）保持一致，并在每次修改时通过 `import-linter` 验证。完整说明位于 **`docs/ARCHITECTURE.md`**。

简要结构：

```text
src/omega_deep/
├── domain/          纯业务逻辑：扫描、目标、服务、配置文件、报告，
│                    discovery（提议目标、验证状态机），
│                    architecture（图谱和关系规则）
├── application/     用例（commands/queries），包括 discover_targets、
│                    validate_targets、reconstruct_architecture
│                    （相对于 omega-check 新增）
├── ports/           应用所需的契约（probers，包括 discovery_prober、
│                    repositories、exporters……）
├── infrastructure/  具体实现（socket/httpx/cryptography、SQLite、
│                    图谱 SVG 渲染；Textual 不在此处）
├── interfaces/      tui/（Textual）和 cli/（可脚本化），功能严格对等
├── app/             组装（DependencyContainer、bootstrap、生命周期）
├── core/, shared/   跨领域词汇和非业务工具
└── plugins/         已建立但为空的结构（尚无确认的扩展方向）
```

设计规则：
- `domain/services/policies.py`：对已收集的线索进行分类，从不执行网络操作。
- `domain/discovery/policies.py`：处理范围、深度和数量护栏；纯逻辑，可在无网络环境下测试。
- `domain/architecture/service.py`：根据每个 `Host` 已记录的来源重建图谱，不重新发起请求。
- `infrastructure/network/` 和 `infrastructure/discovery/`：执行网络操作（sockets、`httpx`、`cryptography`），但从不做判断。
- `interfaces/`：只负责显示，不包含业务逻辑。发现目标验证界面调用 `validate_targets`，而不是自行实现 fail-safe 规则。
- `infrastructure/exporters/`：读取分析结果（扫描、主机和图谱），不重新计算任何内容。

## 7. 服务与角色识别

### 检测的协议

| 协议 | 探测方式 | 收集的信息 |
|---|---|---|
| HTTP / HTTPS | `httpx` | `Server` 横幅、认证请求头 |
| TLS | `cryptography`（协商证书，包括 `CERT_NONE`） | 版本、cipher、证书主题/颁发者 |
| SSH | 原始横幅 | 软件和版本（例如 `OpenSSH 10.4`） |
| VNC（RFB） | 服务器声明的安全代码 | 支持的认证类型 |
| 通用 | 对未识别开放端口读取原始横幅 | 谨慎提取，不使用激进启发式规则 |

### 推断的角色

角色依据**实际协商的协议**推断，而不是依据假定的端口号：

| 角色 | 条件 | 可信度 |
|---|---|---|
| `Web 服务器` | 已确认 HTTP/HTTPS 协议 | `INFERRED` |
| `Shell 访问` | 已确认 SSH 协议 | `CORROBORATED` |
| `图形访问` | 已确认 VNC 协议 | `CORROBORATED` |
| `数据库` | 端口属于系统 `db` 配置文件的范围 | `INFERRED` |

### 已知 WAF 特征

通过声明性请求头（`server`、`x-sdk`）检测。其存在由**目标自行声明**，从不独立验证：Cloudflare、Sucuri、Akamai、Imperva Incapsula、AWS ELB（仅作参考列出，严格来说并不是应用 WAF）。

## 8. 架构图谱

图谱完全根据每个已接受主机中已经记录的来源（`discovered_from`/`discovery_source`/`discovery_confidence`）重建：不会发起新的网络请求，也不会重新分析原始线索。

### 生成的关系

| 关系 | 发现来源 | 含义 |
|---|---|---|
| `proxy_to` | `header` | 根目标（或已接受的主机）很可能是指向发现目标的代理 |
| `redirect_to` | `redirection` | 观察到 HTTP 重定向指向发现目标 |
| `linked_to` | `certificate` 或 `html_link` | 最中性的关系：共享基础设施/应用，但不确认流量方向 |

不会生成 `backend_of`（`proxy_to` 的反向边），因为它只是重复信息，不是新的推断。

### 渲染

- **TUI**（分析详情）和 **JSON/文本导出**：显示边列表（来源、关系、目标和可信度）；终端不适合呈现复杂图形。
- **HTML 导出**：提供**真正的 SVG 图表**（节点为圆形，边为带标签的箭头），根据根目标进行分层布局，大小与发现的机器数量成比例。不依赖重量级图布局库，因为图谱在设计上较小，并受[§4](#4-目标发现与安全护栏)中的护栏限制。

## 9. 可信度策略

每个收集到的字段都具有以下一种可信度等级：

| 等级 | 含义 |
|---|---|
| `VERIFIED` | 直接观察到的协议事实，目标无法伪造（例如由 TCP RST 确认的关闭端口，或实际协商的 TLS 版本）。 |
| `DECLARED` | 目标在完全由其控制的字段中自行声明的值（例如 `Server` 横幅或 `X-Backend-Server` 请求头）：合理但可以随意伪造。 |
| `CORROBORATED` | 由独立线索确认的 `DECLARED` 值（例如实际协商出 SSH 协议后得到的 SSH 角色）。 |
| `INFERRED` | 根据模式或启发式规则推断，没有目标的明确声明（例如 HTML 链接）。 |
| `UNKNOWN` | 没有可用线索，或目标主动隐藏了信息。 |

## 10. 防范伪造值

Omega-deep 不会默认信任目标自行声明的数据，并会明确标示其可信度。目标发现是最敏感的部分：恶意目标*可能*声明虚假的 `X-Backend-Server`，将发现过程引向任意 IP。工具使用两个相互独立的结构性保护措施：
- 任何来源于目标的信息都不会仅因被声明就获得 `VERIFIED`：`Server` 横幅或 `X-Backend-Server` 请求头始终保持 `DECLARED`，无论其看起来多么合理。
- 范围护栏（[§4](#4-目标发现与安全护栏)）限制声明目标能够指向的范围（同一私有 `/24`，除非显式配置），用户验证则决定是否真正扫描。范围外的虚假目标甚至不会被提出；范围内的目标仍然必须经过明确确认。

## 11. 终端兼容性

TUI（Textual）会自动检测终端能力（模拟器和尺寸），并据此调整结构化样式（`complete`/`standard`/`reduced`/`mono`），无需手动参数。CLI 始终使用纯文本，与终端无关。该策略由整个 `omega-` 套件共享（`omega-lib`、`terminal/policies.py`）。

### 按模拟器确定配置

| 模拟器 | 初始配置 |
|---|---|
| Ghostty、Alacritty、WezTerm、Kitty | `complete` |
| Konsole、GNOME Terminal、Terminator、Xfce4 Terminal | `standard` |
| xterm、urxvt、现代 SSH | `reduced` |
| Linux TTY、旧版 SSH | `mono` |
| 未识别的模拟器 | `reduced`（默认回退） |

### 按终端尺寸确定配置

| 最小尺寸（列 × 行） | 配置上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 更小 | `mono` |

最终配置取两个条件（模拟器和尺寸）中**限制最严格的一个**。例如，Ghostty 即使允许 `complete`，当窗口缩小到 70 列时也会降级为 `mono`。可以使用 `r` 键实时刷新。

## 12. 导出

报告默认生成在 `var/exports/`（运行时路径以项目目录为基准，可通过 `$OMEGA_DEEP_VAR_DIR` 覆盖），也可以写入指定路径（CLI 使用 `--output`，TUI 使用对话框）。文件名明确并包含时间：`analyse-{profil}-{date}.ext`；个人配置文件使用 `analyse-custom-{date}.ext`。

### JSON，事实来源

完整的分析结构（`Scan` + `Host[]` + `ArchitectureGraph`），严格可序列化为 JSON，并包含可信度等级。

### 文本，紧凑的人类可读报告

无需 ANSI 控制码，在终端之外也能阅读；图谱以边列表显示。

### HTML，独立 Web 报告

可选择 5 种主题（CLI 使用 `--theme`，TUI 使用选择器；如果存在对应主题，默认跟随当前界面主题）。专用布局包括容器、信息网格、按端口状态划分的统计卡片、彩色徽章以及**架构图谱 SVG 图表**（参阅[§8](#8-架构图谱)），整体视觉风格与 `omega-scan`/`omega-check` 保持一致。

## 13. 历史与比较

每次分析都会保存到 SQLite（`var/db/omega-deep.db`）：`scan_id` 包含根目标、全部发现并接受的主机，以及重建后的图谱。历史可以按根目标查询，并显示发现目标数量；可以查看历史分析详情（主机和图谱）、比较两次分析（仅比较**根目标**的端口状态——比较发现图谱可以作为未来扩展，但目前没有必要），还可以在不重新输入目标的情况下重新运行同一个根目标。

## 14. 测试

```bash
source .venv/bin/activate
lint-imports        # 验证 Dependency Rule
pytest -q           # 173 个测试
ruff check src tests
mypy -p omega_deep
```

目录结构：`tests/unit/`（领域和应用，无真实 I/O）、`tests/integration/`（SQLite/真实文件、`pytest-httpserver` 虚拟 HTTP 服务器、通过 `trustme` 提供 TLS）以及 `tests/tui/`（通过 `Pilot` 进行结构化导航测试；不声称提供自动视觉验证）。

## 15. 不在范围内

- CVE 扫描。
- 主动检测 SQLi、XSS 和 RCE。
- 操作系统指纹识别。
- 类似 nmap 的低级扫描技术（SYN 扫描、原始数据包）。
- 爬取。
- 模糊测试。
- 暴力破解。
- 在任何模式下未经明确确认扫描发现的目标。
- 未显式配置时，超出初始目标私有子网的发现。
- Web 控制面板。

---

> Omega-deep —— 发现、绘制、评估、报告。  
> 以明确的可信度重建架构，而不是把猜测伪装成事实。
