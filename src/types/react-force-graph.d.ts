declare module 'react-force-graph-2d' {
  import { FC } from 'react';

  interface GraphData {
    nodes: Array<{
      id: string;
      name?: string;
      group?: number;
      x?: number;
      y?: number;
      z?: number;
    }>;
    links: Array<{
      source: string;
      target: string;
    }>;
  }

  interface ForceGraph2DProps {
    graphData: GraphData;
    nodeLabel?: string | ((node: any) => string);
    nodeAutoColorBy?: string;
    linkDirectionalParticles?: number;
    linkDirectionalParticleWidth?: number;
    onNodeClick?: (node: any) => void;
    nodeCanvasObject?: (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => void;
    nodeColor?: string | ((node: any) => string);
    nodeRelSize?: number;
    linkColor?: string | ((link: any) => string);
    linkWidth?: number;
    linkDirectionalArrowLength?: number;
    linkDirectionalArrowRelPos?: number;
    cooldownTicks?: number;
    onEngineStop?: () => void;
  }

  const ForceGraph2D: FC<ForceGraph2DProps>;
  export default ForceGraph2D;
} 