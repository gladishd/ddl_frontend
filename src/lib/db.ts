/* ---------------------------------------------------------------------
 *  Database helpers for the Dædælus document library
 *  – now prunes stale rows so ghost-PDF links disappear automatically.
 * --------------------------------------------------------------------*/

import { Pool } from "pg";
import fs from "fs";
import path from "path";
import { DocumentRecord } from "@/types/Document";

/* ────────────────────────── 1. Postgres connection ─────────────────── */
const connectionString = process.env.DATABASE_URL as string;
if (!connectionString) throw new Error("DATABASE_URL is not set");

const pool = new Pool({
  connectionString,
  ssl: /render\.com/.test(connectionString)
    ? { rejectUnauthorized: false }
    : undefined,
});

/* ────────────────────────── 2. document manifest ───────────────────── */
type DocMeta = { file: string; title: string; description?: string };

const PDF_META: DocMeta[] = [
  {
    file: "Packct-Spraying.pdf",
    title: "Packct Spraying",
    description: "Technical notes on packet-spraying attack simulations."
  },
  { file: "Bandwidth-Works-in-Practice-not-in-Theory.pdf", title: "Bandwidth Works in Practice, Not in Theory" },
  { file: "Latex-Files-and-Colors.numbers.pdf", title: "LaTeX - File Types and Color Tags" },
  { file: "main.pdf", title: "Packet Switching - Historical Context" },
  { file: "main2.pdf", title: "Critique of Bandwidth-First Design" },
  { file: "main3.pdf", title: "Packet Switching - Extended Notes" },
  { file: "Metcalfe+Boggs.pdf", title: "Ethernet: Metcalfe and Boggs (1976)" },
  { file: "NDA-Dean-Gladish-2025-06-04_23-06.pdf", title: "Non-Disclosure Agreement (Dean Gladish)" },
  { file: "OAE_Logo_copy.pdf", title: "OAE Logo (Vector PDF)" },
  { file: "Omni-Figure-1.pdf", title: "Legacy Ethernet Topology (Omni Fig 1)" },
  { file: "Reinventing-Reliability-at-L2.pdf", title: "Reinventing Reliability at Layer 2" },
  { file: "template_copy.pdf", title: "Network Topology Models (Baran)" },
  { file: "TEST-Ethernet-Figures.pdf", title: "Ethernet - Core Figures" },
  { file: "test.pdf", title: "Emulator and Testbed Notes" },
  { file: "Welcome-Dean.pdf", title: "Welcome, Dean" },
  { file: "Mac-Mini-Network-Configuration.pdf", title: "Mac Mini Network Configuration" },
  {
    file: "Multiscale-Field-Theory-for-Network-Flows-PhysRevX.15.021044.pdf",
    title: "Multiscale Field Theory for Network Flows (PRX 15 021044)",
  },
  {
    file: "Reliable-Full-Duplex-File-Transmission-over-Half-Duplex-Telephone-Lines-363347.363366.pdf",
    title: "Reliable Full-Duplex File Tx over Half-Duplex Lines",
  },
  {
    file: "A-Note-on-Reliable-Full-Duplex-Transmission-over-Half-Duplex-Links-362946.362970.pdf",
    title: "Note on Full-Duplex over Half-Duplex Links",
  },
  { file: "CASE.pdf", title: "CASE White-paper" },
  { file: "single-computer-testing.pdf", title: "Single-Computer Testing Methodology" },
  { file: "main-resend-Sahas.pdf", title: "Packet Switching (Re-send Draft – Sahas)" },
  { file: "Daedaelus-agent-based-Ethernet.screencapture.pdf", title: "Daedaelus Agent-Based Ethernet (ChatGPT capture)" },
  {
    file: "FMS-CTO-Panel-2025.pdf",
    title: "FMS CTO Panel (2025)",
    description: "Presentation for the Future of Memory and Storage CTO panel.",
  },
  {
    file: "Welcome-Wolfram.pdf",
    title: "Welcome to Wolfram",
    description: "Introduction to Dædælus for Mathematica programmers.",
  },
  {
    file: "LaTeX-vs-Markdown-for-a-Scientific-Document-Repository.pdf",
    title: "LaTeX vs Markdown for Scientific Docs",
    description: "Guidance on documentation standards, comparing LaTeX and Markdown.",
  },
  {
    file: "Instructions-for-Daedaelus.pdf",
    title: "Instructions for Dædælus",
    description: "Internal notes and instructions related to the Dædælus project.",
  },
  {
    file: "FAQ-GVM.pdf",
    title: "FAQ – Graph Virtual Machine (GVM)",
    description: "Frequently asked questions on the design and usage of the Graph Virtual Machine.",
  },
  {
    file: "Bennett_Reversibility.pdf",
    title: "Reversibility & Time-Reversible Computing",
    description: "Charles H. Bennett’s foundational paper on logical reversibility and thermodynamics of computation."
  },
  // ─── new 2025-07 additions ───
  /* ――― NEW ENTRIES (Daedalus New) ――― */
  {
    file: "OAE-SPEC-MAIN.pdf",
    title: "Open Atomic Ethernet Specification",
    description: "The main specification document for the Open Atomic Ethernet (OAE) workstream, detailing its principles, architecture, and protocols.",
  },
  {
    file: "Instructions for Daedaelus.pdf",
    title: "Daedaelus Project Instructions",
    description: "Internal project notes, tasks, and discussions related to the Daedaelus platform and its development.",
  },
  {
    file: "main-resend-Sahas.pdf",
    title: "Bandwidth Works in Practice, not in Theory (Sahas Resend)",
    description: "A version of the core Daedaelus thesis on reliable networking, challenging the industry's focus on bandwidth over transactional integrity.",
  },
  {
    file: "Finite-Automata.pdf",
    title: "Finite Automata and Decision Problems",
    description: "A deep dive into the theory of finite automata, their decision problems, and their foundational role in computer science.",
  },
  {
    file: "Mulligan-Stew-FAQ.pdf",
    title: "Mulligan Stew FAQ",
    description: "A compilation of questions and detailed answers from the Daedaelus team, clarifying core concepts like atomicity, problem space, and architectural principles.",
  },
  {
    file: "simon_wacker_graphFSP.pdf",
    title: "Time-Optimal Firing Squad/Mob Synchronisation",
    description: "Simon Wacker's paper on a time-optimal quasi-solution of the firing mob synchronisation problem on connected graphs.",
  },
  {
    file: "1402958.1402967.pdf",
    title: "A Scalable, Commodity Data Center Network Architecture",
    description: "The influential 2008 SIGCOMM paper proposing a scalable data center architecture using fat-tree topologies with commodity switches.",
  },
  {
    file: "PatHellandQuestions.pdf",
    title: "Pat Helland's Questions (Mulligan Stew FAQ)",
    description: "A focused FAQ addressing specific, challenging questions from Pat Helland regarding the core problem and definition of atomicity.",
  },
  { file: "DeansPresentation.pdf", title: "Dean Gladish – Keynote Slides" },
  { file: "OCP-OAE-02025-EVOLVING.pdf", title: "OCP-OAE 2025 – Evolving Interconnects" },
  { file: "CellularAutomata-FromClassicalComputationtoQuantumErrorCorrection.pdf", title: "Cellular Automata – Classical to Quantum EC" },
  { file: "aethernet_talk_final.pdf", title: "Æthernet Talk (final)" },
  {
    file: "TheDistributedFiringSquadProblem-AReviewofTemporalInconsistenciesBetweenComputationandPhysics.pdf",
    title: "Distributed Firing-Squad – Temporal Inconsistencies"
  },
  { file: "PUF_Talk.pdf", title: "PUF Talk" },
  { file: "Demolition2.pdf", title: "Demolition 2" },
  { file: "TR25-017.pdf", title: "Technical Report TR25-017" },
  { file: "LIPIcs.CCC.2022.8.pdf", title: "LIPIcs CCC 2022 §8" },
  { file: "Square-Root-Space.pdf", title: "Square-Root Space" },
  { file: "Graph-Report.pdf", title: "Graph Report" },
  { file: "PastedGraphic-1.png", title: "Inline Graphic 1" },
  { file: "PastedGraphic-3.png", title: "Inline Graphic 3" },
  { file: "GuQqVMxbwAAMg4t.jpeg", title: "Æthernet Poster (JPEG)" },
  { file: "01_principles-of_operation.pdf", title: "Principles of Operation (01)" },
  { file: "DistributedFiringSquadcopy-BN.pdf", title: "Distributed Firing-Squad (BN copy)" },
  { file: "Screenshot2025-07-02at7.13.40PM.png", title: "UI Screenshot (2025-07-02 19-13-40)" },
  /* ――― 2025-07-09 additions ――― */
  {
    file: "QCA.pdf",
    title: "Quantum Cellular Automata (QCA) Primer",
    description: "Survey linking classical CA to quantum information processing."
  },
  {
    file: "RDMA-Meta.pdf",
    title: "RDMA Meta-Protocol",
    description: "Design notes for an RDMA-accelerated meta-protocol in Ethernet 2025."
  },
  {
    file: "TAP120_Set-Reconcilliation-Pat-Daniel.pdf",
    title: "TAP #120 — Set Reconciliation (Pat & Daniel)",
    description: "Time Appliances Project episode 120: provably-safe set reconciliation."
  },
  {
    file: "3623490_HammingMesh:_A_Network_Topology_for_Large-Scale_Deep_Learning.pdf",
    title: "HammingMesh: A Topology for Deep Learning",
    description: "A novel network topology optimized for large-scale deep learning, balancing high bandwidth, cost, and flexibility.",
  },
  /* ――― 2025-07-13 additions ――― */
  {
    file: "PastedGraphic-1_(1).png",
    title: "Cost and Bandwidth Comparison",
    description: "Detailed comparison of network topologies from the HammingMesh paper."
  },
  {
    file: "Welcome-David.pdf",
    title: "Welcome, David – Dædælus Intro",
    description: "Introductory document outlining the core problems Daedaelus addresses."
  },
  {
    file: "Chiplet-Mesh-Networking-02024-Apr-18.pdf",
    title: "Chiplet Mesh Networking (Apr 2024)",
    description: "Presentation on applying graph theory to chiplet mesh networks."
  },
  {
    file: "promela_modeling.pdf",
    title: "PROMELA Modeling for FSP",
    description: "Using PROMELA to model the Firing Squad Problem."
  },
  {
    file: "Dual-SAW-Spekkens.pdf",
    title: "Dual SAW Petri-Spekkens Protocol",
    description: "Details the Dual Stop-and-Wait protocol using Petri Nets and the Spekkens Toy Model for epistricted consistency.",
  },
  {
    file: "Ethernet2022.pdf",
    title: "The Evolution of Ethernet (2022)",
    description: "A 2022 perspective on Ethernet's evolution, challenging classic assumptions and proposing optimizations for latency over bandwidth.",
  },
  {
    file: "Information-Surprise.pdf",
    title: "Information is a Surprise",
    description: "Explores the concept that information is surprisal and must be paired, applying it to network protocols.",
  },
  {
    file: "Liveness_Tensor.pdf",
    title: "Liveness Tensor",
    description: "Describes a transitively coherent data structure for liveness awareness in directly connected datacenter networks.",
  },
  {
    file: "Requirements-Charlie-2.pdf",
    title: "Project Requirements (Charlie-2)",
    description: "Core requirements for the Daedaelus project, including hardware targets and protocol state machine principles.",
  },
  {
    file: "Slice-Engine.pdf",
    title: "Slice Engine Specification",
    description: "Defines the protocol for processing 8-byte slices, confinement, and port-addressing solutions.",
  },
  {
    file: "State-Machine-Specification.pdf",
    title: "State Machine Specification",
    description: "Defines the reversible state machine models, including 1-state, 2-state, and 4-state transfer protocols.",
  },
  {
    file: "Superposition-Engine.pdf",
    title: "Superposition Engine",
    description: "Details the MORTS (Morphism pORTS) Open Petri Net Model for managing connected information and event ordering.",
  },
  /* ――― New Entries ――― */
  {
    file: "Slowdown-Theorem-on-Links-FILE_3981.pdf",
    title: "Slowdown Theorem on Links",
    description: "Critiques 'Forward-In-Time-Only' thinking and proposes a reversible link protocol model that accounts for indefinite causality.",
  },
  {
    file: "DAE-FAQ-Bandwidth_20230709a.pdf",
    title: "FAQ – Bandwidth",
    description: "Compares the bandwidth and resilience of the Daedaelus Transaction Fabrix with conventional Clos networks.",
  },
  {
    file: "FAQ-Latency-2-copy.pdf",
    title: "FAQ – Latency",
    description: "Explores the predictable, low-latency characteristics of the Transaction Fabrix versus the tail latency of switched networks.",
  },
  { file: "Arista.pdf", title: "Arista" },
  { file: "Clos-Fabric.graffle.pdf", title: "Clos Fabric (OmniGraffle export)" },
  { file: "ConventionalNetworking.pdf", title: "Conventional Networking" },
  { file: "Old-Animated.pdf", title: "Ethernet Animation (legacy)" },
  { file: "Tranzaction-Processing-Spec.pdf", title: "Transaction Processing Spec" },
];

// /* ────────────────────────── 3. Self-seeding + GC with "first-time" create_document_features.sql ───────────────────── */
// let seeded = false;

// async function ensureDocuments() {
//   if (seeded) return;

//   // Before interacting with the database, we must ensure the foundational schema exists.
//   // We read our canonical schema from the SQL file and apply it. This makes the system
//   // self-sufficient, capable of initializing its own data layer from a blueprint.
//   const client = await pool.connect();
//   try {
//     const schemaSql = fs.readFileSync(path.join(process.cwd(), 'create_document_features.sql'), 'utf-8');
//     await client.query(schemaSql);

//     // Now proceed with the reversible subtransaction to sync the documents.
//     const publicDir = path.join(process.cwd(), "public");
//     const exists = (f: string) => fs.existsSync(path.join(publicDir, f));

//     const validMeta = PDF_META.filter(m => exists(m.file));
//     const currentHrefs = validMeta.map(m => `/${m.file}`);

//     await client.query("BEGIN");

//     for (const { file, title, description } of validMeta) {
//       await client.query(
//         `INSERT INTO documents (title, description, href)
//          VALUES ($1, $2, $3)
//          ON CONFLICT (href) DO NOTHING;`,
//         [title, description ?? null, `/${file}`],
//       );
//     }

//     await client.query(
//       `DELETE FROM documents
//         WHERE href <> ALL ($1::text[]);`,
//       [currentHrefs],
//     );

//     await client.query("COMMIT");
//     seeded = true; // Mark as seeded only after a successful full run
//   } catch (err) {
//     await client.query("ROLLBACK");
//     console.error("Failed to seed/prune documents:", err);
//     throw err;
//   } finally {
//     client.release();
//   }
// }

/* ────────────────────────── 3. Self-seeding + GC ───────────────────── */
let seeded = false;

async function ensureDocuments() {
  if (seeded) return;
  seeded = true;

  const publicDir = path.join(process.cwd(), "public");
  const exists = (f: string) => fs.existsSync(path.join(publicDir, f));

  const validMeta = PDF_META.filter(m => exists(m.file));          // only files that truly exist
  const currentHrefs = validMeta.map(m => `/${m.file}`);           // ['/file.pdf', …]

  const client = await pool.connect();
  try {
    await client.query("BEGIN");

    /* 3-a  insert / update the canonical set */
    for (const { file, title, description } of validMeta) {
      await client.query(
        `INSERT INTO documents (title, description, href)
         VALUES ($1, $2, $3)
         ON CONFLICT (href) DO NOTHING;`,
        [title, description ?? null, `/${file}`],
      );
    }

    /* 3-b  garbage-collect anything that isn’t in the manifest          */
    await client.query(
      `DELETE FROM documents
        WHERE href <> ALL ($1::text[]);`,
      [currentHrefs],
    );

    await client.query("COMMIT");
  } catch (err) {
    await client.query("ROLLBACK");
    console.error("Failed to seed/prune documents:", err);
    throw err;
  } finally {
    client.release();
  }
}

/* ────────────────────────── 4. Public helpers ──────────────────────── */
export async function listDocuments(): Promise<DocumentRecord[]> {
  await ensureDocuments();

  const { rows } = await pool.query(`
    SELECT  d.*,
            COALESCE(l.count, 1)  AS likes,
            COALESCE(v.count, 1)  AS views,
            COALESCE(
              (SELECT array_agg(tag)
                 FROM document_tags t
                WHERE t.document_id = d.id),
              '{}'::text[]
            )                      AS tags
      FROM documents          d
 LEFT JOIN document_likes l ON l.document_id = d.id
 LEFT JOIN document_views v ON v.document_id = d.id
  ORDER BY d.id;
  `);

  return rows;
}

export async function incLike(id: number) {
  await pool.query(
    `INSERT INTO document_likes (document_id, count)
       VALUES ($1, 11)
       ON CONFLICT (document_id) DO UPDATE
         SET count = document_likes.count + 1;`,
    [id],
  );
}

export async function incView(id: number) {
  await pool.query(
    `INSERT INTO document_views (document_id, count)
       VALUES ($1, 21)
       ON CONFLICT (document_id) DO UPDATE
         SET count = document_views.count + 1;`,
    [id],
  );
}

export async function setTags(id: number, tags: string[]) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query("DELETE FROM document_tags WHERE document_id = $1;", [id]);

    if (tags.length) {
      const values = tags.map((_, i) => `($1, $${i + 2})`).join(", ");
      await client.query(
        `INSERT INTO document_tags (document_id, tag) VALUES ${values};`,
        [id, ...tags],
      );
    }

    await client.query("COMMIT");
  } catch (e) {
    await client.query("ROLLBACK");
    throw e;
  } finally {
    client.release();
  }
}
/* psql "postgresql://ddl_database_3_user:PkAC1BE0W4lB1dzgJ8aM422LpU1DNBQc@dpg-d2e4lpqdbo4c73emr7t0-a.ohio-postgres.render.com/ddl_database_3" -f create_document_features.sql
// psql "postgresql://ddl_database_3_user:PkAC1BE0W4lB1dzgJ8aM422LpU1DNBQc@dpg-d2e4lpqdbo4c73emr7t0-a.ohio-postgres.render.com/ddl_database_3" -f seed_documents.sql
//  */