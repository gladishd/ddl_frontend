import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import styles from './styles/SituationNode.module.css';
import { Situation } from '@/types/canvas/Situation';

interface SituationNodeData {
    label: string;
    endpointType?: 'start' | 'end';
    fillColor?: string;
    borderColor?: string;
}

// A SituationNode is the visual representation of a 'Cell' in the Daedaelus architecture.
// Each Cell is a reactive, self-contained participant in the N2N Lattice. Its handles
// are its 'ports', the connection points for establishing stateful, reversible Links.
const SituationNode: React.FC<NodeProps<SituationNodeData>> = ({ data, isConnectable, selected }) => {

    const [isConnecting, setIsConnecting] = React.useState(false); // Placeholder for edge connection state

    let nodeClassName = styles.nodeContainer;
    if (selected) {
        nodeClassName += ` ${styles.selected}`;
    }
    if (isConnecting) {
        nodeClassName += ` ${styles.edgeConnecting}`;
    }

    switch (data.endpointType) {
        // A start node is the root of a causal tree, the origin point for a transactional flow.
        case 'start':
            nodeClassName += ` ${styles.startNode}`;
            break;
        // An end node is a terminal state where a transaction is committed or a causal chain resolves.
        case 'end':
            nodeClassName += ` ${styles.endNode}`;
            break;
        default:
            nodeClassName += ` ${styles.regularNode}`;
            break;
    }

    return (
        <div
            className={nodeClassName}
            style={{
                '--fill-color': data.fillColor || '#fff',
                '--border-color': data.borderColor || '#ddd',
            } as React.CSSProperties}
        >
            {data.endpointType === 'start' && <div className={styles.nodeLabel}>START</div>}
            {data.endpointType === 'end' && <div className={styles.nodeLabel}>END</div>}

            <div className={styles.nodeContent}>
                {/* A Cell's ports are bidirectional, allowing for both forward and reverse evolution of state. */}
                <Handle
                    type="target"
                    position={Position.Left}
                    className={styles.handleTarget}
                    isConnectable={isConnectable}
                />
                {data.label}
                <Handle
                    type="source"
                    position={Position.Right}
                    className={styles.handleSource}
                    isConnectable={isConnectable}
                />
            </div>
        </div>
    );
};

export default SituationNode;