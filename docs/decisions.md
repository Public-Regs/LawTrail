# Catatan keputusan proyek

Format: tanggal, keputusan, alasan. Tambahkan entri baru di bagian atas (terbaru dulu).

## 2026-10-07 — Kontak User-Agent dan email commit

**Keputusan**: Pakai `hiramaulana@users.noreply.github.com` sebagai kontak di header `User-Agent` scraper (`Lawtrail/0.1 (+hiramaulana@users.noreply.github.com)`) dan sebagai email commit Git.

**Alasan**: Aturan proyek melarang mencantumkan data pribadi pemilik proyek. Email no-reply bawaan GitHub memberi jalur kontak yang valid tanpa membocorkan email pribadi.

## 2026-10-07 — Sumber primer dan pembanding

**Keputusan**: `peraturan.bpk.go.id` sebagai sumber primer untuk pengambilan data Peraturan Menteri Ketenagakerjaan; `jdih.kemnaker.go.id` sebagai sumber pembanding.

**Alasan**: Dari pengintaian Fase 0 (lihat [`docs/source-recon.md`](source-recon.md)), peraturan.bpk.go.id menyediakan PDF teks lengkap dan daftar relasi (`Mengubah`, `Diubah dengan`, `Mencabut`, `Menetapkan`) yang lebih lengkap sebagai link HTML langsung. jdih.kemnaker.go.id adalah sumber resmi penerbit (Kemnaker langsung), jadi tetap dipakai untuk verifikasi status dan metadata resmi, meski halaman detailnya yang diperiksa belum menunjukkan PDF teks lengkap peraturan.

**Catatan**: Keputusan ini bisa direvisi di Fase 1 jika verifikasi manual menunjukkan temuan Fase 0 tidak akurat (lihat bagian "Hal yang masih terbuka" di source-recon.md).
