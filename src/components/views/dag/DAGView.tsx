"use client";

import React, {
  useMemo,
  useCallback,
  useRef,
  useState,
  useEffect,
  MouseEvent,
} from "react";
import dynamic from "next/dynamic";
import { useMacMiniContext } from "@/context/MacMiniContext";
import { MessageData, PortPath, Edge } from "@/types/PortSnapshot";
import { ZoomIn, ZoomOut, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

/* ------------------------------------------------------------------ */
/*  Lazy-load canvas graph (SSR-safe)                                 */
/* ------------------------------------------------------------------ */
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => <div className="p-4 text-gray-500">Loading graph…</div>,
});

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */
interface GraphData {
  nodes: Array<{ id: string; name: string; color: string }>;
  links: Array<{ source: string; target: string }>;
}
const COLORS = [
  "#4f46e5",
  "#14b8a6",
  "#f97316",
  "#a855f7",
  "#22c55e",
  "#ec4899",
];
const randomColor = () => COLORS[Math.floor(Math.random() * COLORS.length)];

/* ------------------------------------------------------------------ */
/*  Main component                                                    */
/* ------------------------------------------------------------------ */
const DAGView: React.FC = () => {
  const { selectedMacMinis, messages } = useMacMiniContext();
  const macMini = selectedMacMinis[0];
  const message: MessageData | undefined = macMini
    ? messages[macMini.ip]
    : undefined;

  /* -------- Build per-port graph data ----------------------------- */
  const toGraph = useCallback((p: PortPath): GraphData => {
    const nodes = p.nodes.map((id) => ({
      id,
      name: id.split(":").pop() ?? id,
      color: randomColor(),
    }));
    const links = p.edges.map((e: Edge) => ({ source: e.source, target: e.target }));
    return { nodes, links };
  }, []);

  const graphMap = useMemo(() => {
    if (!message?.port_paths) return {};
    return Object.fromEntries(
      Object.entries(message.port_paths).map(([pid, path]) => [pid, toGraph(path)])
    );
  }, [message?.port_paths, toGraph]);

  if (!macMini) {
    return <div className="p-4 text-gray-500">Select a Mac Mini to view DAGs.</div>;
  }

  /* ----------------------------------------------------------------
   *  Renderer for a single port                                     */
  /* ---------------------------------------------------------------- */
  const PortGraph: React.FC<{ portId: string; data: GraphData }> = ({ portId, data }) => {
    const fgRef = useRef<any>(null);
    const [hoverNode, setHoverNode] = useState<any>(null);
    const [tip, setTip] = useState<{ x: number; y: number; txt: string } | null>(null);

    /* Initial centring whenever data swaps out */
    useEffect(() => {
      if (fgRef.current) fgRef.current.zoomToFit(400, 40);
    }, [data]);

    /* Painter */
    const drawNode = useCallback(
      (n: any, ctx: CanvasRenderingContext2D, scale: number) => {
        const base = 8;
        const r = hoverNode && hoverNode.id === n.id ? base * 1.4 : base;

        ctx.save();
        ctx.shadowColor = `${n.color}55`;
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(n.x, n.y, r, 0, 2 * Math.PI);
        ctx.fillStyle = n.color;
        ctx.fill();
        ctx.restore();

        ctx.beginPath();
        ctx.arc(n.x, n.y, r * 0.5, 0, 2 * Math.PI);
        ctx.fillStyle = "#fff";
        ctx.fill();

        ctx.font = `${12 / scale}px "Raleway", sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillStyle = "#374151";
        ctx.fillText(n.name, n.x, n.y + r + 2);
      },
      [hoverNode]
    );

    /* Expanded pointer-area hitbox */
    const pointerArea = useCallback(
      (n: any, _col: string, ctx: CanvasRenderingContext2D) => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, 12, 0, 2 * Math.PI);
        ctx.fill();
      },
      []
    );

    /* HTML tooltip */
    const handleMove = (e: MouseEvent<HTMLDivElement>) => {
      if (!hoverNode) return;
      const rect = (e.target as HTMLCanvasElement).getBoundingClientRect();
      setTip({ x: e.clientX - rect.left + 10, y: e.clientY - rect.top + 10, txt: hoverNode.id });
    };

    return (
      <div className="relative border rounded-lg shadow-sm">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-2 border-b bg-gray-50">
          <h3 className="font-semibold text-sm text-gray-700">Port&nbsp;{portId}</h3>
          <div className="flex gap-1">
            <Button size="icon" variant="ghost" onClick={() => fgRef.current?.zoom(1.2, 300)}>
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button size="icon" variant="ghost" onClick={() => fgRef.current?.zoom(0.8, 300)}>
              <ZoomOut className="w-4 h-4" />
            </Button>
            <Button size="icon" variant="ghost" onClick={() => fgRef.current?.zoomToFit(300, 40)}>
              <RefreshCcw className="w-4 h-4" />
            </Button>
          </div>
        </header>

        {/* Canvas */}
        <div className="relative" style={{ height: 420 }} onMouseMove={handleMove}>
          <ForceGraph2D
            ref={fgRef}
            graphData={data}
            nodeCanvasObject={drawNode}
            nodePointerAreaPaint={pointerArea}
            nodeLabel="id"
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            linkDirectionalParticles={4}
            linkDirectionalParticleWidth={2}
            linkDirectionalParticleSpeed={0.004}
            backgroundColor="#ffffff"
            d3VelocityDecay={0.35}
            cooldownTicks={120}
            /* Re-centre when the physics engine finishes */
            onEngineStop={() => fgRef.current?.zoomToFit(300, 40)}
            onNodeHover={(n) => {
              setHoverNode(n);
              if (!n) setTip(null);
            }}
            onNodeClick={() => fgRef.current?.zoomToFit(300, 40)}
          />

          {tip && (
            <div
              className="absolute pointer-events-none px-2 py-1 text-xs rounded bg-gray-800 text-white shadow"
              style={{ left: tip.x, top: tip.y }}
            >
              {tip.txt}
            </div>
          )}
        </div>
      </div>
    );
  };

  /* ------------------------------------------------------------------ */
  /*  Layout                                                            */
  /* ------------------------------------------------------------------ */
  return (
    <div className="p-4 overflow-y-auto max-h-[calc(100vh-8rem)] space-y-4">
      <h2 className="text-lg font-bold mb-2">
        Directed Acyclic Graphs — <span className="text-primary">{macMini.ip}</span>
      </h2>

      {message?.port_paths ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(graphMap).map(([pid, data]) => (
            <PortGraph key={pid} portId={pid} data={data} />
          ))}
        </div>
      ) : (
          <p className="text-gray-500">No DAG data available.</p>
      )}
    </div>
  );
};

export default DAGView;
