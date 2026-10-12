# site/

Situs statis LawTrail, dibangun dengan [Astro](https://astro.build). Membaca data langsung dari `../data/` (lihat `src/lib/data.js`) — tidak ada data yang disalin ke dalam `site/`.

## Setup

```
npm install
```

## Development

```
npm run dev
```

Buka `http://localhost:4321`. Catatan: pencarian (Pagefind) tidak aktif di mode dev — indeksnya baru dibuat saat `npm run build` (langkah `postbuild`).

## Build

```
npm run build
```

Menghasilkan `dist/` (halaman statis) dan menjalankan Pagefind untuk membuat indeks pencarian di `dist/pagefind/`. Preview hasil build:

```
npm run preview
```

## Struktur

- `src/lib/data.js` — baca `data/regulations/`, `data/edges.json`, `data/changes/`, `data/last-checked.json` dari root repo.
- `src/pages/index.astro` — daftar peraturan + kotak pencarian Pagefind.
- `src/pages/peraturan/[id].astro` — halaman detail per peraturan (metadata, status, relasi, riwayat perubahan, link sumber).
- `src/pages/perubahan/index.astro` — log perubahan gabungan semua peraturan.
- `src/pages/rss.xml.js` — feed RSS dari `data/changes/`.
- `src/pages/graph.json.js` — endpoint statis berisi seluruh node+edge untuk peta relasi (Fase 4).
- `src/lib/graph-client.js` — logika Cytoscape.js sisi klien (traversal 1-2 hop, perluasan klik, clustering simpul omnibus, filter jenis relasi), dipakai oleh `peraturan/[id].astro`.

## Catatan implementasi

- `src/lib/data.js` sengaja memakai `process.cwd()` (bukan `import.meta.url`) untuk menemukan folder `data/` — Vite membundel ulang modul ini saat `astro build`, dan `import.meta.url` hasil bundling tidak lagi menunjuk ke lokasi file asli, sehingga path yang dihitung darinya salah dan diam-diam mengembalikan 0 peraturan (hanya saat build, bukan saat `astro dev`). Kalau butuh ubah lokasi file ini, jangan balik ke pendekatan `import.meta.url`.
- Skrip Pagefind di `index.astro` memakai `<script is:inline src="...">` biasa, bukan `import()` dinamis — supaya Vite tidak mencoba me-resolve file itu saat build (baru ada setelah langkah `postbuild`).
- `graph-client.js`: simpul yang dikelompokkan (cluster, untuk relasi >5 jenis yang sama dari satu peraturan) hanya dibentuk dari pasangan simpul yang SUDAH tampil di radius saat itu (lihat komentar di fungsi `computeElements`) — jadi memecah cluster tidak pernah butuh menarik node baru dari luar radius. Set `forcedVisible` tetap dipertahankan sebagai jaga-jaga (defensive), bukan karena dibutuhkan oleh alur normal saat ini.
- Deploy (Cloudflare Pages/GitHub Pages) belum disiapkan — itu bagian Fase 5. `astro.config.mjs` masih memakai `site: 'https://lawtrail.example'` sebagai placeholder untuk RSS; ganti begitu domain final diputuskan.
