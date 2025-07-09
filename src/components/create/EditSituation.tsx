// This component is the editor for a single 'Cell' (Situation). It manages the Cell's
// internal state (title, semantic text) and its set of outgoing 'Links' (Choices).
// Each modification here is a transaction that updates the state of a discrete,
// reactive participant within the GVM.
'use client';

import React, { useContext, useState, useEffect } from 'react';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import styles from './styles/EditSituation.module.css';
import EditSidebarTabs from './EditSidebarTabs';
import DeleteModal from './DeleteModal';
import UploadModal from './UploadModal';
import ChoicesList from './ChoicesList'; // Import ChoicesList

interface EditSituationProps {
  setRenderEditSidebar: (render: boolean) => void;
}

const EditSituation: React.FC<EditSituationProps> = ({ setRenderEditSidebar }) => {
  const {
    selectedSituation,
    updateSituationAndNode,
    deleteSituationAndNode,
    activeEditTab,
    loading,
    resetState,
  } = useContext(CanvasContext);

  const [title, setTitle] = useState(selectedSituation?.title || '');
  const [text, setText] = useState(selectedSituation?.text || '');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState<'image' | 'audio' | null>(null);

  useEffect(() => {
    setTitle(selectedSituation?.title || '');
    setText(selectedSituation?.text || '');
  }, [selectedSituation]);

  const handleUpdate = async (field: 'title' | 'text', value: string) => {
    if (selectedSituation) {
      await updateSituationAndNode(selectedSituation._id, { [field]: value });
    }
  };

  const handleDelete = async () => {
    if (selectedSituation) {
      await deleteSituationAndNode(selectedSituation._id);
      setRenderEditSidebar(false);
      setShowDeleteModal(false);
    }
  };

  const handleReset = () => {
    // This action reverts the entire GVM to its genesis state.
    if (window.confirm('This will revert the groundplane to its initial state. This action cannot be undone. Proceed?')) {
      resetState();
    }
  }

  const renderTabContent = () => {
    switch (activeEditTab) {
      case '2': // Links Tab
        return <ChoicesList />;
      case '3': // Settings Tab
        return (
          <div className={styles.settingsContainer}>
            <button onClick={() => setShowDeleteModal(true)} className={styles.deleteButton} disabled={loading || selectedSituation?.isStart}>
              Destroy Ethernet Node
            </button>
            <button onClick={handleReset} className={styles.resetButton} disabled={loading}>
              Reset Groundplane
            </button>
          </div>
        );
      case '1': // Content Tab
      default:
        return (
          <div className={styles.form}>
            <label htmlFor="situationTitle" className={styles.label}>Ethernet Node Title</label>
            <input
              id="situationTitle"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onBlur={() => handleUpdate('title', title)}
              className={styles.input}
              placeholder="Enter Cell Title"
            />
            <label htmlFor="situationText" className={styles.label}>Semantic Content</label>
            <textarea
              id="situationText"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onBlur={() => handleUpdate('text', text)}
              className={styles.textarea}
              placeholder="Describe the state or function of this Cell..."
            />
          </div>
        );
    }
  };

  return (
    <div className={styles.editSituationContainer}>
      <EditSidebarTabs editType="situation" />
      <div className={styles.scrollableContent}>
        {renderTabContent()}
      </div>
      {showDeleteModal && <DeleteModal type="Cell" onConfirm={handleDelete} onCancel={() => setShowDeleteModal(false)} />}
      {showUploadModal && <UploadModal uploadType={showUploadModal} setIsModalOpen={() => setShowUploadModal(null)} />}
    </div>
  );
};

export default EditSituation;