import React, { useContext } from 'react';
import styles from './styles/SituationsList.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import { Situation } from '@/types/canvas/Situation';

interface SituationsListProps {
  situations: Situation[];
}

// Lists the Cells (Situations) contained within a Group (TRAPH).
// Removing a Cell is an atomic transaction: `situationGroup` becomes `undefined` (never `null`).
const SituationsList: React.FC<SituationsListProps> = ({ situations }) => {
  const {
    updateSituationAndNode,
    getSituation,
    setActiveEditTab,
  } = useContext(CanvasContext);

  const removeSituationFromGroup = async (situationId: string) => {
    try {
      await updateSituationAndNode(situationId, { situationGroup: undefined });
    } catch (error) {
      console.error('Error removing Cell from Group or updating canvas: ', error);
    }
  };

  const handleSituationClick = async (situationId: string) => {
    await getSituation(situationId);
    if (setActiveEditTab) setActiveEditTab('1');
  };

  return (
    <div className={styles.situationsContainer}>
      {situations.length === 0 ? (
        <div className={styles.noSituationsText}>No Cells in this Group</div>
      ) : (
          situations.map((situation: Situation) => (
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
                aria-label="Remove situation from group"
              onClick={(e) => {
                e.stopPropagation();
                removeSituationFromGroup(situation._id);
              }}
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