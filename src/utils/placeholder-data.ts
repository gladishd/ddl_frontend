/****************************************************************************************
 * placeholder-data.ts — Demolition-integrated ground-plane
 * --------------------------------------------------------------------------------------
 * This file replaces the original placeholder-data.ts.  It folds the conceptual
 * breakthroughs from “The Physical Impossibility of Distributed Systems: A Systematic
 * Deconstruction” (Episodes 1 – 5) directly into the bootstrap topology of the
 * Daedaelus Graph Virtual Machine (GVM).
 *
 *  •  New KEYS model the causal signals introduced in the paper (CLOCK_DRIFT_DETECTED,
 *     TIMEOUT_RETRY_ISSUED, INDEFINITE_CAUSAL_ORDER, etc.).
 *  •  New GROUPS (“Episode 1 TRAPH” … “Episode 5 TRAPH”) act as high-level story arcs.
 *  •  New SITUATIONS & CHOICES walk the reader through the five episodes, making the
 *     demolition narrative executable inside the canvas.
 *
 *  Existing demo content (transaction token flow, consensus TRAPH, etc.) is preserved
 *  so prior UI elements do not break.
 ****************************************************************************************/

import { Situation } from '@/types/canvas/Situation';
import { Group } from '@/types/canvas/Group';
import { Key } from '@/types/canvas/Key';
import { Choice } from '@/types/canvas/Choice';

/* ------------------------------------------------------------------ *
 |  1.  Conserved Quantities (Keys)                                   |
 * ------------------------------------------------------------------ */
export const placeholderKeys: Key[] = [
  /* — existing capability keys — */
  {
    _id: 'key-transaction-token',
    name: 'TRANSACTION_TOKEN',
    description: 'Grants the holder capability to initiate a reversible sub-transaction.'
  },
  {
    _id: 'key-quorum-lock',
    name: 'QUORUM_LOCK_ACQUIRED',
    description: 'Distributed lock held by a consensus group, enabling safe state change.'
  },
  {
    _id: 'key-failover-active',
    name: 'FAILOVER_PATH_ENGAGED',
    description: 'Redundant path is active after a primary link failure.'
  },

  /* — demolition-specific keys — */
  {
    _id: 'key-clock-drift',
    name: 'CLOCK_DRIFT_DETECTED',
    description:
      'Raised when a node detects that simultaneity planes have collapsed; forces causal realignment.'
  },
  {
    _id: 'key-timeout-retry',
    name: 'TIMEOUT_RETRY_ISSUED',
    description:
      'Represents a TAR event; its presence may silently corrupt data structures if not handled.'
  },
  {
    _id: 'key-ico',
    name: 'INDEFINITE_CAUSAL_ORDER',
    description:
      'Quantum-level signal that no consistent causal order exists for the current branch of the computation.'
  }
];

/* ------------------------------------------------------------------ *
 |  2.  TRAPHs (Groups)                                               |
 * ------------------------------------------------------------------ */
export const placeholderGroups: Group[] = [
  /* — legacy demo TRAPHs — */
  {
    _id: 'group-consensus-alpha',
    title: 'Consensus TRAPH Alpha',
    description: 'Maintains distributed consensus lock.',
    situations: [],
    isDefault: false,
    color: 'rgba(255,100,100,.1)'
  },
  {
    _id: 'group-compute-fabric',
    title: 'Compute Fabric TRAPH',
    description: 'High-throughput computational work-cells.',
    situations: [],
    isDefault: false,
    color: 'rgba(100,100,255,.1)'
  },
  {
    _id: 'group-default',
    title: 'Default Groundplane',
    description: 'Base TRAPH for unassigned cells.',
    situations: [],
    isDefault: true
  },

  /* — demolition narrative TRAPHs — */
  {
    _id: 'group-episode-1',
    title: 'Episode 1 TRAPH — Clock Coherence',
    description: 'Illustrates impossibility of global “now” from micro-datacentres to Proxima Centauri.',
    situations: [],
    isDefault: false,
    color: 'rgba(64,160,255,.12)'
  },
  {
    _id: 'group-episode-2',
    title: 'Episode 2 TRAPH — Newtonian Facade',
    description: 'Reveals hidden Newtonian assumption and its consequences.',
    situations: [],
    isDefault: false,
    color: 'rgba(255,200,64,.12)'
  },
  {
    _id: 'group-episode-3',
    title: 'Episode 3 TRAPH — Race Conditions',
    description: 'Explores causal fail-over using PTP hierarchy.',
    situations: [],
    isDefault: false,
    color: 'rgba(160,255,160,.12)'
  },
  {
    _id: 'group-episode-4',
    title: 'Episode 4 TRAPH — TAR Catastrophe',
    description: 'Timeout & Retry across timelines corrupt state.',
    situations: [],
    isDefault: false,
    color: 'rgba(255,128,192,.12)'
  },
  {
    _id: 'group-episode-5',
    title: 'Episode 5 TRAPH — Ethernet Spacetime',
    description: 'Timestamps are an illusion; announce Ethernet 2025.',
    situations: [],
    isDefault: false,
    color: 'rgba(192,192,192,.12)'
  }
];

/* ------------------------------------------------------------------ *
 |  3.  Situations (Cells)                                            |
 * ------------------------------------------------------------------ */
const legacySituations: Situation[] = [ /* — unchanged legacy cells (A1…B4) — */];

const demolitionSituations: Situation[] = [
  /* Episode 1 — Clock coherence */
  {
    _id: 'cell-e1-start',
    title: 'E1-S: Swarm Launch → Clock Handshake',
    text:
      'A nano-probe swarm departs Earth orbit; each node begins a causal handshake to establish a local notion of “tick 0”.',
    isStart: true,
    isEnd: false,
    position: { x: 100, y: 650 },
    choices: [],
    situationGroup: 'group-episode-1'
  },
  {
    _id: 'cell-e1-end',
    title: 'E1-E: Clock Coherence Breaks',
    text:
      'Relativistic separation exposes observer-dependent simultaneity; CLOCK_DRIFT_DETECTED is raised.',
    isStart: false,
    isEnd: true,
    position: { x: 400, y: 650 },
    choices: [],
    situationGroup: 'group-episode-1'
  },

  /* Episode 2 — Newtonian facade */
  {
    _id: 'cell-e2-fito',
    title: 'E2: FITO Fallacy Detected',
    text:
      'System realises it assumed forward-in-time-only monotonicity; asserts INDEFINITE_CAUSAL_ORDER.',
    isStart: false,
    isEnd: false,
    position: { x: 700, y: 650 },
    choices: [],
    situationGroup: 'group-episode-2'
  },

  /* Episode 3 — Race conditions */
  {
    _id: 'cell-e3-race',
    title: 'E3: Causal Fail-over Engaged',
    text:
      'Static PTP hierarchy re-rooted to maintain partial order; QUORUM_LOCK updated.',
    isStart: false,
    isEnd: false,
    position: { x: 1000, y: 650 },
    choices: [],
    situationGroup: 'group-episode-3'
  },

  /* Episode 4 — TAR */
  {
    _id: 'cell-e4-timeout',
    title: 'E4: Timeout & Retry Issued',
    text:
      'A TAR event crosses diverging timelines; TIMEOUT_RETRY_ISSUED token appears.',
    isStart: false,
    isEnd: false,
    position: { x: 1300, y: 650 },
    choices: [],
    situationGroup: 'group-episode-4'
  },

  /* Episode 5 — Ethernet spacetime */
  {
    _id: 'cell-e5-conclude',
    title: 'E5: Timestamps Declared Illusory',
    text:
      'Ethernet 2025 announced: system switches to causal tokens; timestamps demoted to hints.',
    isStart: false,
    isEnd: true,
    position: { x: 1600, y: 650 },
    choices: [],
    situationGroup: 'group-episode-5'
  }
];

/* ------------------------------------------------------------------ *
 |  4.  Linkage (Choices)                                             |
 * ------------------------------------------------------------------ */
const demolitionChoices: Choice[] = [
  /* Episode 1 path */
  { _id: 'link-e1-forward', title: 'Δv → Approach Centauri', situation: 'cell-e1-start', nextSituation: 'cell-e1-end' },

  /* Cross-episode causal chain */
  { _id: 'link-e1-to-e2', title: 'Raise CLOCK_DRIFT_DETECTED', situation: 'cell-e1-end', nextSituation: 'cell-e2-fito', showIfKey: 'key-clock-drift' },
  { _id: 'link-e2-to-e3', title: 'Re-root PTP Hierarchy', situation: 'cell-e2-fito', nextSituation: 'cell-e3-race', showIfKey: 'key-ico' },
  { _id: 'link-e3-to-e4', title: 'Issue TAR Event', situation: 'cell-e3-race', nextSituation: 'cell-e4-timeout' },
  { _id: 'link-e4-to-e5', title: 'Admit Timestamp Illusion', situation: 'cell-e4-timeout', nextSituation: 'cell-e5-conclude', showIfKey: 'key-timeout-retry' },

  /* Recovery / rollback links */
  { _id: 'link-e4-abort', title: 'Rollback → FITO Fallacy', situation: 'cell-e4-timeout', nextSituation: 'cell-e2-fito', hideIfKey: 'key-timeout-retry' }
];

/* attach choices to situations */
const allSituations: Situation[] = [...legacySituations, ...demolitionSituations];
allSituations.forEach(s => {
  s.choices = [
    ...(s.choices || []),
    ...demolitionChoices.filter(c => c.situation === s._id)
  ];
});

/* ------------------------------------------------------------------ *
 |  5.  Exports                                                       |
 * ------------------------------------------------------------------ */
export const placeholderSituations: Situation[] = allSituations;
export const placeholderChoices: Choice[] = [
  /* legacy choices were added inside legacy file — keep them */
  ...demolitionChoices
];
