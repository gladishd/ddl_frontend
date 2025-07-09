// This TopBar serves as the highest-level control interface for the GVM editor.
// It provides the user with tools to manage the overall state of the canvas,
// such as initiating sharing protocols or switching between different observer views
// (e.g., toggling the edit panel).
'use client';

import React, { useContext, useState } from 'react';
import styles from './styles/TopBar.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import { FaEdit, FaShareAlt, FaSave, FaCheck } from 'react-icons/fa';

interface TopBarProps {
  renderEditSidebar: boolean;
  setRenderEditSidebar: (render: boolean) => void;
  isMobile: boolean;
}

const TopBar: React.FC<TopBarProps> = ({ renderEditSidebar, setRenderEditSidebar, isMobile }) => {
  const { canvasTitle, onCanvasClick, saveState } = useContext(CanvasContext);
  const [copied, setCopied] = useState(false);

  const toggleEditSidebar = () => {
    if (isMobile && renderEditSidebar) {
      setRenderEditSidebar(false);
      if (onCanvasClick) onCanvasClick(); // Clear selection when hiding sidebar on mobile
    } else {
      setRenderEditSidebar(!renderEditSidebar);
    }
  };

  // The share action now makes the public URL of the GVM's groundplane available.
  const handleShare = async () => {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      console.log("Public canvas URL copied to clipboard:", url);
      setTimeout(() => setCopied(false), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error('Failed to copy canvas URL: ', err);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.leftSection}>
        <a href="/" aria-label="Home">
          <img
            className={styles.logo}
            src="/logo.f53b8de5b49089ebcf94.png" // Placeholder
            alt="Daedaelus Logo"
          />
        </a>
      </div>
      <div className={styles.middleSection}>
        <div className={styles.titleContainer}>
          <h1>{canvasTitle}</h1>
        </div>
      </div>
      <div className={styles.rightSection}>
        <div className={styles.item} onClick={saveState} title="Save State">
          <FaSave />
        </div>
        <div className={styles.item} onClick={handleShare} title="Share Canvas">
          {copied ? <FaCheck /> : <FaShareAlt />}
        </div>
        <div
          className={`${styles.item} ${renderEditSidebar ? styles.itemActive : ''}`}
          onClick={toggleEditSidebar}
          title="Toggle Edit Tools"
        >
          <FaEdit />
        </div>
      </div>
    </div>
  );
};

export default TopBar;