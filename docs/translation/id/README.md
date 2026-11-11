<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Lisensi MIT (lihat berkas LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-deep.png" alt="Omega-Deep" width="512">
</div>

# 🖧 OMEGA-DEEP

**Analisis arsitektur multi-target (penemuan + pengaman + graf)**

> Dibuat oleh [kraynux](https://github.com/kraynux) untuk [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Halaman resmi: [OMEGA-DEEP](https://kraynux.snake-mackarel.ts.net/omega-deep/) &nbsp; Pratinjau: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-deep/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Antarmuka dan laporan ekspor tersedia dalam **17 bahasa** — lihat [Bahasa antarmuka](#bahasa-antarmuka).  
**Bahasa:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-deep** melakukan semua yang dilakukan `omega-check` pada satu target (pemindaian port, pengenalan layanan, peran, WAF, TLS) dan menambahkan **penemuan target tambahan** dari petunjuk yang ditinggalkan target yang sudah dipindai (header, pengalihan, sertifikat, tautan HTML), di bawah **pengaman yang ketat** dan **validasi eksplisit oleh pengguna** sebelum target temuan mana pun dipindai, lalu **merekonstruksi graf arsitektur** (siapa berbicara dengan siapa, dengan tingkat keyakinan apa). Alat dari rangkaian `omega-`, disusun dengan Clean Architecture — lihat `docs/ARCHITECTURE.md` untuk detail teknis lengkap.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-deep/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-deep/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-deep/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-deep/D.png" width="24%" />
</p>

## 1. Visi dan cakupan

Omega-deep menjawab pertanyaan yang tidak diajukan omega-check: *di balik IP ini, apa lagi yang ada?* Reverse proxy yang mengumumkan backend-nya, sertifikat yang mencakup beberapa host, halaman yang menunjuk ke layanan di sebelahnya — semuanya petunjuk yang diikuti omega-deep dengan hati-hati, tidak pernah atas kehendaknya sendiri.

### Yang dilakukan Omega-deep

- Memindai target akar persis seperti omega-check (profil sistem atau profil pribadi yang tersimpan).
- Menemukan calon target dari petunjuk yang ditinggalkan setiap host yang sudah dipindai: header HTTP (`X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via`), pengalihan (`Location`), sertifikat TLS (SAN), tautan HTML — lihat [§4](#4-penemuan-target-dan-pengaman).
- **Tidak pernah** memindai target temuan tanpa validasi eksplisit, satu per satu — diam tidak pernah berarti setuju.
- Membatasi penemuan dengan pengaman yang ketat: kedalaman maksimum, jumlah maksimum target tambahan, subnet yang diizinkan (secara bawaan rentang privat yang sama dengan target akar).
- Merekonstruksi **graf arsitektur** dari asal-usul setiap target yang diterima (`proxy_to`, `redirect_to`, `linked_to`), dengan tingkat keyakinan per relasi — lihat [§8](#8-graf-arsitektur).
- Menampilkan hasil di TUI (Textual) atau CLI untuk skrip, dengan tiga ekspor yang sama seperti omega-check (JSON, teks, HTML dengan 5 tema) — di sana grafnya adalah **diagram yang benar-benar digambar** dalam HTML, bukan tabel.
- Memberi setiap informasi yang terkumpul (layanan maupun penemuan) tingkat keyakinan yang jelas — lihat [§9](#9-kebijakan-keyakinan).
- Menyimpan riwayat analisis permanen yang dapat diulang dan dibandingkan dari waktu ke waktu.

### Yang tidak dilakukan Omega-deep

- Pemindaian kerentanan aktif: tanpa SQLi, XSS, atau RCE.
- Pemindaian CVE.
- Pengenalan sistem operasi.
- Teknik pemindaian tingkat rendah ala nmap (SYN scan, paket mentah) — hanya koneksi TCP tingkat aplikasi.
- Alat brute force atau fuzzing.
- Memindai target temuan tanpa konfirmasi eksplisit dari pengguna — tidak pernah, dalam mode apa pun.
- Penemuan di luar subnet privat target awal, kecuali dikonfigurasi secara eksplisit (`--subnet`).
- Dasbor web.

## 2. Instalasi

### Prasyarat

- Python 3.10+
- Koneksi Internet, untuk dependensi

### Instalasi

```bash
[ -d omega-deep ] && echo "ℹ️ Sudah diekstrak di sini, langkah dilewati." || tar -xzf omega-deep.tar.gz
cd omega-deep/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Membuat lingkungan virtual `.venv` jika belum ada.
2. Memasang dependensi (`vendor/omega-lib/` lalu `pip install -e .`; `pyproject.toml` tetap menjadi satu-satunya sumber kebenaran).
3. Menjadikan `omega-deep.sh` dan `install.sh` dapat dieksekusi.
4. Menambahkan alias `deep` ke `~/.bashrc` dan `~/.zshrc` (tanpa duplikat jika sudah ada).

### Dependensi

Dideklarasikan di `pyproject.toml` (tidak ada lagi `requirements.txt`):
- `omega-lib`: pustaka bersama rangkaian (`ConfidenceLevel`, tema, deteksi terminal) — disertakan di `vendor/omega-lib/`
- `textual`: antarmuka TUI, tema, penyesuaian otomatis dengan terminal
- `httpx`: probe HTTP/HTTPS (layanan dan penemuan)
- `cryptography`: pembacaan sertifikat TLS yang dinegosiasikan
- `jinja2`: templat untuk ekspor HTML
- Dependensi pengembangan (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `trustme`, `ruff`, `mypy`, `import-linter`

## 3. Penggunaan

### Mode interaktif (TUI)

Disarankan untuk pemakaian sehari-hari — dijalankan tanpa argumen:

```bash
./omega-deep.sh
```
jika Anda sudah membuat alias, cukup ketik `deep` di terminal:
```bash
deep
```

Alur: layar pembuka (tertutup dengan satu tombol atau klik) → menu utama (Analisis / Profil / Riwayat / Pengaturan / Bantuan) → isian target akar, pilihan profil dan pengaman penemuan (kedalaman maks., jumlah target maks., subnet yang diizinkan) → analisis (indikator tak tentu dan log operasi jaringan secara langsung) → untuk setiap kelompok target temuan, layar validasi (satu baris per target, dengan sumber/keyakinan/bukti terlihat, sakelar terima/tolak — tidak ada yang dicentang secara bawaan) → detail analisis (host, port/layanan/peran, graf, ekspor) → riwayat/perbandingan/pengulangan dan pengaturan dari menu utama. Penyesuaian dengan terminal (warna, ukuran, penyederhanaan struktur) berlangsung otomatis.

#### Pintasan keyboard

| Tombol | Aksi |
|---|---|
| `↑` / `↓` | Berpindah antarelemen layar |
| `Tab` / `Shift+Tab` | Berpindah antarkolom formulir |
| `Esc` | Kembali ke layar sebelumnya (konfirmasi keluar di layar awal) |
| `t` | Tema berikutnya (langsung diterapkan, tanpa konfirmasi) |
| `r` | Menyegarkan deteksi terminal |
| `a` | Menampilkan bantuan |
| `q` | Keluar (dengan konfirmasi) |

### Bahasa antarmuka

Antarmuka tersedia dalam 17 bahasa: Prancis, Inggris, Spanyol, Portugis (Brasil), Italia, Jerman, Belanda, Polandia, Rusia, Tionghoa Sederhana, Vietnam, Thai, Indonesia, Jepang, Korea, Hindi, dan Arab. Pilihan dibuat di Pengaturan (“Langue / Language”) dan berlaku setelah antarmuka dimulai ulang; variabel `OMEGA_DEEP_LANG` (misalnya `OMEGA_DEEP_LANG=id ./omega-deep.sh`) memaksakan bahasa untuk satu sesi. Jika dijalankan dari omega-suite, omega-deep memakai bahasa rangkaian. Di konsol teks Linux (TTY), bahasa beraksara non-Latin ditampilkan dalam bahasa Inggris selama sesi itu. Baris perintah tetap berbahasa Prancis.

### Kontak dan dukungan

Bantuan (tombol `a`) menyediakan layar **Kontak dan dukungan**: *Traktir kopi* (halaman PayPal pengembang), *Hubungi dukungan* (alamat email dan formulir kontak situs, ditampilkan apa adanya), *Daftarkan saya sebagai pengguna (anonim)*, dan *Periksa pembaruan*. Pendaftaran bersifat sukarela, nonaktif secara bawaan, dan dikirim hanya sekali: hanya digunakan untuk menghitung pengguna dan, jika Anda mau, benua atau negara mereka (daftar tertutup, tidak pernah teks bebas). Yang dikirim adalah kunci yang diambil secara acak, nama perangkat lunak (`omega-deep`), dan versinya; tidak pernah nama, nama mesin, pengaturan, target, maupun hasil. Alamat IP tidak disimpan dalam pendaftaran, tetapi, seperti setiap kunjungan, melewati pemeriksaan keamanan dan log server penerima. Penarikan kapan saja dari layar yang sama (*Jangan daftarkan saya lagi*). Pemeriksaan pembaruan hanya membaca daftar versi yang dipublikasikan di situs, dan tidak pernah tanpa klik.

### Mode skrip (CLI)

Setiap subperintah mengaktifkan mode CLI:

```bash
# Menganalisis target (pemindaian akar + penemuan multi-target)
./omega-deep.sh analyze 192.168.1.10 --profile web --max-depth 3 --max-targets 10 --subnet 192.168.1.0/24

# Riwayat (dapat difilter per target akar)
./omega-deep.sh history --target 192.168.1.10 --limit 20

# Detail analisis (teks, JSON, atau HTML) — 5 tema ekspor untuk dipilih
./omega-deep.sh show <scan_id> --format html --theme omega-base --output laporan.html

# Membandingkan dua analisis (status port target akar)
./omega-deep.sh compare <scan_id_a> <scan_id_b>

# Profil port pribadi
./omega-deep.sh profile list
./omega-deep.sh profile create lab --ports 22,80,443 --description "Profil saya"
./omega-deep.sh profile edit lab --ports 22,80,443,8080
./omega-deep.sh profile pin lab
./omega-deep.sh profile unpin lab
./omega-deep.sh profile delete lab
```

Di CLI, target temuan divalidasi melalui satu pertanyaan interaktif per target (`Scanner <cible> ? [o/N]`, dalam bahasa Prancis seperti bagian lain baris perintah), dengan detail bukti ditampilkan sebelum setiap pertanyaan. `--auto-validate` menerima semuanya tanpa peninjauan (**tidak disarankan**, peringatan ditampilkan); di lingkungan non-interaktif (tanpa TTY dan tanpa `--auto-validate`), setiap target temuan ditolak secara bawaan alih-alih dipindai tanpa konfirmasi.

### Format target yang diterima

```text
192.168.1.10                IPv4
example.org                 Nama host
http://example.org          URL HTTP  (skema dihapus sebelum resolusi)
https://example.org:8443    URL HTTPS dengan port  (skema dan port dihapus)
```

Skema dan port, bila ada, dihapus sebelum resolusi DNS (`domain/targets/validation.py::normalize_target_input`) — menempelkan URL lengkap tetap berfungsi, hanya host yang disimpan. Target *temuan* dinormalisasi dengan cara yang sama, tetapi tidak pernah dipindai tanpa validasi (lihat [§4](#4-penemuan-target-dan-pengaman)).

## 4. Penemuan target dan pengaman

### Sumber petunjuk

| Sumber | Asal | Keyakinan |
|---|---|---|
| `header` | `X-Forwarded-Host`, `X-Real-IP`, `X-Backend-Server`, `Via` | `DECLARED` |
| `redirection` | Header `Location` dari respons HTTP | `DECLARED` |
| `certificate` | SAN (Subject Alternative Names) dari sertifikat TLS yang dinegosiasikan | `DECLARED` |
| `html_link` | Tautan (`<a href>`) yang disajikan halaman | `INFERRED` |

Nilai `DECLARED` tetap merupakan deklarasi diri dari target (dapat dipalsukan) — lihat [§10](#10-perlindungan-terhadap-nilai-palsu). `html_link` sengaja dijadikan sumber terlemah: sekadar tautan tidak menyatakan relasi infrastruktur apa pun.

### Pengaman (selalu aktif, tidak pernah bisa dimatikan)

- **Perimeter**: calon target harus berupa IP privat dalam `/24` yang sama dengan target akar, kecuali `--subnet` diberikan secara eksplisit (dalam hal ini yang dihitung hanya keanggotaan pada subnet yang diberikan, meskipun mencakup IP publik — konfigurasi eksplisit itulah yang mengizinkan pengecualian). Nama host yang belum diresolusi tidak pernah diterima oleh filter ini (meresolusinya untuk memeriksa sudah merupakan tindakan jaringan di luar cakupan pemeriksaan ini).
- **Kedalaman**: `--max-depth` (bawaan 3) — paling banyak A → B → C → D.
- **Jumlah target**: `--max-targets` (bawaan 10) — di semua kedalaman.

### Validasi (tidak pernah memindai tanpa konfirmasi)

Setiap target yang diusulkan melalui `PROPOSED → PRESENTED → ACCEPTED` atau `REJECTED`. Aturannya **aman saat gagal**: setiap target yang tidak pernah diterima secara eksplisit (diam, layar ditutup, interupsi, waktu habis, tanpa TTY) dianggap ditolak — tidak pernah sebaliknya. Di TUI, layar khusus mencantumkan target suatu kelompok beserta bukti dan keyakinannya, sakelar terima/tolak per baris, “terima semua”/“tolak semua”, dan penolakan total secara bawaan dengan Esc. Di CLI, satu pertanyaan per target; `--auto-validate` (tidak disarankan) adalah satu-satunya cara melewati interaktivitas.

## 5. Profil pemindaian

| Profil | Deskripsi | Disematkan |
|---|---|---|
| `minimal` | Pemindaian sangat cepat: SSH + HTTP + HTTPS (22, 80, 443) | ya |
| `classic` | Layanan Internet/LAN umum | ya |
| `web` | Layanan web dan alternatifnya | tidak |
| `db` | Basis data dan layanan data | tidak |
| `remote` | Akses jarak jauh — shell, desktop, RustDesk | tidak |
| `mail` | Layanan surel | tidak |
| `dns` | Layanan DNS | tidak |
| `iot` | Perangkat IoT, kamera, router, rumah pintar | tidak |
| `dev` | Lingkungan pengembangan/laboratorium | tidak |
| `docker` | Docker, Swarm, dan layanan umum dalam kontainer | tidak |
| `complet` | **Dibuat seketika**: gabungan terurut tanpa duplikat dari semua profil di atas | tidak |
| *profil pribadi* | Dibuat di layar **Profil** (TUI) atau dengan `profile create` (CLI), dicantumkan bersama profil sistem, diberi awalan `* ` di TUI | tidak |

Profil berlaku untuk target akar **dan** untuk setiap target temuan yang diterima — tidak ada profil berbeda per host. Detail lengkap, aturan validasi, dan pengelolaan profil pribadi: `docs/PROFILES.md`.

## 6. Arsitektur

Omega-deep disusun dengan **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins / shared), selaras dengan templat rangkaian `omega-` (lihat `omega-scan`/`omega-check`) dan diverifikasi oleh `import-linter` pada setiap perubahan. Detail lengkap ada di **`docs/ARCHITECTURE.md`**.

Gambaran singkat:

```text
src/omega_deep/
├── domain/          Logika bisnis murni: pemindaian, target, layanan, profil, laporan,
│                    discovery (target yang diusulkan, mesin status validasi),
│                    architecture (graf, aturan relasi)
├── application/     Kasus penggunaan (commands/queries) — termasuk discover_targets,
│                    validate_targets, reconstruct_architecture (baru dibanding omega-check)
├── ports/           Kontrak yang diharapkan aplikasi (probe, termasuk discovery_prober,
│                    repositori, pengekspor...)
├── infrastructure/  Implementasi konkret (socket/httpx/cryptography, SQLite,
│                    penggambaran graf dalam SVG — Textual TIDAK ada di sini)
├── interfaces/      tui/ (Textual) dan cli/ (untuk skrip), dengan kesetaraan fungsi yang ketat
├── app/             Perakitan (DependencyContainer, bootstrap, siklus hidup)
├── core/, shared/   Kosakata lintas bagian, utilitas nonbisnis
└── plugins/         Struktur sudah disiapkan, kosong (belum ada arah perluasan yang dipastikan)
```

Aturan desain:
- `domain/services/policies.py`: menggolongkan petunjuk yang sudah terkumpul, tidak pernah mengakses jaringan.
- `domain/discovery/policies.py`: pengaman perimeter/kedalaman/jumlah — logika murni, dapat diuji tanpa jaringan.
- `domain/architecture/service.py`: merekonstruksi graf dari asal-usul yang sudah dibawa setiap `Host`, tidak mengirim permintaan baru.
- `infrastructure/network/` dan `infrastructure/discovery/`: mengakses jaringan (soket, `httpx`, `cryptography`), tidak pernah menilai.
- `interfaces/`: menampilkan, tidak berisi logika bisnis apa pun — layar validasi target temuan memanggil `validate_targets`, bukan menerapkan sendiri aturan aman saat gagal.
- `infrastructure/exporters/`: membaca hasil analisis (pemindaian, host, graf), tidak menghitung ulang apa pun.

## 7. Pengenalan layanan dan peran

### Protokol yang dideteksi

| Protokol | Probe | Detail yang dikumpulkan |
|---|---|---|
| HTTP / HTTPS | `httpx` | Banner `Server`, header autentikasi |
| TLS | `cryptography` (sertifikat yang dinegosiasikan, termasuk `CERT_NONE`) | Versi, cipher, subjek/penerbit sertifikat |
| SSH | Banner mentah | Perangkat lunak dan versi (mis. `OpenSSH 10.4`) |
| VNC (RFB) | Kode keamanan yang diumumkan server | Jenis autentikasi yang didukung |
| Umum | Banner mentah pada port terbuka yang tidak dikenali | Ekstraksi hati-hati, tanpa heuristik agresif |

### Peran yang disimpulkan

Disimpulkan dari protokol yang **benar-benar dinegosiasikan**, tidak pernah dari dugaan nomor port:

| Peran | Syarat | Keyakinan |
|---|---|---|
| `server web` | Protokol HTTP/HTTPS terkonfirmasi | `INFERRED` |
| `akses shell` | Protokol SSH terkonfirmasi | `CORROBORATED` |
| `akses grafis` | Protokol VNC terkonfirmasi | `CORROBORATED` |
| `basis data` | Port dalam rentang profil sistem `db` | `INFERRED` |

### Tanda tangan WAF yang dikenal

Dideteksi melalui header deklaratif (`server`, `x-sdk`) — kehadirannya **dideklarasikan oleh target**, tidak pernah diverifikasi secara independen: Cloudflare, Sucuri, Akamai, Imperva Incapsula, AWS ELB (dicantumkan sebagai informasi, sebenarnya bukan WAF aplikasi).

## 8. Graf arsitektur

Direkonstruksi semata-mata dari asal-usul yang sudah dibawa setiap host yang diterima (`discovered_from`/`discovery_source`/`discovery_confidence`) — tanpa permintaan jaringan baru, tanpa analisis ulang petunjuk mentah.

### Relasi yang dihasilkan

| Relasi | Sumber penemuan | Arti |
|---|---|---|
| `proxy_to` | `header` | Target akar (atau host yang sudah diterima) kemungkinan adalah proxy menuju target temuan |
| `redirect_to` | `redirection` | Pengalihan HTTP teramati menuju target temuan |
| `linked_to` | `certificate` atau `html_link` | Relasi paling netral — infrastruktur/aplikasi bersama, tanpa menyatakan arah aliran |

`backend_of` (sisi kebalikan dari `proxy_to`) sengaja tidak dihasilkan — itu akan menjadi informasi ganda, bukan kesimpulan baru.

### Tampilan

- **TUI** (detail analisis) dan **ekspor JSON/teks**: daftar sisi (sumber, relasi, tujuan, keyakinan) — terminal bukan tempat untuk tampilan grafis yang kaya.
- **Ekspor HTML**: **diagram SVG sungguhan** (simpul = lingkaran, sisi = panah berlabel), tata letak berlapis yang dihitung dari target akar, ukuran sebanding dengan jumlah mesin yang ditemukan — tidak pernah bergantung pada pustaka tata letak graf yang berat; secara rancangan grafnya tetap kecil (dibatasi oleh pengaman di [§4](#4-penemuan-target-dan-pengaman)).

## 9. Kebijakan keyakinan

Setiap kolom yang dikumpulkan memiliki salah satu tingkat berikut:

| Tingkat | Arti |
|---|---|
| `VERIFIED` | Fakta protokol yang diamati langsung, yang tidak dapat dipalsukan target (mis. port tertutup yang dikonfirmasi oleh RST TCP, versi TLS yang benar-benar dinegosiasikan). |
| `DECLARED` | Nilai yang diumumkan sendiri oleh target di kolom yang sepenuhnya ia kendalikan (mis. banner `Server`, header `X-Backend-Server`) — masuk akal tetapi dapat dipalsukan sesuka hati. |
| `CORROBORATED` | Nilai `DECLARED` yang dikonfirmasi oleh petunjuk independen (mis. peran SSH, karena protokolnya benar-benar dinegosiasikan). |
| `INFERRED` | Disimpulkan dari pola/heuristik, tanpa deklarasi eksplisit dari target (mis. tautan HTML). |
| `UNKNOWN` | Tidak ada petunjuk yang dapat dipakai, atau sengaja disembunyikan target. |

## 10. Perlindungan terhadap nilai palsu

Omega-deep tidak memercayai data apa pun yang dideklarasikan sendiri oleh target tanpa menandainya secara eksplisit — dan penemuan target adalah bagian paling sensitif dari proyek ini: target berbahaya *bisa saja* mengumumkan `X-Backend-Server` palsu untuk mengarahkan penemuan ke IP pilihannya. Ada dua perlindungan struktural yang saling independen:
- Tidak ada informasi turunan dari target yang pernah menjadi `VERIFIED` hanya karena diumumkan — banner `Server` atau header `X-Backend-Server` tetap `DECLARED`, seberapa pun masuk akalnya.
- Pengaman perimeter ([§4](#4-penemuan-target-dan-pengaman)) membatasi ke mana target yang diumumkan dapat mengarah (`/24` privat yang sama, kecuali dikonfigurasi secara eksplisit), dan validasi pengguna menentukan apakah target itu dipindai sama sekali — target palsu di luar perimeter bahkan tidak pernah diusulkan; target di dalam perimeter tetap memerlukan konfirmasi eksplisit sebelum pemindaian apa pun.

## 11. Kompatibilitas terminal

TUI (Textual) otomatis mendeteksi kemampuan terminal (emulator, ukuran) dan menyesuaikan lembar gaya strukturalnya (`complete`/`standard`/`reduced`/`mono`), tanpa opsi manual. Mode CLI selalu berupa teks biasa, tidak bergantung pada terminal. Kebijakan ini dipakai bersama oleh seluruh rangkaian `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil menurut emulator yang terdeteksi

| Emulator | Profil awal |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH modern | `reduced` |
| TTY Linux, SSH lama | `mono` |
| Emulator tidak dikenal | `reduced` (cadangan bawaan) |

### Profil menurut ukuran terminal

| Ukuran minimum (kolom × baris) | Batas atas profil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| di bawahnya | `mono` |

Profil akhir adalah **yang lebih ketat dari keduanya** (emulator dan ukuran) — Ghostty layar penuh yang diperkecil menjadi 70 kolom turun ke `mono`, meskipun emulatornya mengizinkan `complete`. Dapat disegarkan langsung dengan tombol `r`.

## 12. Ekspor

Laporan teks dan HTML ditulis dalam bahasa yang dipilih di Pengaturan (“Bahasa ekspor”, bawaannya sama dengan antarmuka); JSON tetap berupa data dan tidak diterjemahkan. Laporan dibuat di `var/exports/` secara bawaan (jalur runtime yang berjangkar pada folder proyek, `$OMEGA_DEEP_VAR_DIR` untuk menggantinya), atau di jalur yang ditentukan (`--output` di CLI, kotak dialog di TUI). Nama berkas jelas dan bercap waktu: `analyse-{profil}-{tanggal}.ext`, `analyse-custom-{tanggal}.ext` untuk profil pribadi.

### JSON, sumber kebenaran

Struktur lengkap analisis (`Scan` + `Host[]` + `ArchitectureGraph`), sepenuhnya dapat diserialisasi ke JSON, termasuk tingkat keyakinan.

### Teks, laporan ringkas yang mudah dibaca

Dapat dibaca di luar terminal, tanpa kode ANSI — graf berupa daftar sisi.

### HTML, laporan web mandiri

5 tema pilihan (`--theme` di CLI, pemilih di TUI; secara bawaan mengikuti tema antarmuka yang aktif bila ada padanannya). Tata letak khusus: wadah, kisi informasi, kotak statistik per status port, lencana berwarna, **diagram SVG graf arsitektur** (lihat [§8](#8-graf-arsitektur)) — keluarga visual yang sama dengan `omega-scan`/`omega-check`.

## 13. Riwayat dan perbandingan

Setiap analisis disimpan (SQLite, `var/db/omega-deep.db`): satu `scan_id` memuat target akar **dan** semua host temuan/diterima, beserta graf hasil rekonstruksi. Riwayat dapat dilihat per target akar (dengan kolom khusus untuk jumlah target temuan), detail analisis sebelumnya (host + graf), perbandingan dua analisis (status port **target akar** saja — membandingkan graf penemuan adalah perluasan yang mungkin, belum diperlukan saat ini), dan pengulangan analisis pada target akar yang sama tanpa mengetik ulang.

## 14. Pengujian

```bash
source .venv/bin/activate
lint-imports        # memeriksa Dependency Rule
pytest -q           # 191 pengujian
ruff check src tests
mypy -p omega_deep
```

Struktur: `tests/unit/` (domain dan aplikasi, tanpa I/O sungguhan), `tests/integration/` (SQLite/berkas sungguhan, server HTTP tiruan `pytest-httpserver`, TLS melalui `trustme`), `tests/tui/` (navigasi melalui `Pilot`, struktural — tanpa klaim verifikasi visual).

## 15. Di luar cakupan

- Pemindaian CVE
- Deteksi aktif SQLi, XSS, RCE
- Pengenalan sistem operasi
- Teknik pemindaian tingkat rendah ala nmap (SYN scan, paket mentah)
- Crawling
- Fuzzing
- Brute force
- Memindai target temuan tanpa konfirmasi eksplisit — tidak pernah, dalam mode apa pun
- Penemuan di luar subnet privat target awal tanpa konfigurasi eksplisit
- Dasbor web

---

> Omega-deep — Menemukan, memetakan, menilai, melaporkan.
> Arsitektur yang direkonstruksi dengan keyakinan yang jelas, tidak pernah dugaan yang menyamar sebagai fakta.
