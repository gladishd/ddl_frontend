// An Edge in this system is not a mere line but a visual representation of a 'Link'.
// Each Link is an autonomous, bipartite communication entity that mediates causality
// between two Cells and enforces atomic delivery guarantees. Its visual properties,
// such as being dashed, reflect its underlying logical state (e.g., a conditional transaction).

import React from 'react';
import { getBezierPath, EdgeProps } from 'reactflow';
import styles from './styles/Edge.module.css';

const Edge: React.FC<EdgeProps> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  markerEnd,
}) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const hasKeyCondition = data?.showIfKey || data?.hideIfKey;

  return (
    <>
      <path
        id={id}
        style={{ strokeDasharray: hasKeyCondition ? '5,5' : 'none' }}
        className={styles.edgePath}
        d={edgePath}
        markerEnd={markerEnd}
      />
      <text
        className={styles.edgeLabel}
        x={labelX}
        y={labelY}
        dy={-5}
        textAnchor="middle"
      >
        {/* FIX: Safely access the label property to prevent runtime errors */}
        {data?.label || ''}
      </text>
    </>
  );
};

export default Edge;