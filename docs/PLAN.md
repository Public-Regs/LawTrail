# Rencana fase LawTrail

Status per fase. Diperbarui setiap fase selesai agar bisa dilanjutkan di sesi baru.

## Fase 0 — Pengintaian sumber dan fondasi repo
**Status**: Selesai (2026-10-07)

- Pengintaian jdih.kemnaker.go.id dan peraturan.bpk.go.id: lihat [`docs/source-recon.md`](source-recon.md).
- Keputusan sumber primer/pembanding dan kontak scraper: lihat [`docs/decisions.md`](decisions.md).
- Kerangka repo (README, LICENSE, CLAUDE.md, struktur folder) dibuat.
- Verifikasi manual dengan `requests`/`pypdf` Python (bukan hanya alat ringkas AI): kedua situs sama-sama punya PDF teks lengkap Permenaker; terdeteksi juga bahwa Kemnaker gagal diakses dari klien HTTP .NET (bukan masalah di sisi situs). Detail di source-recon.md.
- **Belum pasti, perlu dicek di Fase 1**: kata "RANCANGAN" muncul di baris pertama PDF Permenaker dari Kemnaker yang disampel — perlu dicek di beberapa Permenaker lain.

## Fase 1 — Skema data dan scraper
**Status**: Selesai (2026-10-07)

- Skema `data/regulations/{id}.json` dan `data/edges.json` dirancang dan disetujui — lihat [`docs/schema.md`](schema.md) dan [`docs/decisions.md`](decisions.md).
- Verifikasi manual (bukan cuma ringkasan AI) dilakukan dengan `requests`/`BeautifulSoup`/`pypdf` langsung terhadap HTML dan PDF nyata — lihat bagian "Verifikasi manual" di [`docs/source-recon.md`](source-recon.md).
- Scraper Python di [`scripts/`](../scripts/): `lawtrail/bpk.py` (crawler daftar + parser detail BPK), `lawtrail/kemnaker.py` (cross-check status, best-effort), `lawtrail/storage.py` (penulisan idempoten), `run_scrape.py` (CLI). Jeda ≥2 detik antar request dan retry ada di `lawtrail/http_client.py`.
- Test parser (`scripts/tests/`) memakai fixture HTML nyata, bukan HTML buatan — 4/4 lulus.
- Idempotensi terverifikasi pada subset (3 peraturan): menjalankan ulang scraper tanpa perubahan di sumber menghasilkan 0 file berubah.
- **Scraping penuh selesai dijalankan** (sekali, manual, bukan GitHub Actions — itu Fase 2): 283 Permenaker diperiksa, 166 berstatus "Berlaku" tersimpan di `data/regulations/`, 127 relasi di `data/edges.json`, cross-check Kemnaker cocok untuk 101/166.
- **Temuan nyata dari cross-check**: 7 peraturan punya status berbeda antara BPK ("Berlaku") dan Kemnaker ("Tidak Berlaku") — lihat daftar di [`docs/decisions.md`](decisions.md). Ini bukan bug, tapi perbedaan data antar sumber yang perlu ditampilkan apa adanya di situs nanti (sesuai aturan bahasa netral).
- **Keterbatasan yang ditemukan, perlu diperbaiki di Fase 2**: dari 65 peraturan yang tidak cocok di Kemnaker, sebagian ternyata cocok saat dicek ulang satu-satu manual (misal Permenaker No. 20/2024 dan No. 19/2022) — menunjukkan `kemnaker.find_detail_url()` kadang gagal menemukan hasil yang sebenarnya ada (flaky, bukan konsisten tidak ada). Jangan anggap `pembanding: null` di data saat ini sebagai bukti final "tidak ada di Kemnaker".

## Fase 2 — Deteksi perubahan dan otomatisasi
**Status**: Selesai (2026-10-07)

- **Keputusan desain** (lihat [`docs/decisions.md`](decisions.md)): peraturan yang pernah tersimpan terus dilacak apa pun statusnya sekarang (bukan cuma yang "Berlaku"), supaya transisi status tercatat sebagai perubahan, bukan hilang diam-diam. Hash SHA-256 PDF dihitung tiap scrape untuk deteksi `pdf_berubah`.
- `lawtrail/changes.py`: bandingkan data lama vs baru → entri `baru`/`status_berubah`/`relasi_berubah`/`pdf_berubah`/`hilang`, ditulis ke `data/changes/{tanggal}.json`. Skema didokumentasikan di [`docs/schema.md`](schema.md). 6 unit test lulus.
- `run_scrape.py` gagal jelas (exit code 1) kalau 0 peraturan ditemukan di crawl penuh — indikasi struktur situs sumber berubah.
- `.github/workflows/scrape.yml`: jadwal harian + `workflow_dispatch`, commit otomatis dengan email no-reply kalau `data/`/`raw/` berubah.
- **Simulasi perubahan diverifikasi**: status satu peraturan diubah manual jadi "Dicabut (simulasi)", scraper dijalankan ulang untuk peraturan itu saja, dan `data/changes/{tanggal}.json` berisi entri `status_berubah` yang benar (sebelum/sesudah) — lalu file simulasi itu dihapus lagi supaya arsip tidak berisi data palsu.
- **Bug ditemukan & diperbaiki selama simulasi**: deteksi "hilang" sempat salah menandai ratusan peraturan sebagai hilang saat scraper dijalankan dengan `--limit` (karena hanya sebagian daftar yang benar-benar dicek). Sekarang deteksi "hilang" dilewati kalau `--limit` dipakai.
- **Catatan**: workflow GitHub Actions belum pernah benar-benar dijalankan di GitHub (perlu push ke repo dulu, lihat kendala git CLI di bawah) — hanya diverifikasi logikanya secara lokal.
- **Gap data yang disengaja (disetujui pemilik proyek)**: 166 regulasi dari scraping penuh Fase 1 (sebelum field `pdf_sha256` ditambah) belum punya hash PDF — hanya 1 (hasil simulasi Fase 2) yang sudah. Dibiarkan dulu demi tidak membebani server BPK/Kemnaker untuk ketiga kalinya dalam sehari; akan terisi otomatis begitu scraper jalan lagi (GitHub Actions terjadwal, atau jalan manual kapan saja).

## Fase 3 — Situs statis
**Status**: Selesai (2026-10-07)

- Situs Astro di [`site/`](../site/): daftar peraturan (`/`), halaman detail per peraturan (`/peraturan/{id}/` — metadata, status primer+pembanding, relasi berlink, riwayat perubahan, tautan sumber+PDF, tanggal terakhir dicek), log perubahan gabungan (`/perubahan/`), RSS perubahan (`/rss.xml`), pencarian Pagefind di halaman daftar. CSS polos responsif (tanpa framework besar).
- Data dibaca langsung dari `../data/` lewat `site/src/lib/data.js` — tidak ada duplikasi data ke dalam `site/`.
- `npm run build` dari `site/` menghasilkan 168 halaman statis + indeks Pagefind; diverifikasi lokal dengan `npm run preview` (index, 1 halaman detail, `/perubahan/`, `/rss.xml`, aset Pagefind semua merespons 200).
- `.github/workflows/build-site.yml` — build CI (belum deploy, itu Fase 5), diverifikasi logikanya lokal (belum pernah jalan sungguhan di GitHub, sama seperti workflow Fase 2 — masih terhalang git CLI).
- **Bug build-time yang ditemukan & diperbaiki**: `src/lib/data.js` awalnya memakai `import.meta.url` untuk menemukan folder `data/` — bekerja di `astro dev` tapi diam-diam mengembalikan 0 peraturan saat `astro build` (Vite membundel ulang modul, jadi `import.meta.url` tidak lagi menunjuk ke lokasi asli). Akibatnya seluruh route `/peraturan/{id}/` hilang dari hasil build tanpa pesan error apa pun. Diganti ke resolusi berbasis `process.cwd()`. Lihat catatan di `site/README.md`.
- **Belum pasti**: domain final belum ada (`astro.config.mjs` masih placeholder `lawtrail.example`, dipakai RSS) — akan diisi di Fase 5 saat hosting diputuskan.

## Fase 4 — Peta relasi
**Status**: Belum dimulai

- Graf per peraturan dengan Cytoscape.js: pusat + tetangga 1–2 langkah, perluasan lewat klik, gaya garis berbeda per jenis relasi, panel detail, penanganan simpul omnibus, filter jenis relasi.
- Selesai bila: peraturan dengan banyak relasi tetap terbaca.

## Fase 5 — Metodologi dan persiapan rilis
**Status**: Belum dimulai

- Halaman metodologi dan batasan, disclaimer terlihat, halaman kontak/koreksi, README kontributor.
- Selesai bila: semua halaman siap ditinjau orang berlatar hukum.
