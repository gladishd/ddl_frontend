"use client";

import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
} from "react";
import dynamic from "next/dynamic";

/* ─────────── Types ─────────── */
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

/* ─────────── Lazy-load canvas ─────────── */
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => (
    <div className="graph-loading-placeholder">
      Loading Simulation Canvas…
    </div>
  ),
});

/* ─────────── Constants ─────────── */
const SLOT_TIME = 51.2;           // 512 bit-times @ 10 Mb s⁻¹

/* ─────────── Component ─────────── */
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
  const fgRef = useRef<any>(null);

  const [graphData, setGraphData] = useState<GraphData>({
    nodes: [],
    links: [],
  });
  const [metrics, setMetrics] = useState({
    successfulPackets: 0,
    totalCollisions: 0,
    time: 0,
  });

  /* ── Build topology whenever `numStations` changes ── */
  useEffect(() => {
    const radius = 150;
    const nodes: StationNode[] = [
      {
        id: "ether",
        name: "Ether",
        fx: 0,
        fy: 0,
        packetQueue: 0,
        backoff: 0,
        collisions: 0,
        state: "idle",
      },
    ];

    for (let i = 0; i < numStations; i++) {
      const θ = (i / numStations) * 2 * Math.PI;
      nodes.push({
        id: `st-${i}`,
        name: `Station ${i}`,
        fx: radius * Math.cos(θ),
        fy: radius * Math.sin(θ),
        packetQueue: 1,
        backoff: 0,
        collisions: 0,
        state: "idle",
      });
    }

    setGraphData({ nodes, links: [] });
    setMetrics({ successfulPackets: 0, totalCollisions: 0, time: 0 });
  }, [numStations]);

  /* ── One simulation tick ── */
  const simStep = useCallback(() => {
    setGraphData(prev => {
      const stations = prev.nodes.filter(n => n.id !== "ether");
      const tx: StationNode[] = [];

      /* phase 1 – contend */
      stations.forEach(s => {
        if (s.backoff > 0) {
          s.backoff = Math.max(0, s.backoff - SLOT_TIME);
          s.state = "waiting";
        }
        if (s.packetQueue > 0 && s.backoff === 0) {
          if (prev.links.some(l => l.state !== "idle")) {
            s.state = "deferring";
          } else {
            tx.push(s);
          }
        }
      });

      let links: EtherLink[] = [];

      /* phase 2 – handle medium / collisions */
      if (tx.length > 1) {
        links = tx.map(s => ({
          source: s.id,
          target: "ether",
          state: "collision",
        }));
        tx.forEach(s => {
          s.state = "collided";
          s.collisions += 1;
          const k = 2 ** Math.min(s.collisions, 10) - 1;
          s.backoff = Math.floor(Math.random() * (k + 1)) * SLOT_TIME;
        });
        setMetrics(m => ({
          ...m,
          totalCollisions: m.totalCollisions + tx.length,
        }));
      } else if (tx.length === 1) {
        const s = tx[0];
        links = [{ source: s.id, target: "ether", state: "transmission" }];
        s.state = "transmitting";
        s.packetQueue = 0;
        s.collisions = 0;
        setMetrics(m => ({
          ...m,
          successfulPackets: m.successfulPackets + 1,
        }));
      }

      setMetrics(m => ({ ...m, time: m.time + SLOT_TIME }));
      return { nodes: [prev.nodes[0], ...stations], links };
    });
  }, []);

  /* ── Start / stop loop ── */
  useEffect(() => {
    if (!isSimulating) return;
    const id = setInterval(simStep, 200);
    return () => clearInterval(id);
  }, [isSimulating, simStep]);

  /* ── Re-apply link particle accessors whenever links change ── */
  useEffect(() => {
    if (!fgRef.current) return;
    fgRef.current
      .linkDirectionalParticles((l: EtherLink) =>
        l.state === "transmission" ? 2 : 0
      )
      .linkDirectionalParticleWidth(2);
  }, [graphData.links]);

  /* ── Node painter ── */
  const nodeCanvasObject = useCallback(
    (node: any, ctx: CanvasRenderingContext2D) => {
      if (node.id === "ether") return;
      const r = 6;
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);

      const palette: Record<StationNode["state"], string> = {
        idle: "#6b7280",
        deferring: "#f59e0b",
        waiting: "#3b82f6",
        transmitting: "#22c55e",
        collided: "#ef4444",
      };
      ctx.fillStyle = palette[node.state];
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

  /* ── Render ── */
  return (
    <div className="relative w-full h-full">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeCanvasObject={nodeCanvasObject}
        linkWidth={1.5}
        linkColor={(l: EtherLink) =>
          l.state === "collision" ? "#ef4444" : "#22c55e"
        }
        linkLineDash={(l: EtherLink) => (l.state === "collision" ? [2, 1] : [])}
        cooldownTicks={0}
      />

      {/* overlay */}
      <div className="simulation-metrics-overlay">
        <div>Efficiency:&nbsp;<span>{efficiency.toFixed(2)}%</span></div>
        <div>Collisions:&nbsp;<span>{metrics.totalCollisions}</span></div>
        <div>Time&nbsp;(slots):&nbsp;<span>{(metrics.time / SLOT_TIME).toFixed(0)}</span></div>
      </div>
    </div>
  );
}
