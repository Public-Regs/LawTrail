import { getAllRegulations, getEdges } from "../lib/data.js";

// Graf statis untuk peta relasi (Fase 4) -- dimuat sekali oleh klien,
// traversal 1-2 langkah dan perluasan lewat klik dihitung di browser
// (lihat src/lib/graph-client.js) supaya tidak perlu fetch berulang.
export function GET() {
  const nodes = getAllRegulations().map((reg) => ({
    id: reg.id,
    nomor: reg.nomor,
    tahun: reg.tahun,
    judul: reg.judul,
    status: reg.status,
  }));
  const edges = getEdges();

  return new Response(JSON.stringify({ nodes, edges }), {
    headers: { "Content-Type": "application/json" },
  });
}
