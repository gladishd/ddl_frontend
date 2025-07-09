// The ErrorOverlay is a critical component for visualizing the health of the GVM.
// In a system where failures are not silent but are instead explicitly handled events,
// this overlay provides a clear, non-intrusive notification mechanism to the operator,
// indicating when a transaction has failed or a part of the fabric requires attention.
'use client';
import React, { useContext } from 'react';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import styles from './styles/ErrorOverlay.module.css';

interface ErrorOverlayProps {
  onSelectNode: (nodeId: string) => void;
  onSelectEdge: (edgeId: string) => void;
}

const ErrorOverlay: React.FC<ErrorOverlayProps> = ({ onSelectNode, onSelectEdge }) => {
  // In a full implementation, this would consume an error state from CanvasContext
  // const { errors } = useContext(CanvasContext);
  const errors: any[] = []; // Placeholder

  if (!errors || errors.length === 0) {
    return null;
  }

  return (
    <div className={styles.errorOverlay}>
      <div className={styles.errorHeader}>GVM State Errors Detected</div>
      <ul className={styles.errorList}>
        {errors.map((error, index) => (
          <li key={index} className={styles.errorItem}>
            <span className={styles.errorMessage}>{error.message}</span>
            {error.nodeId && (
              <button onClick={() => onSelectNode(error.nodeId)} className={styles.errorAction}>
                Go to Cell
              </button>
            )}
            {error.edgeId && (
              <button onClick={() => onSelectEdge(error.edgeId)} className={styles.errorAction}>
                Go to Link
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ErrorOverlay;