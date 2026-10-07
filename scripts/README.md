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
2. Untuk tiap peraturan yang statusnya "Berlaku": ambil detail, simpan HTML mentah ke `../raw/bpk/{id}.html`, cross-check status ke Kemnaker (kecuali `--no-kemnaker`), tulis `../data/regulations/{id}.json`.
3. Membangun ulang `../data/edges.json` dari seluruh relasi yang tersimpan.
4. Mencatat tanggal pengambilan ke `../data/last-checked.json`.

File JSON hanya ditulis ulang bila isinya (selain `last-checked.json`) benar-benar berubah — menjalankan ulang scraper tanpa perubahan di sumber seharusnya tidak menghasilkan diff apa pun di `data/regulations/`.

## Menjalankan test

```
python -m pytest tests/ -v
```

Test parser memakai fixture HTML nyata di `tests/fixtures/` (hasil pengambilan sungguhan dari peraturan.bpk.go.id, bukan HTML buatan), supaya kalau struktur situs berubah, scraper gagal diuji secara jelas dan cepat.

## Catatan

- Permenaker yang statusnya bukan "Berlaku" dilewati di Fase 1 ini (lihat `docs/decisions.md`) — scraper tetap mencatatnya di relasi target (misal `mencabut`) meski file JSON-nya sendiri tidak dibuat.
- Kemnaker (`jdih.kemnaker.go.id`) dicocokkan lewat pencarian kata kunci + nomor/tahun; kalau tidak ketemu, `pembanding` diisi `null` (bukan error).
