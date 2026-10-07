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
- **Dokumen yang bisa diunduh di halaman detail yang diperiksa**: hanya **Abstrak**, **Risalah Pembahasan**, dan **Data Dukung** (ketiganya PDF). **Tidak ditemukan** link PDF teks lengkap batang tubuh peraturan di halaman yang diperiksa.
  - **Ini adalah temuan yang belum pasti final** — perlu dicek ulang secara manual pada beberapa Permenaker lain di awal Fase 1 sebelum disimpulkan bahwa situs ini memang tidak menyediakan teks lengkap.

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

## Hal yang masih terbuka untuk Fase 1

- Konfirmasi final: apakah jdih.kemnaker.go.id benar-benar tidak menyediakan PDF teks lengkap Permenaker, atau link-nya hanya belum ditemukan.
- Verifikasi apakah PDF di peraturan.bpk.go.id selalu berupa teks yang bisa diekstrak, atau ada yang berupa hasil scan (terutama peraturan lama).
- Cek apakah ada endpoint/API tersembunyi (misal JSON) di salah satu situs yang lebih stabil untuk diambil dibanding HTML.
