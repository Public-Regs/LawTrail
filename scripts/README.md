# scripts/

Scraper Python untuk Peraturan Menteri Ketenagakerjaan. Sumber primer: `peraturan.bpk.go.id`. Sumber pembanding (cross-check status): `jdih.kemnaker.go.id`. Lihat [`../docs/source-recon.md`](../docs/source-recon.md) dan [`../docs/schema.md`](../docs/schema.md).

## Setup

```
pip install -r requirements.txt
```

## Menjalankan scraper

Dari folder `scripts/`:

```
python run_scrape.py
```

Opsi:
- `--no-kemnaker` — lewati cross-check ke jdih.kemnaker.go.id (lebih cepat untuk uji coba lokal).
- `--limit N` — hanya proses N peraturan pertama (untuk uji coba).

Scraper akan:
1. Mengambil daftar semua Peraturan Menteri Ketenagakerjaan dari `peraturan.bpk.go.id` (filter `jenis=105`).
2. Untuk peraturan yang statusnya "Berlaku" **atau** sudah pernah tersimpan sebelumnya (supaya transisi status tetap terlacak, lihat `docs/decisions.md`): ambil detail, hitung hash SHA-256 PDF-nya, simpan HTML mentah ke `../raw/bpk/{id}.html`, cross-check status ke Kemnaker (kecuali `--no-kemnaker`), tulis `../data/regulations/{id}.json`.
3. Membandingkan data lama vs baru per peraturan dan menulis entri perubahan (`baru`/`status_berubah`/`relasi_berubah`/`pdf_berubah`/`hilang`) ke `../data/changes/{tanggal}.json` (hanya dibuat kalau ada perubahan).
4. Membangun ulang `../data/edges.json` dari seluruh relasi yang tersimpan.
5. Mencatat tanggal pengambilan ke `../data/last-checked.json`.
6. Keluar dengan exit code 1 kalau tidak ada satu pun peraturan ditemukan di crawl penuh (indikasi struktur situs berubah) — supaya GitHub Actions menandai run sebagai gagal.

File JSON hanya ditulis ulang bila isinya (selain `last-checked.json`) benar-benar berubah — menjalankan ulang scraper tanpa perubahan di sumber seharusnya tidak menghasilkan diff apa pun di `data/regulations/`.

**Catatan soal `--limit`**: deteksi "hilang" (peraturan yang sudah tidak muncul di sumber) secara sengaja dilewati saat `--limit` dipakai, karena hanya sebagian daftar yang benar-benar dicek — tanpa ini, peraturan yang belum dikunjungi akan keliru tercatat "hilang".

## Otomatisasi (GitHub Actions)

`.github/workflows/scrape.yml` menjalankan scraper setiap hari (`workflow_dispatch` juga tersedia untuk trigger manual) dan commit otomatis ke `data/` + `raw/` kalau ada perubahan, memakai email no-reply (lihat `docs/decisions.md`). Workflow ini belum pernah dijalankan sungguhan di GitHub — perlu repo ini di-push dulu.

## Menjalankan test

```
python -m pytest tests/ -v
```

Test parser memakai fixture HTML nyata di `tests/fixtures/` (hasil pengambilan sungguhan dari peraturan.bpk.go.id, bukan HTML buatan), supaya kalau struktur situs berubah, scraper gagal diuji secara jelas dan cepat.

## Catatan

- Permenaker yang statusnya bukan "Berlaku" dan belum pernah tersimpan sebelumnya tidak diambil — tapi begitu tersimpan sekali, perubahan status berikutnya (termasuk jadi dicabut) tetap diupdate dan dicatat di `data/changes/`.
- Kemnaker (`jdih.kemnaker.go.id`) dicocokkan lewat pencarian kata kunci + nomor/tahun, dengan retry 3x kalau tidak ketemu (server kadang mengembalikan hasil kosong sesaat). Kalau tetap tidak ketemu, `pembanding` diisi `null` (bukan error) — mayoritas kasus ini genuinely tidak terindeks di Kemnaker, bukan bug (lihat `docs/decisions.md`).
