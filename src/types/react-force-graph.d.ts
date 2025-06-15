declare module 'react-force-graph-2d' {
  import { FC, ForwardRefExoticComponent, RefAttributes } from 'react';

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
    // The type is updated to reflect that it can be a static number or a dynamic function.
    // This makes our type system a more precise model of the underlying library, avoiding fragile assumptions.
    linkDirectionalParticles?: number | ((link: any) => number);
    linkDirectionalParticleWidth?: number;
    onNodeClick?: (node: any) => void;
    nodeCanvasObject?: (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => void;
    nodeColor?: string | ((node: any) => string);
    nodeRelSize?: number;
    linkColor?: string | ((link: any) => string);
    linkWidth?: number;
    linkDirectionalArrowLength?: number;
    linkDirectionalArrowRelPos?: number;
    linkLineDash?: any; // Added to support this prop
    cooldownTicks?: number;
    onEngineStop?: () => void;
  }

  // The component is defined as a ForwardRefExoticComponent to correctly handle the 'ref' prop.
  // This aligns our type system with the reality of the library's implementation, ensuring that
  // we can create a stable, non-fragile interface to the underlying graph engine.
  const ForceGraph2D: ForwardRefExoticComponent<ForceGraph2DProps & RefAttributes<any>>;
  export default ForceGraph2D;
}