# Berkontribusi ke LawTrail

Terima kasih sudah tertarik membantu. Aturan lengkap proyek ada di [`CLAUDE.md`](CLAUDE.md) — baca itu dulu, terutama bagian etika scraping dan "cara kerja" (satu fase per waktu, tunggu persetujuan sebelum perubahan besar).

## Menjalankan scraper secara lokal

```
cd scripts
pip install -r requirements.txt
python run_scrape.py --limit 5   # uji coba dengan jumlah kecil dulu
```

Lihat [`scripts/README.md`](scripts/README.md) untuk opsi lengkap dan [`docs/schema.md`](docs/schema.md) untuk skema data.

**Jangan** menjalankan scraper tanpa `--limit` secara berulang-ulang untuk eksperimen — itu membebani server peraturan.bpk.go.id dan jdih.kemnaker.go.id. Jeda sopan (≥2 detik antar request) sudah otomatis diterapkan, tapi tetap hindari menjalankan scraping penuh lebih dari yang perlu.

## Menjalankan situs secara lokal

```
cd site
npm install
npm run dev
```

Lihat [`site/README.md`](site/README.md) untuk detail build, preview, dan catatan implementasi (termasuk hal-hal yang sengaja dibuat dengan cara tertentu — jangan diubah tanpa memahami alasannya).

## Menjalankan test

```
cd scripts && python -m pytest tests/ -v
```

## Struktur data

`data/` adalah sumber kebenaran — jangan mengedit file di `data/regulations/` atau `data/edges.json` secara manual, semuanya dibangkitkan oleh scraper. Kalau menemukan data yang salah, perbaiki di parser (`scripts/lawtrail/`) lalu jalankan ulang scraper untuk peraturan yang bersangkutan, bukan mengedit file JSON-nya langsung.

## Melaporkan kesalahan data (bukan bug kode)

Kalau kamu menemukan ketidaksesuaian antara data di situs dan sumber resminya, laporkan lewat [GitHub Issues](https://github.com/Public-Regs/LawTrail/issues) — lihat juga halaman [Koreksi](https://Public-Regs.github.io/LawTrail/koreksi/) di situs untuk panduan lengkap.

## Komitmen etika (wajib, tidak bisa dinegosiasikan)

- Patuhi `robots.txt` setiap sumber baru yang ditambahkan.
- Jangan menyimpan PDF asli ke Git.
- Jangan mencantumkan data pribadi (email, nama asli) di commit, kode, atau dokumen manapun — pakai email no-reply.
- Bahasa di situs harus netral: fakta dan tautan sumber saja, tidak menyimpulkan status hukum atau menulis opini.
