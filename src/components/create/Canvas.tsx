// The Canvas is the primary rendering surface for the Graph Virtual Machine.
// It provides a visual representation of the N2N Lattice, where each node is a Cell
// and each edge is a stateful, directional Link. User interactions on the canvas
// trigger atomic, reversible transactions that manipulate the underlying graph structure.
'use client';

import React, { useCallback, useMemo, useRef, useContext } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useReactFlow,
  EdgeLabelRenderer,
  NodeProps, // Ensure NodeProps is imported if not already
} from 'reactflow';
import 'reactflow/dist/style.css';
import SituationNode from './SituationNode';
import Edge from './Edge';
import ErrorOverlay from './ErrorOverlay';
import styles from './styles/Canvas.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';

interface CanvasProps {
  setRenderEditSidebar: (render: boolean) => void;
  isMobile: boolean;
}

const Canvas: React.FC<CanvasProps> = ({ setRenderEditSidebar, isMobile }) => {
  const {
    nodes,
    onNodesChange,
    edges,
    onEdgesChange,
    onConnect,
    onNodeClick,
    onEdgeClick,
    onCanvasClick,
    createSituationAndNode,
  } = useContext(CanvasContext);

  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { project } = useReactFlow();

  // Dropping an element onto the canvas is not a simple UI event; it is a request
  // to instantiate a new Cell within the GVM's groundplane.
  const onDrop = useCallback(async (event: React.DragEvent) => {
    event.preventDefault();

    const type = event.dataTransfer.getData('application/reactflow');
    if (!type || !reactFlowWrapper.current) return;

    const position = project({
      x: event.clientX - reactFlowWrapper.current.getBoundingClientRect().left,
      y: event.clientY - reactFlowWrapper.current.getBoundingClientRect().top,
    });

    // The 'createSituationAndNode' function embodies the principle of making the infrastructure programmable,
    // where UI actions translate directly into state changes in the underlying graph fabric.
    await createSituationAndNode(position);
  }, [project, createSituationAndNode]);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // By passing the SituationNode component directly, we let React Flow manage the 'selected'
  // prop. This is a more direct and efficient implementation that avoids redundant state
  // management and relies on the framework's own deterministic state updates.
  const nodeTypes = useMemo(() => ({
    situation: SituationNode,
  }), []);

  const edgeTypes = useMemo(() => ({
    choice: Edge,
  }), []);

  return (
    <div className={styles.container} ref={reactFlowWrapper} onDrop={onDrop} onDragOver={onDragOver}>
      <ReactFlow
        nodes={nodes}
        onNodesChange={onNodesChange}
        edges={edges}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick as any}
        onEdgeClick={onEdgeClick as any}
        onPaneClick={onCanvasClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
      >
        <Controls />
        <Background color="#aaa" gap={16} />
        <EdgeLabelRenderer />
        <ErrorOverlay onSelectNode={() => { }} onSelectEdge={() => { }} />
      </ReactFlow>
    </div>
  );
};

export default Canvas;