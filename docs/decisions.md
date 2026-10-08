# Catatan keputusan proyek

Format: tanggal, keputusan, alasan. Tambahkan entri baru di bagian atas (terbaru dulu).

## 2026-10-08 — Pindah ke GitHub Organization

**Keputusan**: Repo dipindah dari akun personal ke organisasi GitHub `Public-Regs` — URL repo sekarang `https://github.com/Public-Regs/LawTrail`.

**Dampak**: `astro.config.mjs` (`site`), link GitHub Issues di `/koreksi/` dan `CONTRIBUTING.md`, serta remote git lokal (`.git/config`) diupdate dari `hiramaulana/LawTrail` ke `Public-Regs/LawTrail`. Email commit no-reply (`hiramaulana@users.noreply.github.com`) **tidak diubah** — itu melekat ke akun personal sebagai committer, bukan ke nama repo/organisasi.

## 2026-10-07 — Temuan: perbedaan status antar sumber (hasil scraping penuh Fase 1)

**Bukan keputusan, tapi temuan data** yang perlu ditangani dengan hati-hati karena menyentuh aturan "bahasa netral": dari 166 Permenaker yang berstatus "Berlaku" di peraturan.bpk.go.id, 101 cocok dicek ke jdih.kemnaker.go.id, dan di antaranya **7 punya status berbeda** (BPK: "Berlaku", Kemnaker: "Tidak Berlaku"):

- Permenaker No. 10 Tahun 2017
- Permenaker No. 11 Tahun 2017
- Permenaker No. 12 Tahun 2018
- Permenaker No. 13 Tahun 2018
- Permenaker No. 24 Tahun 2018
- Permenaker No. 5 Tahun 2019
- Permenaker No. 8 Tahun 2022

**Sikap proyek**: sesuai aturan di [`CLAUDE.md`](../CLAUDE.md), LawTrail tidak menyimpulkan status mana yang "benar" — kedua status ditampilkan apa adanya di `data/regulations/{id}.json` (field `status` dari primer, `pembanding.status` dari Kemnaker) beserta tanggal pengambilan, dan nanti di situs sebagai fakta dari masing-masing sumber dengan link ke keduanya.

**Catatan reliabilitas cross-check (diperbarui setelah investigasi)**: 65 dari 166 Permenaker awalnya tidak ketemu pasangannya di Kemnaker. `lawtrail.kemnaker.find_detail_url()` lalu diberi retry (3x, jeda 3 detik) untuk kasus "tidak ketemu", karena beberapa pengujian manual awal (bukan dari 65 ini, tapi pengujian terpisah) menunjukkan server Kemnaker bisa sesekali mengembalikan hasil kosong. Setelah 65 kasus itu diperiksa ulang dengan retry: **hanya 1 yang ternyata ketemu** (Permenaker No. 21 Tahun 2022), 64 sisanya tetap tidak ketemu meski 3x percobaan. Simpulan: sebagian besar dari 65 itu memang genuinely tidak terindeks di Kemnaker (konsisten dengan temuan Permenaker No. 6 Tahun 2012 yang juga tidak pernah ketemu) — bukan flaky secara massal, hanya ada sedikit kasus transient. Retry tetap dipertahankan di kode karena murah dan terbukti menangkap minimal 1 kasus nyata.

## 2026-10-07 — Skema data, cakupan scraping, dan cara cross-check Kemnaker

**Keputusan**:
- `data/regulations/{id}.json` memakai slug BPK sebagai id, dengan blok `primer` (BPK) dan `pembanding` (Kemnaker, boleh `null`), serta `relations[]` beranotasi `type`/`target_id`/`sumber`.
- `data/edges.json` dibangkitkan otomatis (bukan ditulis manual) dari union seluruh `relations[]`.
- Fase 1 hanya mengambil dan menyimpan Permenaker yang statusnya "Berlaku" di peraturan.bpk.go.id (filter `jenis=105`). Peraturan yang sudah dicabut tetap muncul sebagai `target_id` di relasi peraturan lain, tapi file JSON-nya sendiri belum dibuat — bisa ditambah di iterasi berikutnya kalau dibutuhkan riwayat peraturan tidak berlaku.
- Cross-check Kemnaker memakai pencarian kata kunci (`?keyword=Peraturan Menteri Ketenagakerjaan Nomor {n} Tahun {t}`) lalu dicocokkan ulang lewat slug persis, karena parameter `nomor=`/`tahun=` di `jdih.kemnaker.go.id` terbukti tidak benar-benar memfilter hasil saat diuji langsung.

**Alasan**: Disetujui pemilik proyek lewat opsi "Setuju, lanjutkan" dan "Semua Permenaker yang masih berlaku" (lihat ringkasan Fase 1 di [`PLAN.md`](PLAN.md)). Pendekatan keyword+slug untuk Kemnaker dipilih setelah pengujian langsung menunjukkan filter query param-nya tidak berfungsi seperti yang diharapkan.

## 2026-10-07 — Kontak User-Agent dan email commit

**Keputusan**: Pakai `hiramaulana@users.noreply.github.com` sebagai kontak di header `User-Agent` scraper (`Lawtrail/0.1 (+hiramaulana@users.noreply.github.com)`) dan sebagai email commit Git.

**Alasan**: Aturan proyek melarang mencantumkan data pribadi pemilik proyek. Email no-reply bawaan GitHub memberi jalur kontak yang valid tanpa membocorkan email pribadi.

## 2026-10-07 — Sumber primer dan pembanding

**Keputusan**: `peraturan.bpk.go.id` sebagai sumber primer untuk pengambilan data Peraturan Menteri Ketenagakerjaan; `jdih.kemnaker.go.id` sebagai sumber pembanding.

**Alasan**: Dari pengintaian Fase 0 (lihat [`docs/source-recon.md`](source-recon.md)), peraturan.bpk.go.id menyediakan PDF teks lengkap dan daftar relasi (`Mengubah`, `Diubah dengan`, `Mencabut`, `Menetapkan`) yang lebih lengkap sebagai link HTML langsung. jdih.kemnaker.go.id adalah sumber resmi penerbit (Kemnaker langsung), jadi tetap dipakai untuk verifikasi status dan metadata resmi, meski halaman detailnya yang diperiksa belum menunjukkan PDF teks lengkap peraturan.

**Catatan**: Keputusan ini bisa direvisi di Fase 1 jika verifikasi manual menunjukkan temuan Fase 0 tidak akurat (lihat bagian "Hal yang masih terbuka" di source-recon.md).
