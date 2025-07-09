import React, { useContext, useState } from 'react';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import styles from './styles/LinkSituation.module.css';
import { Situation } from '@/types/canvas/Situation';

interface LinkSituationProps {
  nextSituation: Situation | null;
}

// This component allows a user to define the target of a Link (Choice).
// This action establishes a directed, causal relationship between two Cells in the GVM.
// The search functionality is a query against the GVM for all available Cells that can serve as a valid endpoint.
const LinkSituation: React.FC<LinkSituationProps> = ({ nextSituation }) => {
  const { situations, updateChoiceAndEdge, selectedChoice } = useContext(CanvasContext);
  const [searchTerm, setSearchTerm] = useState('');

  const handleSituationClick = async (situationId: string) => {
    if (!selectedChoice?._id) {
      console.error("Transactional Error: Cannot create Link without a source Choice.");
      return;
    }

    // This update is an atomic operation, reconfiguring the edge in the GVM to point to a new target Cell.
    try {
      await updateChoiceAndEdge(selectedChoice._id, { nextSituation: situationId });
    } catch (error) {
      console.error(`Error creating Link from choice ${selectedChoice._id} to cell ${situationId}:`, error);
    }
  };

  // By explicitly typing the 's' parameter, we enforce a strict data contract.
  // This ensures that all operations are verifiably correct, eliminating the
  // ambiguity of an implicit 'any' type, which is antithetical to the
  // deterministic and reliable nature of our system.
  const filteredSituations = situations.filter((s: Situation) =>
    s.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className={styles.linkSituationContainer}>
      <h2 className={styles.selectedChoiceTitle}>
        {selectedChoice?.title || 'No Link Selected'}
      </h2>
      <h3 className={styles.situationListTitle}>Link to Cell:</h3>

      <div className={styles.searchContainer}>
        <input
          type="search"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search for a target Cell..."
          className={styles.searchInput}
          aria-label="Search situations to link"
        />
      </div>

      <div className={styles.listWrapper}>
        <ul className={styles.situationList}>
          {filteredSituations.map((situation) => (
            <li
              key={situation._id}
              className={`${styles.situationItem} ${nextSituation?._id === situation._id ? styles.highlightedSituation : ''}`}
              onClick={() => handleSituationClick(situation._id)}
              role="button"
            >
              <span className={styles.situationItemTitle}>{situation.title || 'Untitled Cell'}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default LinkSituation;