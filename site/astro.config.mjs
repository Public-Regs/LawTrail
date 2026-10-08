// @ts-check
import { defineConfig } from 'astro/config';

// GitHub Pages untuk repo "LawTrail" (bukan repo khusus username.github.io)
// terbit di subpath /LawTrail/, bukan di root domain -- karena itu `base`
// diisi di sini. Semua link internal di kode sudah lewat helper
// `src/lib/base.js` supaya tetap benar baik di subpath ini maupun kalau
// nanti pindah ke domain khusus (base: '/').
export default defineConfig({
  site: 'https://Public-Regs.github.io',
  base: '/LawTrail',
});
