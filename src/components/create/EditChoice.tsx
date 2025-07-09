// This component provides the editing interface for a selected 'Link' (Choice).
// In the Daedaelus model, a Link is not a static connector but an active, stateful
// agent that mediates causality. This interface allows for the direct manipulation
// of a Link's properties, its target Cell, and its gating Keys, which are all
// fundamental operations within the Graph Virtual Machine (GVM).
'use client';

import React, { useContext, useState, useEffect } from 'react';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import styles from './styles/EditChoice.module.css';
import EditSidebarTabs from './EditSidebarTabs';
import LinkSituation from './LinkSituation';
import DeleteModal from './DeleteModal';
import { Situation } from '@/types/canvas/Situation';

interface EditChoiceProps {
  setRenderEditSidebar: (render: boolean) => void;
}

const EditChoice: React.FC<EditChoiceProps> = ({ setRenderEditSidebar }) => {
  const {
    selectedChoice,
    updateChoiceAndEdge,
    deleteChoiceAndEdge,
    activeEditTab,
    getSituation,
    loading
  } = useContext(CanvasContext);

  const [title, setTitle] = useState(selectedChoice?.title || '');
  const [nextSituation, setNextSituation] = useState<Situation | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    setTitle(selectedChoice?.title || '');
    if (selectedChoice?.nextSituation) {
      // Fetch the full situation object for the linked target
      const fetchNextSituation = async () => {
        const situation = await getSituation(selectedChoice.nextSituation);
        setNextSituation(situation || null);
      };
      fetchNextSituation();
    } else {
      setNextSituation(null);
    }
  }, [selectedChoice, getSituation]);

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value);
  };

  const handleTitleBlur = async () => {
    if (selectedChoice && title !== selectedChoice.title) {
      await updateChoiceAndEdge(selectedChoice._id, { title });
    }
  };

  // Deleting a Link is an irreversible operation that severs a potential causal path
  // within the GVM. The transaction must be confirmed.
  const handleDelete = async () => {
    if (selectedChoice) {
      await deleteChoiceAndEdge(selectedChoice._id);
      setRenderEditSidebar(false);
      setShowDeleteModal(false);
    }
  };

  const renderTabContent = () => {
    switch (activeEditTab) {
      case '2': // Target Tab
        return <LinkSituation nextSituation={nextSituation} />;
      case '3': // Settings Tab
        return (
          <div className={styles.settingsContainer}>
            <button
              onClick={() => setShowDeleteModal(true)}
              className={styles.deleteButton}
              disabled={loading}
            >
              Destroy Link
            </button>
          </div>
        );
      case '1': // Content Tab
      default:
        return (
          <div className={styles.form}>
            <label htmlFor="choiceTitle" className={styles.label}>Link Title</label>
            <input
              id="choiceTitle"
              type="text"
              value={title}
              onChange={handleTitleChange}
              onBlur={handleTitleBlur}
              className={styles.input}
              placeholder="Enter Link Title"
              disabled={loading}
            />
          </div>
        );
    }
  };

  return (
    <div className={styles.editChoiceContainer}>
      <EditSidebarTabs editType="choice" />
      <div className={styles.scrollableContent}>
        {renderTabContent()}
      </div>
      {showDeleteModal && (
        <DeleteModal
          type="Link"
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteModal(false)}
        />
      )}
    </div>
  );
};

export default EditChoice;