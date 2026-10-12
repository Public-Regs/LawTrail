import cytoscape from "cytoscape";
import { url } from "./base.js";

export const RELATION_STYLE = {
  mengubah: { color: "#0b4f8a", style: "dashed", label: "Mengubah" },
  diubah_dengan: { color: "#0b4f8a", style: "dashed", label: "Diubah dengan" },
  mencabut: { color: "#a32f1f", style: "solid", label: "Mencabut" },
  dicabut_dengan: { color: "#a32f1f", style: "solid", label: "Dicabut dengan" },
  menetapkan: { color: "#4a7c2f", style: "dotted", label: "Menetapkan" },
};

const CLUSTER_THRESHOLD = 5; // >5 relasi jenis yang sama dari satu simpul -> dikelompokkan
const HOPS = 2;

function buildAdjacency(edges) {
  const adj = new Map(); // id -> [{ other, type }]
  for (const e of edges) {
    if (!adj.has(e.from)) adj.set(e.from, []);
    if (!adj.has(e.to)) adj.set(e.to, []);
    adj.get(e.from).push({ other: e.to, type: e.type });
    adj.get(e.to).push({ other: e.from, type: e.type });
  }
  return adj;
}

function neighborsWithinHops(adj, centerId, hops) {
  const visited = new Set([centerId]);
  let frontier = [centerId];
  for (let h = 0; h < hops; h++) {
    const next = [];
    for (const id of frontier) {
      for (const link of adj.get(id) ?? []) {
        if (!visited.has(link.other)) {
          visited.add(link.other);
          next.push(link.other);
        }
      }
    }
    frontier = next;
  }
  return visited;
}

function nodeLabel(node) {
  return node ? `No. ${node.nomor}/${node.tahun}` : "?";
}

export async function initGraph({ containerId, panelId, legendId, filterFormId, centerId }) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const res = await fetch(url("/graph.json"));
  const { nodes, edges } = await res.json();
  const nodesById = new Map(nodes.map((n) => [n.id, n]));
  const adj = buildAdjacency(edges);

  const extraSeeds = new Set(); // node yang diklik di luar radius awal -> tampilkan tetangganya juga
  const brokenClusters = new Set(); // `${nodeId}:${type}` yang sudah dipecah jadi node satu-satu
  const forcedVisible = new Set(); // anggota cluster yang sudah dipecah, supaya tetap tampil walau di luar radius
  let activeTypes = new Set(Object.keys(RELATION_STYLE));

  function visibleIds() {
    const within = neighborsWithinHops(adj, centerId, HOPS);
    const visible = new Set(within);
    for (const seed of extraSeeds) {
      visible.add(seed);
      for (const link of adj.get(seed) ?? []) visible.add(link.other);
    }
    for (const id of forcedVisible) visible.add(id);
    return visible;
  }

  function computeElements() {
    const visible = visibleIds();
    const elements = [];
    const addedNodes = new Set();
    const clusterCount = new Map(); // `${nodeId}:${type}` -> { count, members }

    function addNode(id, data = {}) {
      if (addedNodes.has(id)) return;
      addedNodes.add(id);
      elements.push({ data: { id, ...data } });
    }

    addNode(centerId, { label: nodeLabel(nodesById.get(centerId)), isCenter: true });
    for (const id of visible) {
      if (id !== centerId) addNode(id, { label: nodeLabel(nodesById.get(id)) });
    }

    // Hitung dulu ukuran kelompok per (simpul, jenis) di antara simpul yang tampil,
    // supaya relasi yang jumlahnya banyak bisa dikelompokkan (simpul omnibus).
    for (const e of edges) {
      if (!activeTypes.has(e.type)) continue;
      if (!visible.has(e.from) || !visible.has(e.to)) continue;
      const key = `${e.from}:${e.type}`;
      if (!clusterCount.has(key)) clusterCount.set(key, { count: 0, members: [] });
      const c = clusterCount.get(key);
      c.count += 1;
      c.members.push(e.to);
    }

    const shownEdgeKeys = new Set();
    for (const e of edges) {
      if (!activeTypes.has(e.type)) continue;
      if (!visible.has(e.from) || !visible.has(e.to)) continue;

      const clusterKey = `${e.from}:${e.type}`;
      const group = clusterCount.get(clusterKey);
      const shouldCluster = group.count > CLUSTER_THRESHOLD && !brokenClusters.has(clusterKey);

      if (shouldCluster) {
        const nodeId = `cluster:${clusterKey}`;
        addNode(nodeId, {
          isCluster: true,
          clusterKey,
          count: group.count,
          members: group.members,
          type: e.type,
          label: `+${group.count} (${RELATION_STYLE[e.type]?.label ?? e.type})`,
        });
        const edgeKey = `${e.from}->${nodeId}`;
        if (!shownEdgeKeys.has(edgeKey)) {
          shownEdgeKeys.add(edgeKey);
          elements.push({ data: { id: edgeKey, source: e.from, target: nodeId, type: e.type } });
        }
      } else {
        const edgeKey = `${e.from}->${e.to}:${e.type}`;
        if (!shownEdgeKeys.has(edgeKey)) {
          shownEdgeKeys.add(edgeKey);
          elements.push({ data: { id: edgeKey, source: e.from, target: e.to, type: e.type } });
        }
      }
    }

    return elements;
  }

  const cy = cytoscape({
    container,
    elements: computeElements(),
    style: [
      {
        selector: "node",
        style: {
          label: "data(label)",
          "font-size": 9,
          "text-valign": "center",
          "background-color": "#dbe7f2",
          "border-width": 1,
          "border-color": "#0b4f8a",
          width: 36,
          height: 36,
          "text-wrap": "wrap",
          "text-max-width": "60px",
        },
      },
      {
        selector: "node[?isCenter]",
        style: { "background-color": "#0b4f8a", color: "#fff", width: 48, height: 48 },
      },
      {
        selector: "node[?isCluster]",
        style: {
          "background-color": "#f0d9d4",
          "border-color": "#a32f1f",
          shape: "round-rectangle",
          width: 70,
          height: 32,
        },
      },
      ...Object.entries(RELATION_STYLE).map(([type, s]) => ({
        selector: `edge[type = "${type}"]`,
        style: {
          "line-color": s.color,
          "target-arrow-color": s.color,
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          "line-style": s.style,
          width: 2,
        },
      })),
    ],
    layout: { name: "cose", animate: false },
  });

  function rerender() {
    cy.elements().remove();
    cy.add(computeElements());
    cy.layout({ name: "cose", animate: false }).run();
  }

  function showPanel(node) {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    if (!node) {
      panel.innerHTML = "<p>Klik sebuah simpul untuk melihat detail.</p>";
      return;
    }
    if (node.data("isCluster")) {
      panel.innerHTML = `<p>${node.data("label")} &mdash; klik untuk memecah jadi peraturan satu per satu.</p>`;
      return;
    }
    const info = nodesById.get(node.id());
    if (!info) {
      panel.innerHTML = `<p>${node.id()}</p>`;
      return;
    }
    panel.innerHTML = `
      <p><strong>Permenaker No. ${info.nomor} Tahun ${info.tahun}</strong></p>
      <p>${info.judul}</p>
      <p><span class="badge ${info.status === "Berlaku" ? "status-berlaku" : "status-lain"}">${info.status}</span></p>
      <p><a href="${url(`/peraturan/${info.id}/`)}">Buka halaman detail &rarr;</a></p>
    `;
  }

  cy.on("tap", "node", (evt) => {
    const node = evt.target;
    showPanel(node);

    if (node.data("isCluster")) {
      brokenClusters.add(node.data("clusterKey"));
      for (const memberId of node.data("members") ?? []) forcedVisible.add(memberId);
      rerender();
      return;
    }

    // Klik simpul mana pun memperluas graf dengan menampilkan tetangganya juga.
    if (!extraSeeds.has(node.id())) {
      extraSeeds.add(node.id());
      rerender();
    }
  });

  cy.on("tap", (evt) => {
    if (evt.target === cy) showPanel(null);
  });

  showPanel(null);

  const legend = document.getElementById(legendId);
  if (legend) {
    legend.innerHTML = Object.entries(RELATION_STYLE)
      .map(
        ([type, s]) =>
          `<span class="legend-item"><span class="legend-line legend-${s.style}" style="border-color:${s.color}"></span> ${s.label}</span>`,
      )
      .join("");
  }

  const form = document.getElementById(filterFormId);
  if (form) {
    form.addEventListener("change", () => {
      const checked = [...form.querySelectorAll("input[type=checkbox]:checked")].map((el) => el.value);
      activeTypes = new Set(checked);
      rerender();
    });
  }

  return cy;
}
