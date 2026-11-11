<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT ライセンス（LICENSE ファイルを参照） -->
<div align="center">
  <img src="../../assets/omega-deep.png" alt="Omega-Deep" width="384">
</div>

# 🖧 OMEGA-DEEP

**複数ターゲットのアーキテクチャ解析（発見 + 安全上の制限 + グラフ）**

> [Omega-Server](https://kraynux.snake-mackarel.ts.net) のために [kraynux](https://github.com/kraynux) が開発   

公式ページ：[OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; スクリーンショット：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 インターフェースとエクスポートされるレポートは **17 言語** に対応 — [インターフェースの言語](#インターフェースの言語)を参照。  
**言語：**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** は、`omega-check` が単一ターゲットに対して行うこと（ポートスキャン、サービスの特定、役割、WAF、TLS）をすべて引き継ぎ、スキャン済みのターゲットが残した手がかり（ヘッダー、リダイレクト、証明書、HTML リンク）から**さらに別のターゲットを発見**します。これは**厳格な安全上の制限**のもとで行われ、発見したターゲットをスキャンする前には必ず**ユーザーの明示的な承認**を求めます。そのうえで**アーキテクチャのグラフを再構築**します（誰が誰と通信しているか、どの程度の信頼度か）。`omega-` スイートのツールで、Clean Architecture で構成されています — 技術的な詳細はすべて `docs/ARCHITECTURE.md` を参照してください。

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ja/omega-deep/D.png" width="24%" />
</p>

## 1. ビジョンと範囲

Omega-deep は、omega-check が問わない問いに答えます：*この IP の背後には、ほかに何があるのか？* バックエンドを名乗るリバースプロキシ、複数のホストをカバーする証明書、隣のサービスを指すページ — omega-deep はこうした手がかりを慎重にたどりますが、決して独断では動きません。

### Omega-deep ができること

- ルートターゲットを omega-check とまったく同じようにスキャンします（システムプロファイル、または保存済みの個人プロファイル）。
- スキャン済みの各ホストが残した手がかりから候補ターゲットを発見します：HTTP ヘッダー（`X-Forwarded-Host`、`X-Real-IP`、`X-Backend-Server`、`Via`）、リダイレクト（`Location`）、TLS 証明書（SAN）、HTML リンク — [§4](#4-ターゲットの発見と安全上の制限) を参照。
- 発見したターゲットを、ターゲットごとの明示的な承認なしに**決して**スキャンしません — 沈黙は決して承認ではありません。
- 発見を厳格な安全上の制限で抑えます：最大の深さ、追加ターゲットの最大数、許可するサブネット（既定ではルートと同じプライベート範囲）。
- 承認された各ターゲットの由来（`proxy_to`、`redirect_to`、`linked_to`）から**アーキテクチャのグラフ**を再構築し、関係ごとに信頼度を付けます — [§8](#8-アーキテクチャのグラフ) を参照。
- 結果を TUI（Textual）またはスクリプト可能な CLI で表示し、omega-check と同じ 3 種類のエクスポート（JSON、テキスト、5 テーマの HTML）を備えます — HTML ではグラフが表ではなく、**実際に描かれた図**になります。
- 収集したすべての情報（サービスも発見も）に明示的な信頼度を付けます — [§9](#9-信頼度ポリシー) を参照。
- 解析履歴を永続的に保存し、再実行や経時的な比較ができます。

### Omega-deep がしないこと

- 能動的な脆弱性スキャン：SQLi、XSS、RCE は行いません。
- CVE スキャン。
- OS のフィンガープリント。
- nmap 風の低レベルなスキャン技法（SYN スキャン、生パケット）— アプリケーションレベルの TCP 接続のみです。
- 総当たりやファジングのツール。
- ユーザーの明示的な承認なしに、発見したターゲットをスキャンすること — どのモードでも決して行いません。
- 明示的に設定しない限り（`--subnet`）、最初のターゲットのプライベートサブネットを越えた発見。
- Web ダッシュボード。

## 2. インストール

### 前提条件

- Python 3.10+
- 依存関係のためのインターネット接続

### インストール

```bash
[ -d omega-deep ] && echo "ℹ️ ここに展開済みのため、この手順をスキップします。" || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`：

1. 仮想環境 `.venv` がまだなければ作成します。
2. 依存関係をインストールします（`vendor/omega-lib/`、続いて `pip install -e .`。`pyproject.toml` が唯一の正となる情報源です）。
3. `omega-deep.sh` と `install.sh` を実行可能にします。
4. エイリアス `deep` を `~/.bashrc` と `~/.zshrc` に追加します（既にあれば重複させません）。

### 依存関係

`pyproject.toml` で宣言（`requirements.txt` は廃止）：
- `omega-lib`：スイート共通ライブラリ（`ConfidenceLevel`、テーマ、端末検出）— `vendor/omega-lib/` に同梱
- `textual`：TUI インターフェース、テーマ、端末への自動適応
- `httpx`：HTTP/HTTPS のプローブ（サービスと発見）
- `cryptography`：ネゴシエートされた TLS 証明書の読み取り
- `jinja2`：HTML エクスポートのテンプレート
- 開発用の依存関係（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`trustme`、`ruff`、`mypy`、`import-linter`

## 3. 使い方

### 対話モード（TUI）

日常の利用におすすめ — 引数なしで起動します：

```bash
./omega-deep.sh
```
エイリアスを作成した場合は、端末で `deep` と入力するだけです：
```bash
deep
```

流れ：スプラッシュ画面（キーまたはクリックで閉じる）→ メインメニュー（解析 / プロファイル / 履歴 / 設定 / ヘルプ）→ ルートターゲットの入力、プロファイルと発見の安全上の制限（最大の深さ、最大ターゲット数、許可するサブネット）の選択 → 解析（不確定の進捗表示とネットワーク操作のリアルタイムログ）→ 発見したターゲットのまとまりごとに承認画面（ターゲットごとに 1 行、出所／信頼度／根拠を表示、承認／却下の切り替え — 既定では何も選択されていません）→ 解析の詳細（ホスト、ポート／サービス／役割、グラフ、エクスポート）→ メインメニューから履歴／比較／再実行と設定。端末への適応（色、サイズ、構造の簡略化）は自動です。

#### キーボードショートカット

| キー | 操作 |
|---|---|
| `↑` / `↓` | 画面の項目間を移動 |
| `Tab` / `Shift+Tab` | フォームの入力欄間を移動 |
| `Esc` | 前の画面に戻る（ホーム画面では終了を確認） |
| `t` | 次のテーマ（確認なしですぐに適用） |
| `r` | 端末の検出を更新 |
| `a` | ヘルプを表示 |
| `q` | 終了（確認あり） |

### インターフェースの言語

インターフェースは 17 言語に対応しています：フランス語、英語、スペイン語、ポルトガル語（ブラジル）、イタリア語、ドイツ語、オランダ語、ポーランド語、ロシア語、簡体字中国語、ベトナム語、タイ語、インドネシア語、日本語、韓国語、ヒンディー語、アラビア語。設定（「Langue / Language」）で選択し、インターフェースの再起動後に反映されます。変数 `OMEGA_DEEP_LANG`（例：`OMEGA_DEEP_LANG=ja ./omega-deep.sh`）で、1 セッションの間だけ言語を固定できます。omega-suite から起動した場合、omega-deep はスイートの言語を使います。Linux のテキストコンソール（TTY）では、ラテン文字以外の言語はそのセッション中は英語で表示されます。コマンドラインはフランス語のままです。

### お問い合わせとサポート

ヘルプ（`a` キー）には **お問い合わせとサポート** 画面があります：*コーヒーをおごる*（開発者の PayPal ページ）、*サポートに連絡*（メールアドレスとサイトのお問い合わせフォームをそのまま表示）、*ユーザーとして登録（匿名）*、*更新を確認*。 登録は任意で、既定では無効、送信は一度だけです。利用者の数と、希望すればその大陸または国（選択式のリストのみ、自由入力なし）を数えるためだけに使われます。送信されるのは、ランダムに生成したキー、ソフトウェア名（`omega-deep`）とそのバージョンだけで、名前、マシン名、設定、対象、結果は決して送信されません。IP アドレスは登録データには保存されませんが、通常のアクセスと同様に、受信サーバーのセキュリティチェックとログを通過します。 同じ画面からいつでも取り消せます（*登録を取り消す*）。 更新の確認は、サイトで公開されているバージョンの一覧を読むだけで、クリックしない限り行われません。

### スクリプトモード（CLI）

サブコマンドを指定すると CLI モードになります：

```bash
# ターゲットを解析（ルートのスキャン + 複数ターゲットの発見）
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# 履歴（ルートターゲットで絞り込み可能）
./omega-deep.sh history --target 192.168.1.10 --limit 20

# 解析の詳細（テキスト、JSON、HTML）— エクスポートのテーマは 5 種類から選択
./omega-deep.sh show <scan_id> --format html --theme omega-base --output report.html

# 2 つの解析を比較（ルートターゲットのポート状態）
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# 個人用ポートプロファイル
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "自分のプロファイル"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

CLI では、発見したターゲットをターゲットごとの対話的な質問で承認します（`Scanner <cible> ? [o/N]`。コマンドラインのほかの部分と同じくフランス語です）。各質問の前に根拠の詳細が表示されます。`--auto-validate` は確認なしですべてを承認します（**非推奨**、警告が表示されます）。非対話環境（TTY がなく、`--auto-validate` もない）では、発見したターゲットは承認なしにスキャンされるのではなく、既定ですべて却下されます。

### 受け付けるターゲットの形式

```text
192.168.1.10                IPv4
example.org                 ホスト名
http://example.org          HTTP の URL（名前解決の前にスキームを除去）
https://example.org:8443    ポート付き HTTPS の URL（スキームとポートを除去）
```

スキームとポートがあれば、DNS の名前解決の前に除去されます（`domain/targets/validation.py::normalize_target_input`）— URL を丸ごと貼り付けても動作し、ホスト部分だけが残ります。*発見された*ターゲットも同じ方法で正規化されますが、承認なしにスキャンされることはありません（[§4](#4-ターゲットの発見と安全上の制限) を参照）。

## 4. ターゲットの発見と安全上の制限

### 手がかりの出所

| 出所 | 由来 | 信頼度 |
|---|---|---|
| `header` | `X-Forwarded-Host`、`X-Real-IP`、`X-Backend-Server`、`Via` | `DECLARED` |
| `redirection` | HTTP レスポンスの `Location` ヘッダー | `DECLARED` |
| `certificate` | ネゴシエートされた TLS 証明書の SAN（Subject Alternative Names） | `DECLARED` |
| `html_link` | ページが返すリンク（`<a href>`） | `INFERRED` |

`DECLARED` の値は、あくまでターゲットの自己申告（偽装可能）です — [§10](#10-偽装された値への対策) を参照。`html_link` は意図的に最も弱い出所にしています：単なるリンクは、インフラ上の関係を何も宣言していないからです。

### 安全上の制限（常に有効、無効にはできません）

- **範囲**：候補ターゲットは、ルートターゲットと同じ `/24` 内のプライベート IP でなければなりません。ただし `--subnet` を明示した場合は、指定したサブネットに属するかどうかだけが判断基準になります（公開 IP を含む場合でも — 例外を認めているのは明示的な設定そのものです）。名前解決されていないホスト名がこのフィルターを通ることはありません（確認のために名前解決することは、すでにこの確認の範囲を超えたネットワーク操作になるためです）。
- **深さ**：`--max-depth`（既定 3）— 最大で A → B → C → D。
- **ターゲット数**：`--max-targets`（既定 10）— すべての深さの合計。

### 承認（承認なしのスキャンは決してしない）

提案された各ターゲットは `PROPOSED → PRESENTED → ACCEPTED` または `REJECTED` をたどります。この規則は**フェイルセーフ**です：一度も明示的に承認されなかったターゲット（沈黙、画面を閉じる、中断、タイムアウト、TTY なし）はすべて却下として扱われます — その逆は決してありません。TUI では専用の画面に、まとまりごとのターゲットが根拠と信頼度とともに一覧され、行ごとの承認／却下の切り替え、「すべて承認」／「すべて却下」があり、Esc では既定ですべて却下されます。CLI ではターゲットごとに 1 つの質問。`--auto-validate`（非推奨）が対話を省略する唯一の方法です。

## 5. スキャンプロファイル

| プロファイル | 説明 | ピン留め |
|---|---|---|
| `minimal` | 超高速スキャン：SSH + HTTP + HTTPS（22、80、443） | はい |
| `classic` | 一般的なインターネット／LAN サービス | はい |
| `web` | Web サービスとその代替ポート | いいえ |
| `db` | データベースとデータサービス | いいえ |
| `remote` | リモートアクセス — シェル、デスクトップ、RustDesk | いいえ |
| `mail` | メールサービス | いいえ |
| `dns` | DNS サービス | いいえ |
| `iot` | IoT 機器、カメラ、ルーター、ホームオートメーション | いいえ |
| `dev` | 開発／検証環境 | いいえ |
| `docker` | Docker、Swarm、コンテナでよく使われるサービス | いいえ |
| `complet` | **その場で生成**：上記すべてのプロファイルを並べ替え、重複を除いた和集合 | いいえ |
| *個人プロファイル* | **プロファイル**画面（TUI）または `profile create`（CLI）で作成し、システムプロファイルと同じ場所に並び、TUI では先頭に `* ` が付きます | いいえ |

プロファイルはルートターゲット**と**承認された各発見ターゲットに適用されます — ホストごとに別のプロファイルを使うことはありません。完全な詳細、検証ルール、個人プロファイルの管理：`docs/PROFILES.md`。

## 6. アーキテクチャ

Omega-deep は **Clean Architecture**（domain / application / infrastructure / interfaces / ports / core / app / plugins / shared）で構成され、`omega-` スイートのテンプレート（`omega-scan`/`omega-check` を参照）に揃えてあり、変更のたびに `import-linter` で検証されます。完全な詳細は **`docs/ARCHITECTURE.md`** にあります。

ごく短い概要：

```text
src/omega_deep/
├── domain/          純粋な業務ロジック：スキャン、ターゲット、サービス、プロファイル、レポート、
│                    discovery（提案されたターゲット、承認の状態機械）、
│                    architecture（グラフ、関係の規則）
├── application/     ユースケース（commands/queries）— discover_targets、
│                    validate_targets、reconstruct_architecture を含む（omega-check に対して新規）
├── ports/           アプリケーションが期待する契約（プローブ、discovery_prober を含む、
│                    リポジトリ、エクスポーター...）
├── infrastructure/  具体的な実装（socket/httpx/cryptography、SQLite、
│                    グラフの SVG 描画 — Textual はここにはありません）
├── interfaces/      tui/（Textual）と cli/（スクリプト可能）、機能は厳密に同等
├── app/             組み立て（DependencyContainer、bootstrap、ライフサイクル）
├── core/, shared/   横断的な語彙、業務外のユーティリティ
└── plugins/         構造のみ用意、空（確定した拡張の方向性なし）
```

設計ルール：
- `domain/services/policies.py`：収集済みの手がかりを分類し、ネットワークには一切アクセスしません。
- `domain/discovery/policies.py`：範囲／深さ／数の安全上の制限 — ネットワークなしでテストできる純粋なロジック。
- `domain/architecture/service.py`：各 `Host` がすでに持っている由来からグラフを再構築し、新たなリクエストは行いません。
- `infrastructure/network/` と `infrastructure/discovery/`：ネットワークにアクセスし（ソケット、`httpx`、`cryptography`）、判断はしません。
- `interfaces/`：表示するだけで、業務ロジックは含みません — 発見ターゲットの承認画面は `validate_targets` を呼び出すだけで、フェイルセーフの規則を自前で実装してはいません。
- `infrastructure/exporters/`：解析結果（スキャン、ホスト、グラフ）を読むだけで、何も再計算しません。

## 7. サービスの特定と役割

### 検出するプロトコル

| プロトコル | プローブ | 収集する詳細 |
|---|---|---|
| HTTP / HTTPS | `httpx` | `Server` バナー、認証ヘッダー |
| TLS | `cryptography`（ネゴシエートされた証明書、`CERT_NONE` を含む） | バージョン、暗号スイート、証明書のサブジェクト／発行者 |
| SSH | 生のバナー | ソフトウェアとバージョン（例：`OpenSSH 10.4`） |
| VNC (RFB) | サーバーが提示するセキュリティコード | 対応している認証方式 |
| 汎用 | 認識できない開いたポートの生のバナー | 慎重な抽出、強引なヒューリスティックは使わない |

### 推定する役割

ポート番号による推測ではなく、**実際にネゴシエートされた**プロトコルから導きます：

| 役割 | 条件 | 信頼度 |
|---|---|---|
| `Web サーバー` | HTTP/HTTPS プロトコルを確認 | `INFERRED` |
| `シェルアクセス` | SSH プロトコルを確認 | `CORROBORATED` |
| `グラフィカルアクセス` | VNC プロトコルを確認 | `CORROBORATED` |
| `データベース` | ポートがシステムプロファイル `db` の範囲内 | `INFERRED` |

### 既知の WAF シグネチャ

宣言的なヘッダー（`server`、`x-sdk`）から検出します — 存在は**ターゲット自身が宣言したもの**で、独立した検証は行いません：Cloudflare、Sucuri、Akamai、Imperva Incapsula、AWS ELB（参考として掲載。厳密にはアプリケーション WAF ではありません）。

## 8. アーキテクチャのグラフ

承認された各ホストがすでに持っている由来（`discovered_from`/`discovery_source`/`discovery_confidence`）だけから再構築します — 新たなネットワークリクエストも、生の手がかりの再解析も行いません。

### 生成する関係

| 関係 | 発見の出所 | 意味 |
|---|---|---|
| `proxy_to` | `header` | ルートターゲット（または承認済みのホスト）が、発見したターゲットへのプロキシである可能性が高い |
| `redirect_to` | `redirection` | 発見したターゲットへの HTTP リダイレクトを観測 |
| `linked_to` | `certificate` または `html_link` | 最も中立的な関係 — 共有インフラ／アプリケーション。通信の向きは断定しない |

`backend_of`（`proxy_to` の逆向きの辺）は意図的に生成しません — それは情報の重複であって、新たな推論ではないからです。

### 表示

- **TUI**（解析の詳細）と **JSON／テキストのエクスポート**：辺の一覧（出所、関係、行き先、信頼度）— 端末は豊かなグラフィック表示をする場所ではありません。
- **HTML エクスポート**：**本物の SVG 図**（ノード = 円、辺 = ラベル付きの矢印）。ルートターゲットから階層状のレイアウトを計算し、サイズは発見したマシンの数に比例します — 重いグラフレイアウトのライブラリには依存しません。グラフは設計上、常に小さく保たれます（[§4](#4-ターゲットの発見と安全上の制限) の安全上の制限で抑えられるため）。

## 9. 信頼度ポリシー

収集した各フィールドには、次のいずれかのレベルが付きます：

| レベル | 意味 |
|---|---|
| `VERIFIED` | 直接観測したプロトコル上の事実で、ターゲットが偽装できないもの（例：TCP RST で確認した閉じたポート、実際にネゴシエートされた TLS バージョン）。 |
| `DECLARED` | ターゲットが完全に制御するフィールドで自ら名乗った値（例：`Server` バナー、`X-Backend-Server` ヘッダー）— もっともらしいが、自由に偽装できる。 |
| `CORROBORATED` | 独立した手がかりによって裏付けられた `DECLARED` の値（例：SSH の役割。プロトコルが実際にネゴシエートされているため）。 |
| `INFERRED` | ターゲットによる明示的な宣言なしに、パターンやヒューリスティックから推定したもの（例：HTML リンク）。 |
| `UNKNOWN` | 使える手がかりがない、またはターゲットが意図的に隠している。 |

## 10. 偽装された値への対策

Omega-deep は、ターゲットが自ら宣言したデータを、そのことを明示せずに信用することはありません — そしてターゲットの発見は、このプロジェクトで最も繊細な部分です：悪意のあるターゲットは、偽の `X-Backend-Server` を名乗り、自分の選んだ IP へ発見を誘導*しうる*からです。互いに独立した 2 つの構造的な防御があります：
- ターゲットから得た情報は、宣言されたというだけで `VERIFIED` になることは決してありません — `Server` バナーや `X-Backend-Server` ヘッダーは、どれほどもっともらしくても `DECLARED` のままです。
- 範囲の制限（[§4](#4-ターゲットの発見と安全上の制限)）は、宣言されたターゲットがどこまで誘導できるかを抑え（明示的な設定がない限り同じプライベート `/24`）、ユーザーの承認はそもそもスキャンするかどうかを決めます — 範囲外の偽ターゲットは提案すらされず、範囲内のターゲットもスキャンの前には必ず明示的な承認が必要です。

## 11. 端末との互換性

TUI（Textual）は端末の能力（エミュレーター、サイズ）を自動的に検出し、それに合わせて構造スタイルシート（`complete`/`standard`/`reduced`/`mono`）を調整します。手動の指定は不要です。CLI モードは常にプレーンテキストで、端末に依存しません。この方針は `omega-` スイート全体で共通です（`omega-lib`、`terminal/policies.py`）。

### 検出したエミュレーターによるプロファイル

| エミュレーター | 初期プロファイル |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm、urxvt、最近の SSH | `reduced` |
| Linux TTY、古い SSH | `mono` |
| 認識できないエミュレーター | `reduced`（既定の代替） |

### 端末サイズによるプロファイル

| 最小サイズ（列 × 行） | プロファイルの上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| それ未満 | `mono` |

最終的なプロファイルは**両者のうち制限の厳しい方**（エミュレーターとサイズ）です — 全画面の Ghostty を 70 列に縮めると、エミュレーターとしては `complete` が可能でも `mono` に下がります。`r` キーでその場で更新できます。

## 12. エクスポート

テキストと HTML のレポートは、設定で選んだ言語で書かれます（「エクスポートの言語」、既定はインターフェースと同じ）。JSON はデータのままで翻訳されません。レポートは既定で `var/exports/` に生成されます（実行時のパスはプロジェクトフォルダーに固定、`$OMEGA_DEEP_VAR_DIR` で変更可能）。または指定したパス（CLI では `--output`、TUI ではダイアログ）に生成されます。わかりやすいタイムスタンプ付きのファイル名：`analyse-{プロファイル}-{日付}.ext`、個人プロファイルでは `analyse-custom-{日付}.ext`。

### JSON、正となる情報源

解析の完全な構造（`Scan` + `Host[]` + `ArchitectureGraph`）、厳密に JSON シリアライズ可能で、信頼度も含みます。

### テキスト、コンパクトで読みやすいレポート

端末の外でも読めて、ANSI コードを含みません — グラフは辺の一覧として示します。

### HTML、単体で完結する Web レポート

5 種類のテーマから選択（CLI では `--theme`、TUI ではセレクター。対応するものがあれば、既定で現在のインターフェースのテーマに従います）。専用のレイアウト：コンテナー、情報グリッド、ポート状態ごとの統計ボックス、色付きバッジ、**アーキテクチャのグラフの SVG 図**（[§8](#8-アーキテクチャのグラフ) を参照）— `omega-scan`/`omega-check` と同じ見た目の系統です。

## 13. 履歴と比較

各解析は保存されます（SQLite、`var/db/omega-deep.db`）：1 つの `scan_id` に、ルートターゲット**と**発見／承認したすべてのホスト、さらに再構築したグラフが含まれます。ルートターゲットごとの履歴（発見したターゲット数の専用列あり）、過去の解析の詳細（ホスト + グラフ）、2 つの解析の比較（**ルートターゲット**のポート状態のみ — 発見グラフの比較は将来の拡張としてありうるものの、現時点では不要）、同じルートターゲットに対する再入力なしの再実行ができます。

## 14. テスト

```bash
source .venv/bin/activate
lint-imports        # Dependency Rule をチェック
pytest -q           # 191 件のテスト
ruff check src tests
mypy -p omega_deep
```

構成：`tests/unit/`（実際の I/O を伴わないドメインとアプリケーション）、`tests/integration/`（実際の SQLite／ファイル、模擬 HTTP サーバー `pytest-httpserver`、`trustme` による TLS）、`tests/tui/`（`Pilot` によるナビゲーション、構造的 — 視覚的な検証をしたとは主張しない）。

## 15. 範囲外

- CVE スキャン
- SQLi、XSS、RCE の能動的な検出
- OS のフィンガープリント
- nmap 風の低レベルなスキャン技法（SYN スキャン、生パケット）
- クロール
- ファジング
- 総当たり攻撃
- 明示的な承認なしに発見したターゲットをスキャンすること — どのモードでも決して行わない
- 明示的な設定なしに、最初のターゲットのプライベートサブネットの外で発見を行うこと
- Web ダッシュボード

---

> Omega-deep — 発見し、地図にし、評価し、報告する。
> 信頼度を明示して再構築したアーキテクチャ。事実を装った推測では決してありません。
