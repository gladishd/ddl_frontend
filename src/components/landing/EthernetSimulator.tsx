"use client";
import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
} from "react";
import dynamic from "next/dynamic";

/* ─────────── Types ─────────── */
// This interface defines the state of each station contending for the Ether.
// It includes properties for the force-directed graph layout (x, y, fx, fy)
// and the state-machine logic of the CSMA/CD protocol.
interface StationNode {
  id: string;
  name: string;
  fx?: number;
  fy?: number;
  x?: number;
  y?: number;
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
// In our model, a slot is the fundamental unit of time, representing the end-to-end propagation delay.
// This is the maximum time between starting a transmission and detecting a collision, as described
// in Metcalfe's original analysis of the broadcast queue.
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
    // The topology here is a classic star, but this is a logical representation.
    // Physically, all stations tap into the same, unrooted, branching Ether.
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
        packetQueue: 1, // Start each station with a packet to send.
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
      const transmittingStations: StationNode[] = [];

      // Phase 1: Stations contend for the Ether.
      // This implements the core logic of CSMA/CD: defer if carrier is sensed,
      // and attempt to transmit if idle and ready.
      stations.forEach(s => {
        if (s.backoff > 0) {
          s.backoff = Math.max(0, s.backoff - SLOT_TIME);
          s.state = "waiting";
        }
        if (s.packetQueue > 0 && s.backoff === 0) {
          // Deference: A station must wait if another transmission is in progress.
          if (prev.links.some(l => l.state === "transmission")) {
            s.state = "deferring";
          } else {
            transmittingStations.push(s);
          }
        }
      });

      let currentLinks: EtherLink[] = [];

      // Phase 2: Arbitrate access to the Ether and handle collisions.
      if (transmittingStations.length > 1) {
        // A collision occurs if more than one station transmits in the same slot.
        currentLinks = transmittingStations.map(s => ({
          source: s.id,
          target: "ether",
          state: "collision",
        }));
        transmittingStations.forEach(s => {
          s.state = "collided";
          s.collisions += 1;
          // Binary Exponential Backoff: The controller adjusts the mean retransmission interval
          // based on collision history to dynamically manage load.
          const k = 2 ** Math.min(s.collisions, 10) - 1;
          s.backoff = Math.floor(Math.random() * (k + 1)) * SLOT_TIME;
        });
        setMetrics(m => ({
          ...m,
          totalCollisions: m.totalCollisions + transmittingStations.length,
        }));
      } else if (transmittingStations.length === 1) {
        // Acquisition: A single station successfully acquires the Ether.
        const station = transmittingStations[0];
        currentLinks = [{ source: station.id, target: "ether", state: "transmission" }];
        station.state = "transmitting";
        station.packetQueue = 0; // The packet is sent.
        station.collisions = 0;  // Reset collision count on success.
        setMetrics(m => ({
          ...m,
          successfulPackets: m.successfulPackets + 1,
        }));
      }

      setMetrics(m => ({ ...m, time: m.time + SLOT_TIME }));
      return { nodes: [prev.nodes[0], ...stations], links: currentLinks };
    });
  }, []);

  /* ── Start / stop loop ── */
  useEffect(() => {
    if (!isSimulating) return;
    const intervalId = setInterval(simStep, 200);
    return () => clearInterval(intervalId);
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
    (node: StationNode, ctx: CanvasRenderingContext2D) => {
      // The Ether itself is a logically passive medium, not a station, so we don't draw it as one.
      if (node.id === "ether") return;

      const radius = 6;
      ctx.beginPath();
      ctx.arc(node.x!, node.y!, radius, 0, 2 * Math.PI);

      // This palette provides a Local Observer View of each station's state.
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
      ctx.fillText(node.name, node.x!, node.y! + radius + 5);
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
        nodeCanvasObject={nodeCanvasObject as any}
        linkWidth={1.5}
        linkColor={(l: any) =>
          (l as EtherLink).state === "collision" ? "#ef4444" : "#22c55e"
        }
        linkLineDash={(l: any) => ((l as EtherLink).state === "collision" ? [2, 1] : [])}
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