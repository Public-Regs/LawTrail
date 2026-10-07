# Skema data

## `data/regulations/{id}.json`

`{id}` adalah slug dari peraturan.bpk.go.id (sumber primer), contoh: `permenaker-no-11-tahun-2022`.

```json
{
  "id": "permenaker-no-11-tahun-2022",
  "jenis": "Peraturan Menteri Ketenagakerjaan",
  "nomor": "11",
  "tahun": 2022,
  "judul": "Peraturan Menteri Ketenagakerjaan Nomor 11 Tahun 2022 tentang Tata Cara Pembentukan Peraturan Menteri Ketenagakerjaan",
  "tempat_penetapan": "Jakarta",
  "tanggal_penetapan": "2022-06-10",
  "tanggal_pengundangan": "2022-06-13",
  "tanggal_berlaku": "2022-06-13",
  "status": "Berlaku",
  "subjek": ["PEMBENTUKAN PERATURAN"],
  "sumber_pengundangan": "BN.2022/No.896, peraturan.go.id: 10 hlm.",
  "primer": {
    "situs": "peraturan.bpk.go.id",
    "id_situs": 231405,
    "url": "https://peraturan.bpk.go.id/Details/231405/permenaker-no-11-tahun-2022",
    "pdf_url": "https://peraturan.bpk.go.id/Download/264901/Permenaker%20Nomor%2011%20Tahun%202022.pdf",
    "pdf_sha256": "..."
  },
  "pembanding": {
    "situs": "jdih.kemnaker.go.id",
    "id_situs": 2219,
    "url": "https://jdih.kemnaker.go.id/peraturan/detail/2219/...",
    "status": "Berlaku",
    "status_cocok": true
  },
  "relations": [
    {
      "type": "mencabut",
      "target_id": "permenaker-no-7-tahun-2020",
      "target_title": "Permenaker No. 7 Tahun 2020 tentang ...",
      "target_url": "https://peraturan.bpk.go.id/Details/.../permenaker-no-7-tahun-2020",
      "sumber": "bpk"
    }
  ]
}
```

Catatan:
- `pembanding` boleh `null` kalau tidak ditemukan peraturan yang cocok di jdih.kemnaker.go.id (bukan error — hanya dicatat sebagai tidak ketemu).
- Field relasi (`relations[].type`) memakai salah satu dari 5 nilai: `mengubah`, `diubah_dengan`, `mencabut`, `dicabut_dengan`, `menetapkan`. `target_id` boleh `null` kalau target tidak punya link (misal peraturan kolonial "Staatsblad").
- **Tidak ada field tanggal pengambilan/`fetched_at` di file ini** — sesuai aturan di [`CLAUDE.md`](../CLAUDE.md). Tanggal "terakhir dicek" disimpan di `data/last-checked.json` (lihat di bawah), dan file ini hanya ditulis ulang bila isinya (selain tanggal) benar-benar berubah.

## `data/edges.json`

Daftar relasi flat untuk dipakai Cytoscape.js (Fase 4), dibangkitkan dari union `relations[]` semua file di `data/regulations/`:

```json
[
  { "from": "permenaker-no-11-tahun-2022", "to": "permenaker-no-7-tahun-2020", "type": "mencabut", "source": "bpk" }
]
```

File ini dibangkitkan otomatis oleh scraper (bukan ditulis manual) — jangan diedit langsung.

## `data/last-checked.json`

```json
{
  "permenaker-no-11-tahun-2022": "2026-10-07"
}
```

Satu file, map id → tanggal terakhir dicek. Diupdate setiap kali scraper jalan, terlepas dari apakah isi peraturan berubah atau tidak.

## `data/changes/{tanggal}.json`

Dibangkitkan otomatis oleh `scripts/run_scrape.py` (Fase 2) — satu file per tanggal jalan, hanya ditulis kalau ada perubahan hari itu. Array berisi entri dengan salah satu `type`:

```json
[
  { "id": "permenaker-no-5-tahun-2026", "type": "baru", "detail": { "status": "Berlaku" } },
  { "id": "permenaker-no-11-tahun-2022", "type": "status_berubah", "detail": { "sebelum": "Berlaku", "sesudah": "Dicabut" } },
  { "id": "permenaker-no-8-tahun-2022", "type": "relasi_berubah", "detail": { "ditambahkan": [...], "dihapus": [...] } },
  { "id": "permenaker-no-3-tahun-2021", "type": "pdf_berubah", "detail": { "sebelum": "sha256...", "sesudah": "sha256..." } },
  { "id": "permenaker-no-9-tahun-2015", "type": "hilang", "detail": {} }
]
```

Catatan:
- Begitu sebuah peraturan pernah tersimpan di `data/regulations/`, ia **terus dilacak** di scrape berikutnya apa pun statusnya sekarang (lihat [`docs/decisions.md`](decisions.md)) — jadi transisi status tercatat sebagai `status_berubah`, bukan file yang hilang diam-diam.
- `hilang` dipakai khusus untuk peraturan yang sudah pernah tersimpan tapi sama sekali tidak muncul lagi di daftar sumber (kemungkinan dihapus dari situs) — bukan untuk peraturan yang sekadar berubah status.
- `pdf_berubah` hanya dicatat kalau kedua hash (`sebelum` dan `sesudah`) berhasil dihitung; kalau salah satu gagal diunduh, tidak dianggap perubahan.
