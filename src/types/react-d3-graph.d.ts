declare module 'react-d3-graph' {
  interface GraphConfig {
    nodeHighlightBehavior?: boolean;
    node?: {
      color?: string;
      size?: number;
      highlightStrokeColor?: string;
      labelProperty?: string;
    };
    link?: {
      highlightColor?: string;
    };
    directed?: boolean;
    height?: number;
    width?: number;
  }

  interface GraphData {
    nodes: Array<{
      id: string;
      name?: string;
    }>;
    links: Array<{
      source: string;
      target: string;
    }>;
  }

  interface GraphProps {
    id: string;
    data: GraphData;
    config: GraphConfig;
  }

  export const Graph: React.FC<GraphProps>;
} 