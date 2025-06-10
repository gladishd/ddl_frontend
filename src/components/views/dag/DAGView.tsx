import React, { useMemo, useCallback } from "react";
import { useMacMiniContext } from "@/context/MacMiniContext";
import dynamic from "next/dynamic";
import { MessageData, PortPath, Edge } from "@/types/PortSnapshot";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => <div>Loading graph…</div>,
});

const DAGView: React.FC = () => {
  const { selectedMacMinis, messages } = useMacMiniContext();
  const macMini = selectedMacMinis[0];

  // Grab message straight from context (demo‑friendly — no WebSocket).
  const message: MessageData | undefined = macMini ? messages[macMini.ip] : undefined;

  const transformDataToGraph = useCallback((portPath: PortPath) => {
    const nodes = portPath.nodes.map((id) => ({ id, name: id }));
    const links = portPath.edges.map((e: Edge) => ({ source: e.source, target: e.target }));
    return { nodes, links };
  }, []);

  const graphDataMap = useMemo(() => {
    if (!message?.port_paths) return {};
    return Object.fromEntries(
      Object.entries(message.port_paths).map(([portId, path]) => [
        portId,
        transformDataToGraph(path),
      ])
    );
  }, [message?.port_paths, transformDataToGraph]);

  if (!macMini) {
    return (
      <div className="p-4 text-gray-500">Please select a Mac Mini to view DAG data.</div>
    );
  }

  return (
    <div className="p-4 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-lg font-bold mb-4">DAG View — {macMini.ip}</h2>

      {message?.port_paths ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(message.port_paths).map(([portId]) => {
            const graphData = graphDataMap[portId]!;
            return (
              <div key={portId} className="border rounded p-4 flex flex-col">
                <h3 className="text-md font-semibold mb-4">Port: {portId}</h3>
                <div className="border rounded p-2 bg-white flex-1 min-h-[400px] relative">
                  <ForceGraph2D
                    graphData={graphData}
                    nodeLabel="name"
                    nodeAutoColorBy="group"
                    linkDirectionalParticles={2}
                    linkDirectionalParticleWidth={2}
                    nodeColor={() => "#1a192b"}
                    nodeRelSize={6}
                    linkColor={() => "#999"}
                    linkWidth={1}
                    linkDirectionalArrowLength={3.5}
                    linkDirectionalArrowRelPos={1}
                    cooldownTicks={60}
                    nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, g: number) => {
                      const label = node.name;
                      const size = 12 / g;
                      ctx.font = `${size}px sans-serif`;
                      ctx.textAlign = "center";
                      ctx.textBaseline = "middle";
                      ctx.fillStyle = "black";
                      ctx.fillText(label, node.x, node.y);
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <p>No DAG data available</p>
      )}
    </div>
  );
};

export default DAGView;
