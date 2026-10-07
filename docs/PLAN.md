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
**Status**: Belum dimulai

- Deteksi dokumen baru, perubahan status/relasi, perubahan hash, dokumen yang hilang; tulis ke `data/changes/`.
- GitHub Actions terjadwal harian: jalankan scraper, commit otomatis bila ada perubahan, gagal jelas (notifikasi) bila struktur sumber berubah.
- Selesai bila: simulasi perubahan menghasilkan commit dan log yang benar.

## Fase 3 — Situs statis
**Status**: Belum dimulai

- Daftar peraturan, halaman detail (metadata, status, relasi, riwayat, tautan sumber), pencarian Pagefind, RSS perubahan, responsif di ponsel.
- Selesai bila: situs bisa di-build lokal dan di CI, dipakai tanpa penjelasan.

## Fase 4 — Peta relasi
**Status**: Belum dimulai

- Graf per peraturan dengan Cytoscape.js: pusat + tetangga 1–2 langkah, perluasan lewat klik, gaya garis berbeda per jenis relasi, panel detail, penanganan simpul omnibus, filter jenis relasi.
- Selesai bila: peraturan dengan banyak relasi tetap terbaca.

## Fase 5 — Metodologi dan persiapan rilis
**Status**: Belum dimulai

- Halaman metodologi dan batasan, disclaimer terlihat, halaman kontak/koreksi, README kontributor.
- Selesai bila: semua halaman siap ditinjau orang berlatar hukum.
