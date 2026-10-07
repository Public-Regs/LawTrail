// Membaca data langsung dari data/ di root repo (bukan disalin ke site/),
// supaya data/ tetap satu-satunya sumber kebenaran (lihat root CLAUDE.md).
//
// Sengaja TIDAK memakai import.meta.url untuk mencari lokasi file ini:
// Vite membundel modul ini saat `astro build`, dan import.meta.url hasil
// bundling tidak lagi menunjuk ke lokasi source asli, jadi path yang
// dihitung darinya salah (resolusi ke 0 peraturan, tapi hanya saat build,
// tidak saat `astro dev` -- butuh waktu lama untuk ditemukan). process.cwd()
// stabil di kedua mode karena `astro dev`/`astro build` selalu dijalankan
// dari folder site/.
import { readFileSync, readdirSync, existsSync } from "node:fs";
import path from "node:path";

const REPO_ROOT = path.resolve(process.cwd(), "..");
const DATA_DIR = path.join(REPO_ROOT, "data");

function readJson(filePath, fallback) {
  if (!existsSync(filePath)) return fallback;
  return JSON.parse(readFileSync(filePath, "utf-8"));
}

export function getAllRegulations() {
  const dir = path.join(DATA_DIR, "regulations");
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => readJson(path.join(dir, f), null))
    .filter(Boolean)
    .sort((a, b) => (b.tahun - a.tahun) || (Number(b.nomor) - Number(a.nomor)));
}

export function getRegulation(id) {
  return readJson(path.join(DATA_DIR, "regulations", `${id}.json`), null);
}

export function getEdges() {
  return readJson(path.join(DATA_DIR, "edges.json"), []);
}

export function getLastChecked(id) {
  const all = readJson(path.join(DATA_DIR, "last-checked.json"), {});
  return all[id] ?? null;
}

export function getAllChanges() {
  const dir = path.join(DATA_DIR, "changes");
  if (!existsSync(dir)) return [];
  const entries = [];
  for (const file of readdirSync(dir).filter((f) => f.endsWith(".json")).sort().reverse()) {
    const date = file.replace(/\.json$/, "");
    const dayEntries = readJson(path.join(dir, file), []);
    for (const entry of dayEntries) {
      entries.push({ ...entry, date });
    }
  }
  return entries;
}

export function getChangesForRegulation(id) {
  return getAllChanges().filter((entry) => entry.id === id);
}

export const RELATION_LABELS = {
  mengubah: "Mengubah",
  diubah_dengan: "Diubah dengan",
  mencabut: "Mencabut",
  dicabut_dengan: "Dicabut dengan",
  menetapkan: "Menetapkan",
};

export const CHANGE_LABELS = {
  baru: "Peraturan baru ditambahkan ke arsip",
  status_berubah: "Status berubah",
  relasi_berubah: "Relasi berubah",
  pdf_berubah: "Dokumen PDF berubah",
  hilang: "Tidak lagi ditemukan di sumber",
};
