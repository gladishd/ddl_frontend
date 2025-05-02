import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useMacMiniContext } from '@/context/MacMiniContext';
import { MessageData } from '@/types/PortSnapshot';
import dynamic from 'next/dynamic';

const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
  loading: () => <div>Loading graph...</div>
});

interface Edge {
  source: string;
  target: string;
}

interface PortPath {
  nodes: string[];
  edges: Edge[];
}

const DAGView: React.FC = () => {
  const { selectedMacMinis } = useMacMiniContext();
  const [message, setMessage] = useState<MessageData | null>(null);
  const connectionRef = useRef<WebSocket | null>(null);
  const messageHandler = useRef<((event: MessageEvent) => void) | null>(null);
  const prevMessageRef = useRef<MessageData | null>(null);

  const transformDataToGraph = useCallback((portPath: PortPath) => {
    console.log("Transforming port path:", portPath);
    const nodes = portPath.nodes.map(node => ({
      id: node,
      name: node,
    }));

    const links = portPath.edges.map(edge => ({
      source: edge.source,
      target: edge.target,
    }));

    const result = {
      nodes,
      links,
    };
    console.log("Transformed result:", result);
    return result;
  }, []);

  const handleNodeClick = useCallback((node: any) => {
    console.log('Node clicked:', node);
    // Center/zoom on node
    const distance = 40;
    const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
  }, []);

  // Memoize the graph data for each port
  const graphDataMap = useMemo(() => {
    if (!message?.port_paths) return {};
    
    console.log("Transforming graph data for all ports:", message.port_paths);
    
    return Object.entries(message.port_paths).reduce((acc, [portId, path]) => {
      const transformedData = transformDataToGraph(path);
      console.log(`Transformed data for port ${portId}:`, transformedData);
      acc[portId] = transformedData;
      return acc;
    }, {} as Record<string, { nodes: any[]; links: any[] }>);
  }, [message?.port_paths, transformDataToGraph]);

  useEffect(() => {
    // Only use first selected Mac Mini
    const macMini = selectedMacMinis[0];
    if (!macMini?.connection) return;

    // Clean up previous connection
    if (connectionRef.current && messageHandler.current) {
      connectionRef.current.removeEventListener('message', messageHandler.current);
    }

    // Set up new connection
    const handler = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        // Only update if the data has actually changed
        const prevPortPaths = prevMessageRef.current?.port_paths;
        const newPortPaths = data.port_paths;
        
        // Deep comparison of port paths
        const hasChanged = !prevPortPaths || !newPortPaths || 
          Object.keys(prevPortPaths).length !== Object.keys(newPortPaths).length ||
          Object.entries(prevPortPaths).some(([portId, prevPath]) => {
            const newPath = newPortPaths[portId];
            if (!newPath) return true;
            return prevPath.nodes.length !== newPath.nodes.length ||
                   prevPath.edges.length !== newPath.edges.length ||
                   !prevPath.nodes.every((node, i) => node === newPath.nodes[i]) ||
                   !prevPath.edges.every((edge, i) => 
                     edge.source === newPath.edges[i].source && 
                     edge.target === newPath.edges[i].target
                   );
          });

        if (hasChanged) {
          prevMessageRef.current = data;
          setMessage(data);
        }
      } catch (e) {
        console.error('Failed to parse message:', e);
      }
    };

    macMini.connection.addEventListener('message', handler);
    connectionRef.current = macMini.connection;
    messageHandler.current = handler;

    return () => {
      if (connectionRef.current && messageHandler.current) {
        connectionRef.current.removeEventListener('message', messageHandler.current);
      }
    };
  }, [selectedMacMinis]);

  if (!selectedMacMinis.length) {
    return (
      <div className="p-4">
        <p>Please select a Mac Mini to view DAG data</p>
      </div>
    );
  }

  return (
    <div className="p-4 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-lg font-bold mb-4">DAG View - {selectedMacMinis[0].ip}</h2>
      
      {message?.port_paths ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(message.port_paths).map(([portId, path]) => {
            const graphData = graphDataMap[portId];
            console.log("Rendering graph for port:", portId, "with data:", graphData);
            
            return (
              <div key={portId} className="border rounded p-4 flex flex-col">
                <h3 className="text-md font-semibold mb-4">Port: {portId}</h3>
                <div className="border rounded p-2 bg-white flex-1 min-h-[400px] relative">
                  <div className="absolute inset-0">
                    <ForceGraph2D
                      key={`${portId}-${graphData.nodes.length}-${graphData.links.length}`}
                      graphData={graphData}
                      nodeLabel="name"
                      nodeAutoColorBy="group"
                      linkDirectionalParticles={2}
                      linkDirectionalParticleWidth={2}
                      onNodeClick={handleNodeClick}
                      nodeColor={() => '#1a192b'}
                      nodeRelSize={6}
                      linkColor={() => '#999'}
                      linkWidth={1}
                      linkDirectionalArrowLength={3.5}
                      linkDirectionalArrowRelPos={1}
                      cooldownTicks={100}
                      onEngineStop={() => console.log(`Graph engine stopped for port ${portId}`)}
                      nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                        const label = node.name;
                        const fontSize = 12/globalScale;
                        ctx.font = `${fontSize}px Sans-Serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillStyle = 'black';
                        ctx.fillText(label, node.x, node.y);
                      }}
                    />
                  </div>
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
