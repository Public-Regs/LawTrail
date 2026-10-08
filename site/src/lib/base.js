// Astro mengisi BASE_URL otomatis dari `base` di astro.config.mjs (selalu
// diakhiri "/", misal "/" di root atau "/LawTrail/" kalau situs dipasang di
// subpath GitHub Pages). Pakai helper ini untuk SEMUA link/asset absolut
// internal (bukan link ke situs luar) supaya situs tetap benar baik di root
// domain maupun di subpath -- jangan hardcode "/xxx" langsung.
const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

export function url(path) {
  return `${BASE}${path}`;
}
