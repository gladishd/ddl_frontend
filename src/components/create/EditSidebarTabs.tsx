import React, { useContext } from 'react';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import styles from './styles/EditSidebarTabs.module.css';

type EditType = 'situation' | 'choice' | 'group';

interface EditSidebarTabsProps {
  editType: EditType;
}

// These tabs separate the configuration of a GVM element into distinct layers of concern.
// This enforces a structured approach to modification, separating an element's semantic
// content from its operational settings and contained elements.
const EditSidebarTabs: React.FC<EditSidebarTabsProps> = ({ editType }) => {
  const { activeEditTab, setActiveEditTab } = useContext(CanvasContext);

  const handleTabClick = (tab: string) => {
    if (setActiveEditTab) setActiveEditTab(tab);
  };

  const getTabLabel = (tab: string): string => {
    switch (tab) {
      case '1':
        return 'Content';
      case '2':
        // The label for the second tab is context-dependent, reflecting the element type.
        // For a Cell, it shows its outgoing Links. For a TRAPH, its contained Cells.
        if (editType === 'situation') return 'Links';
        if (editType === 'group') return 'Cells';
        return 'Target';
      case '3':
        return 'Settings';
      default:
        return '';
    }
  };

  // The interface is streamlined to three primary concerns: content, contained elements, and settings.
  const tabs = ['1', '2', '3'];

  return (
    <div className={styles.tabsContainer}>
      {tabs.map((tab) => (
        <div
          key={tab}
          className={`${styles.tab} ${activeEditTab === tab ? styles.activeTab : ''}`}
          onClick={() => handleTabClick(tab)}
        >
          {getTabLabel(tab)}
        </div>
      ))}
    </div>
  );
};

export default EditSidebarTabs;