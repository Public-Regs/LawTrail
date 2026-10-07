# LawTrail

Arsip dan pelacak perubahan peraturan perundang-undangan Indonesia — situs statis tanpa server, tanpa AI, tanpa database. Tahap awal: Peraturan Menteri Ketenagakerjaan.

## Status proyek

Fase 0 (pengintaian sumber dan fondasi repo) selesai. Lihat [`docs/PLAN.md`](docs/PLAN.md) untuk status tiap fase dan [`docs/source-recon.md`](docs/source-recon.md) untuk temuan pengintaian sumber data.

## Tujuan

- Mengambil data peraturan dari portal JDIH resmi, menyimpan versi dan relasinya (mengubah, mencabut, diubah oleh, dicabut oleh), lalu menampilkannya sebagai situs statis dengan riwayat perubahan, pencarian, dan peta relasi interaktif.
- Ditujukan untuk masyarakat awam yang ingin tahu status dan riwayat sebuah peraturan — bukan nasihat hukum.

## Arsitektur

- **Tanpa server**: Git sebagai sumber kebenaran data. Pengambilan data berjalan terjadwal lewat GitHub Actions; situs statis dihosting di Cloudflare Pages atau GitHub Pages.
- **Sumber data**: primer `peraturan.bpk.go.id`, pembanding `jdih.kemnaker.go.id`. Lihat alasan di [`docs/decisions.md`](docs/decisions.md).
- **Struktur repo**:
  - `raw/` — salinan mentah halaman sumber sebagai bukti pengambilan.
  - `data/regulations/` — satu JSON per peraturan.
  - `data/edges.json` — relasi antar peraturan.
  - `data/changes/` — log perubahan terdeteksi.
  - `scripts/` — scraper dan alat deteksi perubahan.
  - `site/` — generator situs statis.
  - `docs/` — dokumentasi proyek.

## Aturan proyek

Aturan lengkap (etika scraping, batasan arsitektur, gaya kerja per-fase) ada di [`CLAUDE.md`](CLAUDE.md).

## Lisensi

Kode dalam repo ini berlisensi [MIT](LICENSE). PDF asli peraturan tidak disimpan di Git (hanya metadata, hash SHA-256, dan URL sumber) dan tetap mengikuti ketentuan hak cipta negara/sumber aslinya.
