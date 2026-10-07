# Pengintaian sumber data (Fase 0)

Tanggal pengintaian: 2026-10-07.
Metode: pemeriksaan `robots.txt` dan struktur halaman lewat alat pengambil halaman otomatis (bukan inspeksi HTML mentah manual). Lihat bagian [Catatan reliabilitas](#catatan-reliabilitas-temuan) — detail spesifik (nomor/tahun peraturan pada contoh) harus diverifikasi ulang dengan `requests`/`curl` di awal Fase 1 sebelum dipakai sebagai acuan pasti.

## jdih.kemnaker.go.id

- **`robots.txt`**: `User-agent: *` / `Allow: /`. Tidak ada path yang dibatasi.
- **Rendering**: server-rendered HTML. Navigasi, daftar peraturan, metadata, dan relasi tampil langsung di HTML awal — tidak perlu menjalankan JavaScript untuk mengambil kontennya.
- **Pola URL**:
  - Daftar: `/peraturan`, dengan filter `?tag[]=...` (tema), serta paging `?hal=2`, `?hal=3`, dst.
  - Detail: `/peraturan/detail/{id}/{slug}` — contoh: `/peraturan/detail/2687/peraturan-menteri-ketenagakerjaan-nomor-5-tahun-2025`.
- **Filter yang tersedia di daftar**: jenis dokumen (UUD, UU, Peraturan Presiden, Keputusan Menteri, dll.), tema/subjek, status (Berlaku / Tidak Berlaku), ketersediaan terjemahan, tahun, nomor dokumen, kata kunci.
- **Metadata pada halaman detail**: nomor, tahun, judul, tanggal penetapan, tanggal pengundangan, status berlaku, subjek/tag, bidang hukum, penandatangan.
- **Relasi**: tampil sebagai link HTML langsung (bukan lewat JavaScript), contoh label yang ditemukan: `Mengubah`. Ada juga bagian visual "Peta Hubungan Peraturan", tapi untuk scraping kita hanya butuh daftar relasi tekstualnya, bukan visualisasinya.
- **Dokumen yang bisa diunduh/dilihat di halaman detail**: tombol "Abstrak", "Risalah Pembahasan", "Data Dukung" (link `<a href>` biasa) — **dan PDF teks lengkap**, tapi disematkan lewat `<iframe>` PDF viewer (`asset/data_puu/{slug}.pdf`) dan tombol "Dokumen" (`onclick`), bukan `<a href>` biasa. **Dikonfirmasi lewat pengambilan HTML mentah** — lihat [verifikasi manual](#verifikasi-manual-2026-10-07-dengan-invoke-webrequest--pypdf-bukan-alat-ringkas-ai) di bawah. (Catatan awal Fase 0 yang menyimpulkan "tidak ada PDF teks lengkap" ternyata salah — itu keterbatasan alat ringkas HTML, bukan keterbatasan situs.)

## peraturan.bpk.go.id

- **`robots.txt`**: `User-agent: *`, disallow `/Admin/`, `/Identity/`, `/Account/`, `/Manage/`, `/health`, `/Error`. Ada `Sitemap: https://peraturan.bpk.go.id/sitemap.xml`. Semua path publik yang relevan (`/Details/`, `/Search`, `/Jenis/`) tidak dibatasi.
- **Rendering**: server-rendered HTML. Ada elemen JS kosmetik (carousel) tapi tidak memengaruhi konten utama/relasi/metadata.
- **Pola URL**:
  - Cari: `/Search?jenis={id}` (contoh: `jenis=27` → Peraturan BPK).
  - Kategori: `/Jenis/{id}`.
  - Detail: `/Details/{id}/{slug}` — contoh: `/Details/246523/uu-no-6-tahun-2023`.
- **Filter yang tersedia**: tahun (1945–2026), entitas/wilayah, jenis peraturan (UUD, Keppres, PP, UU, Peraturan Menteri/Lembaga, Peraturan Daerah, dll.), subjek, tematik.
- **Metadata pada halaman detail**: tipe dokumen, judul, T.E.U. (teritorial), nomor, bentuk (UU/PP/Permen/dll.), tahun, tempat & tanggal penetapan, tanggal pengundangan, tanggal berlaku, sumber (LN/TLN), subjek, status, bahasa, bidang, alias.
- **Relasi**: tampil sebagai daftar link terkategori — label yang ditemukan: `Diubah dengan`, `Mencabut`, `Menetapkan`, `Mengubah` (kemungkinan juga `Dicabut dengan` pada peraturan yang sudah dicabut, belum terverifikasi langsung karena contoh yang diperiksa masih berlaku).
- **Dokumen yang bisa diunduh**: PDF teks lengkap tersedia di bagian "FILE-FILE PERATURAN", dengan pola `/Read/{id}/{nama-file}.pdf` (lihat di browser) dan `/Download/{id}/{nama-file}.pdf` (unduh). Dari contoh yang diperiksa, ini adalah **dokumen teks lengkap**, bukan sekadar abstrak.
- **Belum diverifikasi**: apakah PDF di sini berupa teks (bisa di-extract) atau hasil scan gambar — untuk UU modern biasanya teks asli, tapi peraturan lama/kolonial (contoh: Staatsblad yang muncul di relasi "Mencabut" pada contoh di atas) kemungkinan besar scan. Perlu dicek langsung per-file di Fase 1 (misal dengan `pdftotext` atau `pypdf`) sebelum scraper bergantung pada ekstraksi teks PDF.

## Perbandingan ringkas

| Aspek | jdih.kemnaker.go.id | peraturan.bpk.go.id |
|---|---|---|
| robots.txt | Bebas | Bebas (kecuali area admin/akun) |
| Rendering | Server-rendered | Server-rendered |
| Relasi di HTML | Ya (ditemukan `Mengubah`) | Ya (lebih lengkap: `Mengubah`, `Diubah dengan`, `Mencabut`, `Menetapkan`) |
| PDF teks lengkap | Tidak ditemukan (baru abstrak) | Ada (`/Download/{id}/{file}.pdf`) |
| Sumber resmi penerbit | Ya (Kemnaker langsung) | Tidak (agregator BPK) |

## Keputusan sumber (disetujui pemilik proyek, 2026-10-07)

- **Sumber primer**: `peraturan.bpk.go.id` — relasi paling lengkap dan PDF teks lengkap tersedia langsung.
- **Sumber pembanding**: `jdih.kemnaker.go.id` — dipakai untuk cross-check status dan metadata resmi dari kementerian penerbit, karena ini sumber langsung dari Kemnaker.
- Keputusan ini dicatat juga di [`docs/decisions.md`](decisions.md).

## Catatan reliabilitas temuan

Pengintaian di atas dilakukan lewat alat pengambil-dan-ringkas halaman otomatis, bukan dengan membaca HTML mentah secara manual. Struktur halaman (pola URL, keberadaan field, lokasi relasi) cukup bisa diandalkan karena konsisten di beberapa halaman yang diperiksa, tapi **detail spesifik seperti nomor/tahun/judul peraturan pada contoh di atas bisa saja salah kutip** oleh alat tersebut. Sebelum menulis parser di Fase 1:

1. Ambil ulang 2–3 halaman detail dari masing-masing situs dengan `requests` + simpan HTML mentahnya ke `raw/` sebagai bukti.
2. Periksa langsung dengan `BeautifulSoup`/`lxml` di mana persisnya tag/kelas CSS yang membungkus setiap field metadata dan relasi.
3. Konfirmasi ulang temuan "tidak ada PDF teks lengkap di jdih.kemnaker.go.id" pada minimal 3 Permenaker lain sebelum menganggapnya sebagai keterbatasan situs yang permanen.

## Verifikasi manual (2026-10-07, dengan `Invoke-WebRequest` + `pypdf`, bukan alat ringkas AI)

Pengecekan langsung terhadap HTML mentah dan satu file PDF nyata, untuk menggantikan asumsi dari ringkasan AI di atas:

- **Konektivitas**: `peraturan.bpk.go.id` bisa diakses langsung dari klien HTTP .NET/PowerShell (TLS 1.2). **`jdih.kemnaker.go.id` GAGAL** — `Invoke-WebRequest` melempar `Could not create SSL/TLS secure channel` meski situs lain (termasuk BPK dan Google) berhasil. Ini menunjukkan server Kemnaker punya konfigurasi TLS/cipher suite yang tidak kompatibel dengan client .NET default — kemungkinan juga akan bermasalah dengan beberapa versi `requests`/OpenSSL di Python, perlu dicoba langsung di Fase 1 (mungkin perlu `urllib3` dengan cipher suite custom atau `curl`).
- **Struktur HTML metadata BPK** (`/Details/{id}/{slug}`): dikonfirmasi berupa pasangan div berulang `<div class="col-lg-3 fw-bold">Label</div><div class="col-lg-9">Nilai</div>` di dalam kontainer "METADATA PERATURAN" — mudah di-parse dengan BeautifulSoup tanpa perlu regex rumit.
- **Struktur relasi BPK**: dikonfirmasi berupa heading `<div class="col-12 fw-semibold bg-light-primary p-4">Label :</div>` (label: `Diubah dengan`, `Mencabut`, `Menetapkan`, `Mengubah`) diikuti `<ol type="a"><li><a href="/Details/{id}/{slug}">...</a> <span class="text-muted">tentang</span> {judul}</li></ol>`. Beberapa entri relasi berupa teks biasa tanpa link (misal peraturan kolonial "Staatsblad") — parser harus menangani item `<li>` tanpa `<a>`.
- **Contoh nyata Permenaker di BPK**: `/Details/231405/permenaker-no-11-tahun-2022` (Permenaker No. 11 Tahun 2022) — field metadata dan pola relasi sama persis dengan contoh UU di atas, dan `Bentuk Singkat` terisi `Permenaker`. Jadi pola parsing yang sama berlaku untuk semua jenis peraturan di situs ini, bukan khusus UU.
- **PDF teks lengkap**: diunduh langsung `/Download/264901/Permenaker%20Nomor%2011%20Tahun%202022.pdf` dan diekstrak dengan `pypdf` — berhasil, 10 halaman, halaman pertama menghasilkan teks bersih (bukan hasil scan/gambar). Jadi untuk Permenaker modern, teks PDF bisa diandalkan untuk ekstraksi otomatis bila dibutuhkan nanti.

**Koreksi penting atas temuan Fase 0 sebelumnya**: dengan `requests` Python (bukan .NET), `jdih.kemnaker.go.id` **berhasil diakses** — jadi masalah TLS di atas spesifik ke stack .NET/PowerShell, bukan ke server itu sendiri. Setelah diakses dengan benar, halaman detail Permenaker **memang punya PDF teks lengkap**, hanya disematkan lewat `<iframe>` PDF viewer (`asset/data_puu/{slug}.pdf`, contoh: `https://jdih.kemnaker.go.id/asset/data_puu/2025pmnaker005.pdf`) dan tombol "Dokumen" (`onclick="directOpen(...)"`), bukan sebagai `<a href>` biasa berlabel "Unduh" — ini sebabnya tidak terlihat oleh ringkasan AI di WebFetch sebelumnya. Relasi (`Mengubah`, dll.) tampil di bagian "Riwayat Peraturan" sebagai timeline dengan link ke peraturan terkait, strukturnya beda dari BPK (BPK: daftar `<ol>` per kategori; Kemnaker: timeline kronologis bercampur semua jenis relasi, label per item lewat class `timeline-label bg-{jenis}`).

- Diunduh dan diekstrak PDF `2025pmnaker005.pdf` (Permenaker No. 5 Tahun 2025) dengan `pypdf`: 16 halaman, teks berhasil diekstrak (bukan scan). **Tapi baris pertama dokumen berbunyi "RANCANGAN PERATURAN MENTERI KETENAGAKERJAAN..."** — kata "RANCANGAN" (draft) muncul di naskah yang disajikan sebagai peraturan resmi berlaku. Ini perlu diklarifikasi di Fase 1: apakah ini quirk template yang tidak dibersihkan, atau memang ada risiko situs menyajikan naskah draft bukan naskah final yang diundangkan.

**Simpulan setelah verifikasi**: kedua situs sebenarnya punya PDF teks lengkap Permenaker. Keputusan sumber primer BPK tetap dipertahankan — relasinya terkategori lebih jelas per jenis (bukan timeline campur), dan tidak ada tanda "RANCANGAN" pada sampel yang dicek. Kemnaker tetap jadi pembanding resmi, dengan catatan kewaspadaan soal kata "RANCANGAN" di atas.

## Hal yang masih terbuka untuk Fase 1

- **Klarifikasi kata "RANCANGAN" pada PDF Kemnaker** — cek beberapa Permenaker lain apakah ini konsisten muncul (kemungkinan quirk template) sebelum memutuskan apakah teks PDF Kemnaker aman dipakai untuk apa pun selain cross-check metadata.
- Verifikasi apakah ada PDF Permenaker/peraturan lain di BPK yang berupa hasil scan (terutama peraturan lama) — sample yang dicek baru dua peraturan modern (2022–2023).
- Cek apakah ada endpoint/API tersembunyi (misal JSON) di salah satu situs yang lebih stabil untuk diambil dibanding HTML.
- Klien HTTP scraper harus memakai Python `requests` (terverifikasi jalan untuk kedua situs) — jangan pakai pendekatan yang bergantung pada stack TLS .NET/PowerShell.
