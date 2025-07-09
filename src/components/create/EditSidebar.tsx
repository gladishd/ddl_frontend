import React, { useContext } from 'react';
import styles from './styles/EditSidebar.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext'; // Adjusted import path
import EditSituation from './EditSituation';
import EditChoice from './EditChoice';
import EditGroup from './EditGroup';

interface EditSidebarProps {
  setRenderEditSidebar: (render: boolean) => void;
}

// The EditSidebar is the control plane for a selected element of the GVM.
// It provides a Local Observer View (LOV) into the properties of a Cell or Link,
// allowing for its state to be manipulated directly. This is a powerful tool for
// debugging and direct architectural construction.
const EditSidebar: React.FC<EditSidebarProps> = ({ setRenderEditSidebar }) => {
  const { selectedSituation, selectedEdgeId, selectedGroup } = useContext(CanvasContext);

  return (
    <div className={styles.container} style={{ backgroundColor: "rgb(44, 44, 44)" }}>
      {/* Editing a 'Cell' (Situation) */}
      {selectedSituation && <EditSituation setRenderEditSidebar={setRenderEditSidebar} />}

      {/* Editing a 'Link' (Choice/Edge) */}
      {selectedEdgeId && <EditChoice setRenderEditSidebar={setRenderEditSidebar} />}

      {/* Editing a 'TRAPH' or 'Hypercell' (Group) */}
      {selectedGroup && <EditGroup setRenderEditSidebar={setRenderEditSidebar} />}

      {/* When no element is selected, the GVM is in a state of equilibrium from the editor's perspective. */}
      {!selectedSituation && !selectedEdgeId && !selectedGroup && (
        <div className={styles.noSelection}>
          No Element Selected
        </div>
      )}
    </div>
  );
};

export default EditSidebar;