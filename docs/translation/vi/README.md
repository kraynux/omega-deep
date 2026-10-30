<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Giấy phép MIT (xem tệp LICENSE) -->
<div align="center">
  <img src="../../assets/omega-deep.png" alt="Omega-Deep" width="384">
</div>

# 🖧 OMEGA-DEEP

**Phân tích kiến trúc nhiều mục tiêu (khám phá + giới hạn an toàn + đồ thị)**

> Được **kraynux** xây dựng cho **Omega-server** 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Trang chính thức: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Ảnh chụp màn hình: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Giao diện và báo cáo xuất có sẵn bằng **17 ngôn ngữ** — xem [Ngôn ngữ giao diện](#ngôn-ngữ-giao-diện).  
**Ngôn ngữ:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** làm được mọi việc `omega-check` làm trên một mục tiêu duy nhất (quét cổng, nhận diện dịch vụ, vai trò, WAF, TLS) và bổ sung thêm **khám phá các mục tiêu khác** từ những dấu hiệu mà mục tiêu đã quét để lại (tiêu đề, chuyển hướng, chứng chỉ, liên kết HTML), dưới **các giới hạn an toàn nghiêm ngặt** và một **xác nhận rõ ràng của người dùng** trước khi quét bất kỳ mục tiêu nào được khám phá, rồi **dựng lại một đồ thị kiến trúc** (ai nói chuyện với ai, với độ tin cậy nào). Đây là một công cụ của bộ `omega-`, được tổ chức theo Clean Architecture — xem `docs/ARCHITECTURE.md` để biết đầy đủ chi tiết kỹ thuật.

## 1. Tầm nhìn và phạm vi

Omega-deep trả lời một câu hỏi mà omega-check không đặt ra: *đằng sau địa chỉ IP này còn có gì nữa?* Một reverse proxy công bố máy chủ phía sau, một chứng chỉ bao phủ nhiều máy, một trang trỏ tới một dịch vụ bên cạnh — đó đều là những dấu hiệu mà omega-deep lần theo, một cách thận trọng và không bao giờ tự ý.

### Omega-deep làm gì

- Quét một mục tiêu gốc giống hệt omega-check (cấu hình hệ thống hoặc cấu hình cá nhân đã lưu).
- Khám phá các mục tiêu ứng viên từ dấu hiệu mà mỗi máy đã quét để lại: tiêu đề HTTP (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), chuyển hướng (`Location`), chứng chỉ TLS (SAN), liên kết HTML — xem [§4](#4-khám-phá-mục-tiêu-và-giới-hạn-an-toàn).
- **Không bao giờ** quét một mục tiêu được khám phá mà không có xác nhận rõ ràng, từng mục tiêu một — im lặng không bao giờ là đồng ý.
- Giới hạn việc khám phá bằng các giới hạn an toàn nghiêm ngặt: độ sâu tối đa, số mục tiêu bổ sung tối đa, mạng con được phép (mặc định cùng dải riêng với mục tiêu gốc).
- Dựng lại một **đồ thị kiến trúc** từ nguồn gốc của mỗi mục tiêu được chấp nhận (`proxy_to`, `redirect_to`, `linked_to`), kèm độ tin cậy cho từng quan hệ — xem [§8](#8-đồ-thị-kiến-trúc).
- Hiển thị kết quả trong TUI (Textual) hoặc CLI có thể viết script, với cùng ba kiểu xuất như omega-check (JSON, văn bản, HTML với 5 giao diện màu) — ở đó đồ thị là một **sơ đồ được vẽ thật sự** bằng HTML, không phải một bảng.
- Gán cho mỗi thông tin thu thập (về dịch vụ hay về khám phá) một mức độ tin cậy rõ ràng — xem [§9](#9-chính-sách-tin-cậy).
- Lưu lịch sử phân tích lâu dài, có thể chạy lại và so sánh theo thời gian.

### Omega-deep không làm gì

- Quét lỗ hổng chủ động: không SQLi, XSS hay RCE.
- Quét CVE.
- Nhận diện hệ điều hành.
- Kỹ thuật quét cấp thấp kiểu nmap (quét SYN, gói tin thô) — chỉ kết nối TCP ở tầng ứng dụng.
- Công cụ dò mật khẩu hay fuzzing.
- Quét một mục tiêu được khám phá mà không có xác nhận rõ ràng của người dùng — không bao giờ, ở bất kỳ chế độ nào.
- Khám phá ra ngoài mạng con riêng của mục tiêu ban đầu, trừ khi được cấu hình rõ ràng (`--subnet`).
- Bảng điều khiển web.

## 2. Cài đặt

### Yêu cầu

- Python 3.10+
- Kết nối Internet, để cài các phụ thuộc

### Cài đặt

```bash
[ -d omega-deep ] && echo "ℹ️ Đã giải nén ở đây, bỏ qua bước này." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Tạo môi trường ảo `.venv` nếu chưa có.
2. Cài các phụ thuộc (`vendor/omega-lib/` rồi `pip install -e .`; `pyproject.toml` vẫn là nguồn chuẩn duy nhất).
3. Cấp quyền thực thi cho `omega-deep.sh` và `install.sh`.
4. Thêm bí danh `deep` vào `~/.bashrc` và `~/.zshrc` (không trùng lặp nếu đã có).

### Phụ thuộc

Khai báo trong `pyproject.toml` (không còn `requirements.txt`):
- `omega-lib`: thư viện dùng chung của bộ công cụ (`ConfidenceLevel`, giao diện màu, nhận diện terminal) — đi kèm trong `vendor/omega-lib/`
- `textual`: giao diện TUI, giao diện màu, tự động thích ứng với terminal
- `httpx`: thăm dò HTTP/HTTPS (dịch vụ và khám phá)
- `cryptography`: đọc chứng chỉ TLS đã thương lượng
- `jinja2`: mẫu cho bản xuất HTML
- Phụ thuộc phát triển (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Sử dụng

### Chế độ tương tác (TUI)

Khuyên dùng hằng ngày — chạy không có đối số:

```bash
./omega-deep.sh
```
nếu đã tạo bí danh, chỉ cần gõ `deep` trong terminal:
```bash
deep
```

Trình tự: màn hình khởi động (đóng bằng một phím hoặc một cú nhấp) → menu chính (Phân tích / Cấu hình / Lịch sử / Thiết lập / Trợ giúp) → nhập mục tiêu gốc, chọn cấu hình và các giới hạn an toàn khi khám phá (độ sâu tối đa, số mục tiêu tối đa, mạng con được phép) → phân tích (thanh tiến trình không xác định và nhật ký thao tác mạng trực tiếp) → với mỗi đợt mục tiêu được khám phá, một màn hình xác nhận (mỗi mục tiêu một dòng, hiển thị nguồn/độ tin cậy/bằng chứng, nút chuyển chấp nhận/từ chối — mặc định không chọn gì) → chi tiết phân tích (máy, cổng/dịch vụ/vai trò, đồ thị, xuất) → lịch sử/so sánh/chạy lại và thiết lập từ menu chính. Việc thích ứng với terminal (màu, kích thước, giản lược cấu trúc) là tự động.

#### Phím tắt

| Phím | Thao tác |
|---|---|
| `↑` / `↓` | Di chuyển giữa các mục trên màn hình |
| `Tab` / `Shift+Tab` | Di chuyển giữa các trường của biểu mẫu |
| `Esc` | Quay lại màn hình trước (xác nhận thoát ở màn hình chính) |
| `t` | Giao diện màu tiếp theo (áp dụng ngay, không cần xác nhận) |
| `r` | Làm mới việc nhận diện terminal |
| `a` | Hiện trợ giúp |
| `q` | Thoát (có xác nhận) |

### Ngôn ngữ giao diện

Giao diện có sẵn bằng 17 ngôn ngữ: tiếng Pháp, tiếng Anh, tiếng Tây Ban Nha, tiếng Bồ Đào Nha (Brasil), tiếng Ý, tiếng Đức, tiếng Hà Lan, tiếng Ba Lan, tiếng Nga, tiếng Trung giản thể, tiếng Việt, tiếng Thái, tiếng Indonesia, tiếng Nhật, tiếng Hàn, tiếng Hindi và tiếng Ả Rập. Ngôn ngữ được chọn trong Thiết lập (“Langue / Language”) và có hiệu lực sau khi khởi động lại giao diện; biến `OMEGA_DEEP_LANG` (ví dụ `OMEGA_DEEP_LANG=vi ./omega-deep.sh`) buộc dùng một ngôn ngữ trong một phiên. Khi được chạy từ omega-suite, omega-deep dùng ngôn ngữ của bộ công cụ. Trên console văn bản Linux (TTY), giao diện hiển thị bằng tiếng Anh trong phiên đó đối với tiếng Việt và các ngôn ngữ không dùng chữ Latinh. Dòng lệnh vẫn bằng tiếng Pháp.

### Chế độ script (CLI)

Bất kỳ lệnh con nào cũng kích hoạt chế độ CLI:

```bash
# Phân tích một mục tiêu (quét mục tiêu gốc + khám phá nhiều mục tiêu)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Lịch sử (lọc được theo mục tiêu gốc)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Chi tiết một lần phân tích (văn bản, JSON hoặc HTML) — chọn 1 trong 5 giao diện xuất
./omega-deep.sh show <scan_id> --format html --theme omega-base --output baocao.html

# So sánh hai lần phân tích (trạng thái cổng của mục tiêu gốc)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Cấu hình cổng cá nhân
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "Cấu hình của tôi"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

Trong CLI, các mục tiêu được khám phá được xác nhận qua một câu hỏi tương tác cho mỗi mục tiêu (`Scanner <cible> ? [o/N]`, bằng tiếng Pháp như phần còn lại của dòng lệnh), kèm chi tiết bằng chứng hiển thị trước mỗi câu hỏi. `--auto-validate` chấp nhận tất cả mà không xem xét (**không khuyến khích**, có hiện cảnh báo); trong môi trường không tương tác (không có TTY, không có `--auto-validate`), mọi mục tiêu được khám phá đều bị từ chối theo mặc định thay vì bị quét khi chưa được xác nhận.

### Định dạng mục tiêu được chấp nhận

```text
192.168.1.10                IPv4
example.org                 Tên máy chủ
http://example.org          URL HTTP  (bỏ giao thức trước khi phân giải)
https://example.org:8443    URL HTTPS có cổng  (bỏ giao thức và cổng)
```

Giao thức và cổng (nếu có) được bỏ đi trước khi phân giải DNS (`domain/targets/validation.py::normalize_target_input`) — dán nguyên một URL vẫn được, chỉ giữ lại máy chủ. Các mục tiêu *được khám phá* cũng được chuẩn hóa theo cách đó, nhưng không bao giờ bị quét khi chưa được xác nhận (xem [§4](#4-khám-phá-mục-tiêu-và-giới-hạn-an-toàn)).

## 4. Khám phá mục tiêu và giới hạn an toàn

### Nguồn dấu hiệu

| Nguồn | Xuất xứ | Độ tin cậy |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | Tiêu đề `Location` của một phản hồi HTTP | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) của chứng chỉ TLS đã thương lượng | `DECLARED` |
| `html_link` | Các liên kết (`<a href>`) do trang cung cấp | `INFERRED` |

Một giá trị `DECLARED` vẫn chỉ là lời tự khai của mục tiêu (có thể giả mạo) — xem [§10](#10-bảo-vệ-trước-giá-trị-giả-mạo). `html_link` được cố ý đặt là nguồn yếu nhất: một liên kết đơn thuần không khai báo quan hệ hạ tầng nào.

### Giới hạn an toàn (luôn bật, không bao giờ tắt được)

- **Phạm vi**: một mục tiêu ứng viên phải là IP riêng nằm cùng `/24` với mục tiêu gốc, trừ khi có `--subnet` rõ ràng (khi đó chỉ xét việc thuộc mạng con đã cho, kể cả khi nó bao gồm IP công khai — chính cấu hình rõ ràng cho phép ngoại lệ này). Một tên máy chủ chưa được phân giải không bao giờ được bộ lọc này chấp nhận (phân giải nó để kiểm tra đã là một thao tác mạng nằm ngoài phạm vi của bước kiểm tra này).
- **Độ sâu**: `--max-depth` (mặc định 3) — tối đa A → B → C → D.
- **Số mục tiêu**: `--max-targets` (mặc định 10) — tính trên mọi độ sâu.

### Xác nhận (không bao giờ quét khi chưa được đồng ý)

Mỗi mục tiêu được đề xuất đi qua `PROPOSED → PRESENTED → ACCEPTED` hoặc `REJECTED`. Quy tắc là **an toàn khi có sự cố**: mọi mục tiêu chưa từng được chấp nhận rõ ràng (im lặng, đóng màn hình, gián đoạn, hết thời gian chờ, không có TTY) đều bị coi là bị từ chối — không bao giờ ngược lại. Trong TUI, một màn hình riêng liệt kê các mục tiêu của một đợt kèm bằng chứng và độ tin cậy, nút chuyển chấp nhận/từ chối trên mỗi dòng, “chấp nhận tất cả”/“từ chối tất cả”, và mặc định từ chối toàn bộ khi nhấn Esc. Trong CLI, mỗi mục tiêu một câu hỏi; `--auto-validate` (không khuyến khích) là cách duy nhất để bỏ qua tính tương tác.

## 5. Cấu hình quét

| Cấu hình | Mô tả | Đã ghim |
|---|---|---|
| `minimal` | Quét siêu nhanh: SSH + HTTP + HTTPS (22, 80, 443) | có |
| `classic` | Dịch vụ Internet/LAN thông dụng | có |
| `web` | Dịch vụ web và cổng thay thế | không |
| `db` | Cơ sở dữ liệu và dịch vụ dữ liệu | không |
| `remote` | Truy cập từ xa — shell, màn hình, RustDesk | không |
| `mail` | Dịch vụ thư | không |
| `dns` | Dịch vụ DNS | không |
| `iot` | Thiết bị IoT, camera, bộ định tuyến, nhà thông minh | không |
| `dev` | Môi trường phát triển/thử nghiệm | không |
| `docker` | Docker, Swarm và các dịch vụ thường chạy trong container | không |
| `complet` | **Tạo tức thì**: hợp đã sắp xếp và loại trùng của mọi cấu hình ở trên | không |
| *cấu hình cá nhân* | Tạo trong màn hình **Cấu hình** (TUI) hoặc bằng `profile create` (CLI), liệt kê cùng chỗ với các cấu hình hệ thống, có tiền tố `* ` trong TUI | không |

Cấu hình áp dụng cho mục tiêu gốc **và** cho từng mục tiêu được khám phá đã được chấp nhận — không có cấu hình riêng cho từng máy. Chi tiết đầy đủ, quy tắc kiểm tra và quản lý cấu hình cá nhân: `docs/PROFILES.md`.

## 6. Kiến trúc

Omega-deep được tổ chức theo **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), thống nhất với mẫu của bộ `omega-` (xem `omega-scan`/`omega-check`) và được `import-linter` kiểm tra ở mỗi thay đổi. Chi tiết đầy đủ nằm trong **`docs/ARCHITECTURE.md`**.

Tổng quan rất ngắn:

```text
src/omega_deep/
├── domain/          Logic nghiệp vụ thuần: quét, mục tiêu, dịch vụ, cấu hình, báo cáo,
│                    discovery (mục tiêu đề xuất, máy trạng thái xác nhận),
│                    architecture (đồ thị, quy tắc quan hệ)
├── application/     Ca sử dụng (commands/queries) — trong đó có discover_targets,
│                    validate_targets, reconstruct_architecture (mới so với omega-check)
├── ports/           Hợp đồng mà ứng dụng cần (bộ thăm dò, trong đó có discovery_prober,
│                    kho lưu trữ, bộ xuất...)
├── infrastructure/  Triển khai cụ thể (socket/httpx/cryptography, SQLite,
│                    vẽ đồ thị bằng SVG — Textual KHÔNG nằm ở đây)
├── interfaces/      tui/ (Textual) và cli/ (viết script được), tương đương chức năng nghiêm ngặt
├── app/             Lắp ráp (DependencyContainer, bootstrap, vòng đời)
├── core/, shared/   Từ vựng dùng chung, tiện ích không thuộc nghiệp vụ
└── plugins/         Đã có cấu trúc, đang trống (chưa có hướng mở rộng nào được xác nhận)
```

Quy tắc thiết kế:
- `domain/services/policies.py`: phân loại các dấu hiệu đã thu thập, không bao giờ truy cập mạng.
- `domain/discovery/policies.py`: giới hạn an toàn về phạm vi/độ sâu/số lượng — logic thuần, kiểm thử được mà không cần mạng.
- `domain/architecture/service.py`: dựng lại đồ thị từ nguồn gốc mà mỗi `Host` đã mang sẵn, không gửi lại yêu cầu nào.
- `infrastructure/network/` và `infrastructure/discovery/`: truy cập mạng (socket, `httpx`, `cryptography`), không bao giờ đánh giá.
- `interfaces/`: hiển thị, không chứa logic nghiệp vụ nào — màn hình xác nhận mục tiêu được khám phá gọi `validate_targets`, nó không tự thực hiện quy tắc an toàn khi có sự cố.
- `infrastructure/exporters/`: đọc kết quả phân tích (quét, máy, đồ thị), không tính lại gì cả.

## 7. Nhận diện dịch vụ và vai trò

### Giao thức được phát hiện

| Giao thức | Cách thăm dò | Chi tiết thu thập |
|---|---|---|
| HTTP / HTTPS | `httpx` | Banner `Server`, tiêu đề xác thực |
| TLS | `cryptography` (chứng chỉ đã thương lượng, kể cả `CERT_NONE`) | Phiên bản, bộ mã hóa, chủ thể/bên cấp chứng chỉ |
| SSH | Banner thô | Phần mềm và phiên bản (ví dụ `OpenSSH 10.4`) |
| VNC (RFB) | Mã bảo mật do máy chủ công bố | Các kiểu xác thực được hỗ trợ |
| Chung | Banner thô trên cổng mở không nhận diện được | Trích xuất thận trọng, không dùng suy đoán mạnh tay |

### Vai trò được suy ra

Suy ra từ giao thức **thực sự được thương lượng**, không bao giờ từ phỏng đoán theo số cổng:

| Vai trò | Điều kiện | Độ tin cậy |
|---|---|---|
| `máy chủ web` | Đã xác nhận giao thức HTTP/HTTPS | `INFERRED` |
| `truy cập shell` | Đã xác nhận giao thức SSH | `CORROBORATED` |
| `truy cập đồ họa` | Đã xác nhận giao thức VNC | `CORROBORATED` |
| `cơ sở dữ liệu` | Cổng nằm trong dải của cấu hình hệ thống `db` | `INFERRED` |

### Chữ ký WAF đã biết

Phát hiện qua một tiêu đề khai báo (`server`, `x-sdk`) — sự hiện diện **do mục tiêu tự khai báo**, không bao giờ được xác minh độc lập: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (liệt kê để tham khảo, thực ra không hẳn là WAF ứng dụng).

## 8. Đồ thị kiến trúc

Chỉ được dựng lại từ nguồn gốc mà mỗi máy được chấp nhận đã mang sẵn (`discovered_from`/`discovery_source`/`discovery_confidence`) — không có yêu cầu mạng mới, không phân tích lại các dấu hiệu thô.

### Các quan hệ được tạo

| Quan hệ | Nguồn khám phá | Ý nghĩa |
|---|---|---|
| `proxy_to` | `header` | Mục tiêu gốc (hoặc một máy đã được chấp nhận) nhiều khả năng là proxy tới mục tiêu được khám phá |
| `redirect_to` | `redirection` | Đã quan sát thấy chuyển hướng HTTP tới mục tiêu được khám phá |
| `linked_to` | `certificate` hoặc `html_link` | Quan hệ trung lập nhất — hạ tầng/ứng dụng dùng chung, không khẳng định hướng luồng |

`backend_of` (cạnh ngược của một `proxy_to`) được cố ý không tạo ra — đó sẽ là thông tin trùng lặp, không phải một suy luận mới.

### Cách hiển thị

- **TUI** (chi tiết một lần phân tích) và **bản xuất JSON/văn bản**: danh sách các cạnh (nguồn, quan hệ, đích, độ tin cậy) — terminal không phải nơi dành cho hiển thị đồ họa phong phú.
- **Bản xuất HTML**: một **sơ đồ SVG thật sự** (nút = hình tròn, cạnh = mũi tên có nhãn), bố cục theo tầng tính từ mục tiêu gốc, kích thước tỉ lệ với số máy được khám phá — không bao giờ dùng thư viện bố cục đồ thị nặng nề; theo thiết kế, đồ thị luôn nhỏ (bị giới hạn bởi các giới hạn an toàn ở [§4](#4-khám-phá-mục-tiêu-và-giới-hạn-an-toàn)).

## 9. Chính sách tin cậy

Mỗi trường thu thập mang một trong các mức sau:

| Mức | Ý nghĩa |
|---|---|
| `VERIFIED` | Sự kiện giao thức quan sát trực tiếp, mục tiêu không thể giả mạo (ví dụ: cổng đóng được xác nhận bằng TCP RST, phiên bản TLS thực sự được thương lượng). |
| `DECLARED` | Giá trị do mục tiêu tự công bố trong một trường mà nó hoàn toàn kiểm soát (ví dụ: banner `Server`, tiêu đề `X-Backend-Server`) — có vẻ hợp lý nhưng có thể giả mạo tùy ý. |
| `CORROBORATED` | Một giá trị `DECLARED` được xác nhận bởi một dấu hiệu độc lập (ví dụ: vai trò SSH, vì giao thức đã thực sự được thương lượng). |
| `INFERRED` | Suy ra từ một mẫu/quy tắc suy đoán, không có khai báo rõ ràng từ mục tiêu (ví dụ: liên kết HTML). |
| `UNKNOWN` | Không có dấu hiệu dùng được, hoặc bị mục tiêu chủ động che giấu. |

## 10. Bảo vệ trước giá trị giả mạo

Omega-deep không tin bất kỳ dữ liệu nào do mục tiêu tự khai báo mà không đánh dấu rõ điều đó — và khám phá mục tiêu là phần nhạy cảm nhất của dự án: một mục tiêu độc hại *có thể* công bố một `X-Backend-Server` giả để dẫn việc khám phá tới một IP do nó chọn. Có hai lớp bảo vệ mang tính cấu trúc, độc lập với nhau:
- Không thông tin nào lấy từ một mục tiêu lại trở thành `VERIFIED` chỉ vì được công bố — một banner `Server` hay tiêu đề `X-Backend-Server` vẫn là `DECLARED`, dù có vẻ hợp lý đến đâu.
- Giới hạn phạm vi ([§4](#4-khám-phá-mục-tiêu-và-giới-hạn-an-toàn)) khống chế nơi mà một mục tiêu được công bố có thể dẫn tới (cùng `/24` riêng, trừ khi cấu hình rõ ràng), và sự xác nhận của người dùng quyết định nó có bị quét hay không — một mục tiêu giả nằm ngoài phạm vi thậm chí không bao giờ được đề xuất; một mục tiêu trong phạm vi vẫn phải được xác nhận rõ ràng trước mọi lần quét.

## 11. Tương thích terminal

TUI (Textual) tự động nhận diện khả năng của terminal (trình giả lập, kích thước) và điều chỉnh bảng kiểu cấu trúc tương ứng (`complete`/`standard`/`reduced`/`mono`), không cần tùy chọn thủ công. Chế độ CLI luôn là văn bản thuần, không phụ thuộc terminal. Đây là chính sách chung của toàn bộ `omega-` (`omega-lib`, `terminal/policies.py`).

### Cấu hình theo trình giả lập được nhận diện

| Trình giả lập | Cấu hình ban đầu |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH hiện đại | `reduced` |
| TTY Linux, SSH cũ | `mono` |
| Trình giả lập không nhận diện được | `reduced` (dự phòng mặc định) |

### Cấu hình theo kích thước terminal

| Kích thước tối thiểu (cột × dòng) | Mức trần cấu hình |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| nhỏ hơn | `mono` |

Cấu hình cuối cùng là **cấu hình hạn chế hơn trong hai** (trình giả lập và kích thước) — một Ghostty toàn màn hình bị thu nhỏ còn 70 cột sẽ hạ xuống `mono`, dù trình giả lập cho phép `complete`. Có thể làm mới trực tiếp bằng phím `r`.

## 12. Xuất

Báo cáo văn bản và HTML được viết bằng ngôn ngữ chọn trong Thiết lập (“Ngôn ngữ bản xuất”, mặc định là ngôn ngữ giao diện); JSON vẫn là dữ liệu, không được dịch. Báo cáo được tạo mặc định trong `var/exports/` (đường dẫn khi chạy gắn với thư mục dự án, dùng `$OMEGA_DEEP_VAR_DIR` để thay đổi), hoặc tại đường dẫn được chỉ định (`--output` trong CLI, hộp thoại trong TUI). Tên tệp rõ ràng, có dấu thời gian: `analyse-{cấu-hình}-{ngày}.ext`, `analyse-custom-{ngày}.ext` cho cấu hình cá nhân.

### JSON, nguồn chuẩn

Toàn bộ cấu trúc của lần phân tích (`Scan` + `Host[]` + `ArchitectureGraph`), tuần tự hóa JSON nghiêm ngặt, kèm các mức tin cậy.

### Văn bản, báo cáo dễ đọc gọn nhẹ

Đọc được ngoài terminal, không có mã ANSI — đồ thị ở dạng danh sách cạnh.

### HTML, báo cáo web độc lập

5 giao diện màu để chọn (`--theme` trong CLI, bộ chọn trong TUI; mặc định theo giao diện đang dùng nếu có tương đương). Bố cục riêng: khung chứa, lưới thông tin, ô thống kê theo trạng thái cổng, nhãn màu, **sơ đồ SVG của đồ thị kiến trúc** (xem [§8](#8-đồ-thị-kiến-trúc)) — cùng phong cách với `omega-scan`/`omega-check`.

## 13. Lịch sử và so sánh

Mỗi lần phân tích đều được lưu (SQLite, `var/db/omega-deep.db`): một `scan_id` chứa mục tiêu gốc **và** mọi máy được khám phá/chấp nhận, cùng với đồ thị đã dựng lại. Xem lịch sử theo mục tiêu gốc (có một cột riêng cho số mục tiêu được khám phá), chi tiết một lần phân tích trước (máy + đồ thị), so sánh hai lần phân tích (chỉ trạng thái cổng của **mục tiêu gốc** — so sánh các đồ thị khám phá là một hướng mở rộng khả thi, hiện chưa cần), và chạy lại một lần phân tích trên cùng mục tiêu gốc mà không cần nhập lại.

## 14. Kiểm thử

```bash
source .venv/bin/activate
lint-imports        # kiểm tra Dependency Rule
pytest -q           # 191 bài kiểm thử
ruff check src tests
mypy -p omega_deep
```

Cấu trúc: `tests/unit/` (domain và ứng dụng, không có I/O thật), `tests/integration/` (SQLite/tệp thật, máy chủ HTTP giả `pytest-httpserver`, TLS qua `trustme`), `tests/tui/` (điều hướng qua `Pilot`, mang tính cấu trúc — không tự nhận đã kiểm tra hình ảnh).

## 15. Ngoài phạm vi

- Quét CVE
- Phát hiện chủ động SQLi, XSS, RCE
- Nhận diện hệ điều hành
- Kỹ thuật quét cấp thấp kiểu nmap (quét SYN, gói tin thô)
- Thu thập trang (crawling)
- Fuzzing
- Dò mật khẩu
- Quét một mục tiêu được khám phá mà không có xác nhận rõ ràng — không bao giờ, ở bất kỳ chế độ nào
- Khám phá ra ngoài mạng con riêng của mục tiêu ban đầu khi không có cấu hình rõ ràng
- Bảng điều khiển web

---

> Omega-deep — Khám phá, lập bản đồ, đánh giá, báo cáo.
> Một kiến trúc được dựng lại với độ tin cậy rõ ràng, không bao giờ là phỏng đoán đội lốt sự thật.
