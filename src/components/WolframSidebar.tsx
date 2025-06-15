"use client";

import React from 'react';
import { FaFlask, FaSlidersH, FaLink } from 'react-icons/fa';
import Link from 'next/link';

// The sidebar for the Wolfram emulator provides a control plane for interaction.
// It is analogous to the classroom sidebar, offering structured navigation and
// contextual actions related to the 'Digital Twin' it accompanies.
const WolframSidebar = () => {
  const mainLinks = [
    { label: 'Model Parameters', path: '#', icon: <FaSlidersH className="wolfram-sidebar-icon" /> },
    { label: 'Run Experiment', path: '#', icon: <FaFlask className="wolfram-sidebar-icon" /> },
  ];

  const relatedDocs = [
    { title: 'Packet Switching – Historical Context', href: '/main.pdf' },
    { title: 'Critique of Bandwidth-First Design', href: '/main2.pdf' },
  ];

  return (
    <aside className="wolfram-sidebar-container">
      <div className="wolfram-sidebar-header">
        <h3 className="wolfram-sidebar-title">Emulator Controls</h3>
        <p className="wolfram-sidebar-subtitle">Interact with the Live Model</p>
      </div>
      <nav className="wolfram-sidebar-nav">
        <ul className="wolfram-sidebar-list">
          {mainLinks.map(link => (
            <li key={link.label}>
              <a href={link.path} className="wolfram-sidebar-item">
                {link.icon} {link.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
      <div className="wolfram-sidebar-divider" />
      <div className="wolfram-sidebar-related-docs">
        <h4 className="wolfram-sidebar-section-title">Related Documents</h4>
        <ul className="wolfram-sidebar-list">
          {relatedDocs.map(doc => (
            <li key={doc.title}>
              <Link href={doc.href} target="_blank" className="wolfram-sidebar-item">
                <FaLink className="wolfram-sidebar-icon" /> {doc.title}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
};

export default WolframSidebar;