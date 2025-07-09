// This component provides the editing interface for a selected 'TRAPH' (Group).
// A TRAPH is a fundamental construct for confinement and hierarchical management.
// This interface allows manipulation of the TRAPH's metadata and provides a
// Local Observer View (LOV) of the Cells it contains.
'use client';

import React, { useState, useEffect, useMemo, useContext } from 'react';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import styles from './styles/EditGroup.module.css';
import EditSidebarTabs from './EditSidebarTabs';
import SituationsList from './SituationsList';
import DeleteModal from './DeleteModal';
import { Situation } from '@/types/canvas/Situation';

interface EditGroupProps {
  setRenderEditSidebar: (render: boolean) => void;
}

const EditGroup: React.FC<EditGroupProps> = ({ setRenderEditSidebar }) => {
  const { selectedGroup, situations, updateGroup, deleteGroup, activeEditTab, loading } = useContext(CanvasContext);
  const [title, setTitle] = useState(selectedGroup?.title || '');
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    setTitle(selectedGroup?.title || 'Untitled TRAPH');
  }, [selectedGroup]);

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value);
  };

  // This is a transaction to update the metadata of the TRAPH.
  const handleTitleBlur = async () => {
    if (selectedGroup && title !== selectedGroup.title) {
      await updateGroup(selectedGroup._id, { title });
    }
  };

  const handleDelete = async () => {
    if (selectedGroup) {
      await deleteGroup(selectedGroup._id);
      setRenderEditSidebar(false);
      setShowDeleteModal(false);
    }
  };

  const containedSituations = useMemo(() => {
    if (!selectedGroup) return [];
    return situations.filter((s: Situation) => s.situationGroup === selectedGroup._id);
  }, [situations, selectedGroup]);

  const renderTabContent = () => {
    switch (activeEditTab) {
      case '2': // Cells Tab
        return <SituationsList situations={containedSituations} />;
      case '3': // Settings Tab
        return (
          <div className={styles.settingsContainer}>
            <button
              onClick={() => setShowDeleteModal(true)}
              className={styles.deleteButton}
              disabled={loading || selectedGroup?.isDefault}
              title={selectedGroup?.isDefault ? "Cannot delete the default group" : "Destroy Group"}
            >
              Destroy TRAPH
            </button>
          </div>
        );
      case '1': // Content Tab
      default:
        return (
          <div className={styles.form}>
            <label htmlFor="groupTitle" className={styles.label}>TRAPH Title</label>
            <input
              id="groupTitle"
              type="text"
              value={title}
              onChange={handleTitleChange}
              onBlur={handleTitleBlur}
              className={styles.input}
              placeholder="Enter Group Title"
            />
          </div>
        );
    }
  };

  return (
    <div className={styles.editGroupContainer}>
      <EditSidebarTabs editType="group" />
      <div className={styles.scrollableContent}>
        {renderTabContent()}
      </div>
      {showDeleteModal && (
        <DeleteModal
          type="Group"
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteModal(false)}
        />
      )}
    </div>
  );
};

export default EditGroup;