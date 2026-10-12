# Aturan proyek LawTrail

Arsip dan pelacak perubahan peraturan perundang-undangan Indonesia, berupa situs statis tanpa server.

## Batasan arsitektur (wajib)

- Tanpa VPS dan tanpa database server di jalur produksi. Git adalah sumber kebenaran data.
- Pengambilan data berjalan terjadwal lewat GitHub Actions. Situs statis dihosting di Cloudflare Pages atau GitHub Pages.
- Struktur repo: `raw/` (salinan mentah sumber sebagai bukti), `data/regulations/` (satu JSON per peraturan), `data/edges.json` (relasi), `data/changes/` (log perubahan), `scripts/`, `site/`, `docs/`.
- Jangan commit PDF asli ke Git; simpan hanya metadata, hash SHA-256, dan URL sumber.
- Jangan menambah dependensi besar tanpa diskusi lebih dulu.

## Aturan etika dan hukum (wajib)

- Patuhi `robots.txt` setiap sumber. Beri jeda antar request minimal 2 detik. Jangan paralel secara agresif.
- User-Agent scraper: `Lawtrail/0.1 (+hiramaulana@users.noreply.github.com)`.
- Bahasa netral: tampilkan fakta dan sumber saja. Jangan menulis frasa seperti "diam-diam diubah", jangan menyimpulkan apa yang "berlaku" di luar yang tertulis di sumber, jangan menyusun versi terkonsolidasi/opini.
- Setiap halaman di situs wajib menautkan ke sumber resmi dan menampilkan tanggal pengambilan data.
- Jangan commit tanggal pengambilan ke file peraturan itu sendiri. Simpan "terakhir dicek" di file terpisah; ubah file peraturan hanya bila isinya benar-benar berubah.
- Jangan mencantumkan data pribadi di commit, kode, atau dokumen. Gunakan email no-reply GitHub (`hiramaulana@users.noreply.github.com`) untuk commit otomatis.

## Cara kerja

1. Kerjakan satu fase pada satu waktu; status tiap fase ada di [`PLAN.md`](PLAN.md).
2. Jangan berasumsi soal struktur situs sumber — periksa HTML-nya langsung sebelum menulis atau mengubah parser.
3. Commit kecil dan sering dengan pesan yang jelas. Tambahkan test untuk parser dan logika deteksi perubahan.
4. Catat keputusan penting di [`decisions.md`](decisions.md) dan status fase di [`PLAN.md`](PLAN.md).
5. Kode dan komentar dalam bahasa Inggris; teks yang tampil di situs dan halaman metodologi dalam bahasa Indonesia.

## Referensi

- Temuan pengintaian sumber: [`source-recon.md`](source-recon.md).
- Sumber primer: `peraturan.bpk.go.id`. Sumber pembanding: `jdih.kemnaker.go.id`. Alasan di [`decisions.md`](decisions.md).
