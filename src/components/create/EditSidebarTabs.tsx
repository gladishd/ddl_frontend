import React, { useContext } from 'react';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import styles from './styles/EditSidebarTabs.module.css';

type EditType = 'situation' | 'choice' | 'group';

interface EditSidebarTabsProps {
  editType: EditType;
}

// These tabs separate the configuration of a GVM element into distinct layers of concern.
// This enforces a structured approach to modification, separating an element's semantic
// content from its operational settings.
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
        return 'Settings';
      default:
        return '';
    }
  };

  // The interface is streamlined to two primary concerns: the element's content,
  // and its operational settings. All other interactions are handled directly on the canvas.
  const tabs = ['1', '2'];

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