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

/* ────────────────────────── 2. PDF manifest ────────────────────────── */
type DocMeta = { file: string; title: string; description?: string };

const PDF_META: DocMeta[] = [
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
];

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
            COALESCE(l.count, 10)  AS likes,
            COALESCE(v.count, 20)  AS views,
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
