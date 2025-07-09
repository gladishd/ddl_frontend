import React, { useContext } from 'react';
import styles from './styles/SituationsList.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import { Situation } from '@/types/canvas/Situation';

interface SituationsListProps {
  situations: Situation[];
}

// This component lists the Cells (Situations) contained within a Group (TRAPH).
// It's a Local Observer View of a subgraph within the GVM, allowing for direct
// interaction with the members of that confined set.
const SituationsList: React.FC<SituationsListProps> = ({ situations }) => {
  const { updateSituationAndNode, getSituation, setActiveEditTab } = useContext(CanvasContext);

  // This operation is a transactional state change, moving a Cell from one TRAPH to another (the null group).
  // The GVM ensures this change is atomic.
  const removeSituationFromGroup = async (situationId: string) => {
    try {
      await updateSituationAndNode(situationId, { situationGroup: null });
    } catch (error) {
      console.error("Error removing Cell from Group or updating canvas: ", error);
    }
  };

  const handleSituationClick = async (situationId: string) => {
    await getSituation(situationId);
    if (setActiveEditTab) setActiveEditTab("1");
  };

  return (
    <div className={styles.situationsContainer}>
      {(!situations || situations.length === 0) ? (
        <div className={styles.noSituationsText}>No Cells in this Group</div>
      ) : (
        situations.map((situation) => (
          <div
            key={situation._id}
            className={styles.situationItem}
            onClick={() => handleSituationClick(situation._id)}
          >
            <div className={styles.situationTitle}>
              {situation.title || 'Untitled Cell'}
            </div>
            <button
              className={styles.removeButton}
              onClick={(e) => {
                e.stopPropagation();
                removeSituationFromGroup(situation._id);
              }}
              aria-label="Remove situation from group"
            >
              <span className={styles.minusIcon}>−</span>
            </button>
          </div>
        ))
      )}
    </div>
  );
};

export default SituationsList;