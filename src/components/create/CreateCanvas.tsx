// This component, formerly CreateScenario, now serves as the primary layout for the GVM editor.
// It assembles the core operational views—the Toolbar for instantiating new Cells, the Canvas
// for visualizing the N2N Lattice, and the EditSidebar for manipulating the state of selected
// Cells and Links. It represents the top-level interface to the single, persistent groundplane.
'use client';

import React, { useState, useContext } from 'react';
import styles from './styles/CreateCanvas.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import useIsMobile from '@/hooks/useIsMobile';

import TopBar from './TopBar';
import Canvas from './Canvas';
import Toolbar from './Toolbar';
import EditSidebar from './EditSidebar';

const CreateCanvas: React.FC = () => {
  const { loading } = useContext(CanvasContext);
  const [renderEditSidebar, setRenderEditSidebar] = useState(true);
  const isMobile = useIsMobile();

  if (loading) {
    return <div className={styles.loadingContainer}>Initializing GVM...</div>;
  }

  return (
    <div className={styles.pageContainer}>
      <TopBar
        renderEditSidebar={renderEditSidebar}
        setRenderEditSidebar={setRenderEditSidebar}
        isMobile={isMobile}
      />
      <div className={styles.mainContent}>
        <Toolbar />
        <div className={styles.canvasWrapper}>
          <Canvas
            setRenderEditSidebar={setRenderEditSidebar}
            isMobile={isMobile}
          />
        </div>
        {renderEditSidebar && (
          <div className={styles.sidebarWrapper}>
            <EditSidebar setRenderEditSidebar={setRenderEditSidebar} />
          </div>
        )}
      </div>
    </div>
  );
};

export default CreateCanvas;