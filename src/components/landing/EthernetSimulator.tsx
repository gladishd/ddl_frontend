"use client";

import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
} from "react";
import dynamic from "next/dynamic";

/* ------------------------------------------------------------------ */
/*  Types                                                             */
/* ------------------------------------------------------------------ */
interface StationNode {
  id: string;
  name: string;
  fx?: number;
  fy?: number;
  packetQueue: number;
  backoff: number;
  collisions: number;
  state: "idle" | "deferring" | "transmitting" | "collided" | "waiting";
}
interface EtherLink {
  source: string;
  target: string;
  state: "idle" | "transmission" | "collision";
}
interface GraphData {
  nodes: StationNode[];
  links: EtherLink[];
}

/* ------------------------------------------------------------------ */
/*  Dynamic import (SSR-safe)                                         */
/* ------------------------------------------------------------------ */
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => (
    <div className="graph-loading-placeholder">Loading Simulation Canvas…</div>
  ),
});

/* ------------------------------------------------------------------ */
/*  Constants                                                         */
/* ------------------------------------------------------------------ */
const SLOT_TIME = 51.2; // 512 bit-times on 10 Mb/s Ethernet

/* ------------------------------------------------------------------ */
/*  Component                                                         */
/* ------------------------------------------------------------------ */
type Props = {
  numStations: number;
  packetLength: number;
  isSimulating: boolean;
};

export default function EthernetSimulator({
  numStations,
  packetLength,
  isSimulating,
}: Props) {
  /* The ref now has an initial value `null` – fixes TS error */
  const fgRef = useRef<InstanceType<typeof ForceGraph2D> | null>(null);

  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [metrics, setMetrics] = useState({
    successfulPackets: 0,
    totalCollisions: 0,
    time: 0,
  });

  /* -------------------------------------------------------- */
  /*  Build initial topology whenever numStations changes     */
  /* -------------------------------------------------------- */
  useEffect(() => {
    const r = 150;
    const nodes: StationNode[] = [
      { id: "ether", name: "Ether", fx: 0, fy: 0, packetQueue: 0, backoff: 0, collisions: 0, state: "idle" },
    ];
    for (let i = 0; i < numStations; i++) {
      const θ = (i / numStations) * 2 * Math.PI;
      nodes.push({
        id: `st-${i}`,
        name: `Station ${i}`,
        fx: r * Math.cos(θ),
        fy: r * Math.sin(θ),
        packetQueue: 1,
        backoff: 0,
        collisions: 0,
        state: "idle",
      });
    }
    setGraphData({ nodes, links: [] });
    setMetrics({ successfulPackets: 0, totalCollisions: 0, time: 0 });
  }, [numStations]);

  /* -------------------------------------------------------- */
  /*  One simulation tick                                     */
  /* -------------------------------------------------------- */
  const simStep = useCallback(() => {
    setGraphData(prev => {
      const stations = prev.nodes.filter(n => n.id !== "ether");
      const txCandidates: StationNode[] = [];

      /* Phase 1 – decide who tries to send */
      stations.forEach(s => {
        if (s.backoff > 0) {
          s.backoff = Math.max(0, s.backoff - SLOT_TIME);
          s.state = "waiting";
        }
        if (s.packetQueue > 0 && s.backoff === 0) {
          if (prev.links.some(l => l.state !== "idle")) {
            s.state = "deferring";
          } else {
            txCandidates.push(s);
          }
        }
      });

      let links: EtherLink[] = [];

      /* Phase 2 – medium access / collision handling */
      if (txCandidates.length > 1) {
        links = txCandidates.map(s => ({
          source: s.id,
          target: "ether",
          state: "collision",
        }));
        txCandidates.forEach(s => {
          s.state = "collided";
          s.collisions += 1;
          const k = Math.pow(2, Math.min(s.collisions, 10)) - 1;
          s.backoff = Math.floor(Math.random() * (k + 1)) * SLOT_TIME;
        });
        setMetrics(m => ({
          ...m,
          totalCollisions: m.totalCollisions + txCandidates.length,
        }));
      } else if (txCandidates.length === 1) {
        const s = txCandidates[0];
        links = [{ source: s.id, target: "ether", state: "transmission" }];
        s.state = "transmitting";
        s.packetQueue = 0;
        s.collisions = 0;
        setMetrics(m => ({ ...m, successfulPackets: m.successfulPackets + 1 }));
      }

      /* Advance virtual time */
      setMetrics(m => ({ ...m, time: m.time + SLOT_TIME }));
      return { nodes: [prev.nodes[0], ...stations], links };
    });
  }, []);

  /* -------------------------------------------------------- */
  /*  Run / stop interval                                     */
  /* -------------------------------------------------------- */
  useEffect(() => {
    if (!isSimulating) return;
    const id = setInterval(simStep, 200);
    return () => clearInterval(id);
  }, [isSimulating, simStep]);

  /* -------------------------------------------------------- */
  /*  Node painter                                            */
  /* -------------------------------------------------------- */
  const nodeCanvasObject = useCallback(
    (node: any, ctx: CanvasRenderingContext2D) => {
      if (node.id === "ether") return;

      const r = 6;
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
      ctx.fillStyle = (
        {
          idle: "#6b7280",
          deferring: "#f59e0b",
          waiting: "#3b82f6",
          transmitting: "#22c55e",
          collided: "#ef4444",
        } as const
      )[node.state];
      ctx.fill();

      ctx.font = "5px Raleway";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = "#111827";
      ctx.fillText(node.name, node.x, node.y + r + 5);
    },
    []
  );

  const efficiency =
    metrics.time === 0
      ? 0
      : ((metrics.successfulPackets * packetLength) / metrics.time) * 100;

  /* -------------------------------------------------------- */
  /*  Render                                                  */
  /* -------------------------------------------------------- */
  return (
    <div className="relative w-full h-full">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeCanvasObject={nodeCanvasObject}
        linkWidth={1.5}
        linkColor={l => (l.state === "collision" ? "#ef4444" : "#22c55e")}
        linkLineDash={l => (l.state === "collision" ? [2, 1] : [])}
        linkDirectionalParticles={l => (l.state === "transmission" ? 2 : 0)}
        linkDirectionalParticleWidth={2}
        cooldownTicks={0}
      />

      {/* Metrics overlay */}
      <div className="simulation-metrics-overlay">
        <div>
          Efficiency:&nbsp;
          <span>{efficiency.toFixed(2)}%</span>
        </div>
        <div>
          Collisions:&nbsp;
          <span>{metrics.totalCollisions}</span>
        </div>
        <div>
          Time (slots):&nbsp;
          <span>{(metrics.time / SLOT_TIME).toFixed(0)}</span>
        </div>
      </div>
    </div>
  );
}
