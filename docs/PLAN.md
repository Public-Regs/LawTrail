# Rencana fase LawTrail

Status per fase. Diperbarui setiap fase selesai agar bisa dilanjutkan di sesi baru.

## Fase 0 — Pengintaian sumber dan fondasi repo
**Status**: Selesai (2026-10-07)

- Pengintaian jdih.kemnaker.go.id dan peraturan.bpk.go.id: lihat [`docs/source-recon.md`](source-recon.md).
- Keputusan sumber primer/pembanding dan kontak scraper: lihat [`docs/decisions.md`](decisions.md).
- Kerangka repo (README, LICENSE, CLAUDE.md, struktur folder) dibuat.
- **Belum pasti, perlu dicek di awal Fase 1**: apakah jdih.kemnaker.go.id benar-benar tidak punya PDF teks lengkap Permenaker (lihat "Hal yang masih terbuka" di source-recon.md).

## Fase 1 — Skema data dan scraper
**Status**: Belum dimulai

- Rancang skema JSON peraturan dan `data/edges.json` (usulkan dulu, tunggu persetujuan pemilik proyek).
- Verifikasi manual temuan Fase 0 (lihat catatan reliabilitas di source-recon.md) sebelum menulis parser.
- Scraper untuk daftar dan halaman detail, simpan `raw/` dan `data/` terpisah, dengan cache dan retry sopan (jeda ≥2 detik, patuh robots.txt).
- Selesai bila: seluruh target terambil, dan menjalankan ulang scraper tanpa perubahan di sumber tidak menghasilkan perubahan file apa pun.

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
