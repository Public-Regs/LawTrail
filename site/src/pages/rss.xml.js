import rss from "@astrojs/rss";
import { getAllChanges, getAllRegulations, CHANGE_LABELS } from "../lib/data.js";

export function GET(context) {
  const titleById = new Map(
    getAllRegulations().map((r) => [r.id, `Permenaker No. ${r.nomor} Tahun ${r.tahun}`]),
  );
  const changes = getAllChanges();

  return rss({
    title: "LawTrail — Riwayat Perubahan Peraturan Menteri Ketenagakerjaan",
    description: "Perubahan status, relasi, dan dokumen Permenaker yang terdeteksi otomatis.",
    site: context.site ?? "https://lawtrail.example",
    items: changes.map((entry) => ({
      title: `${titleById.get(entry.id) ?? entry.id} — ${CHANGE_LABELS[entry.type] ?? entry.type}`,
      link: `/peraturan/${entry.id}/`,
      pubDate: new Date(entry.date),
      description: JSON.stringify(entry.detail ?? {}),
    })),
  });
}
