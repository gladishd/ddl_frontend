// The Toolbar provides the palette of primitive elements that can be instantiated
// onto the GVM's groundplane. Dragging an item from the toolbar initiates a
// transaction to create a new Cell in the N2N Lattice.
'use client';

import React from 'react';
import styles from './styles/Toolbar.module.css';

const Toolbar: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className={styles.toolbar}>
      <div className={styles.title}>Toolbox</div>
      <div className={styles.description}>
        Drag an Ethernet Node onto the canvas to begin.
      </div>
      <div
        className={styles.toolItem}
        onDragStart={(event) => onDragStart(event, 'situation')}
        draggable
      >
        Ethernet Node
      </div>
    </div>
  );
};

export default Toolbar;