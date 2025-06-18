// The SideMenu provides a structured, hierarchical view of the application's primary sections.
// It acts as a map to the Graph Virtual Machine's different information spaces, allowing users
// to navigate between the foundational Library, the interactive Digital Twins (emulators),
// and the core architectural arguments.
'use client';

import React from 'react';
import Link from 'next/link';
import { useMenu } from '@/context/MenuContext';
import { X } from 'lucide-react';
import { FaBook, FaFlask, FaProjectDiagram } from 'react-icons/fa';

const SideMenu = () => {
  const { isMenuOpen, closeMenu } = useMenu();

  // The menu items define the primary navigational pathways of the application.
  const menuItems = [
    { href: '/#', label: 'Strategic Initiatives', icon: <FaProjectDiagram /> },
    { href: '/#library', label: 'Dædælus Library', icon: <FaBook /> },
    // This href is updated to point to the dedicated models page, reflecting a more structured information architecture.
    { href: '/models', label: 'Live Computational Models', icon: <FaFlask /> },
  ];

  // A 'Ruleset' to enable a non-zero-sum game outcome; in this case, a clear and ordered navigation.
  const romanNumerals = ['II', 'III', 'IV'];

  return (
    <>
      <div
        className={`side-menu-backdrop ${isMenuOpen ? 'active' : ''}`}
        onClick={closeMenu}
      />
      <nav className={`side-menu ${isMenuOpen ? 'open' : ''}`}>
        <div className="side-menu-header">
          {/* The primary entry point, the root of the navigation tree, is marked accordingly. */}
          <h3 className="font-bold">I. Home...</h3>
          <button onClick={closeMenu} className="p-1 rounded-full hover:bg-gray-200">
            <X size={20} />
          </button>
        </div>
        <ul className="side-menu-list">
          {menuItems.map((item, index) => {
            // The subsequent entries are enumerated to reflect their position in the hierarchy.
            const romanNumeral = romanNumerals[index];
            return (
              <li key={item.label}>
                <Link href={item.href} onClick={closeMenu} className="side-menu-item">
                  <span className="side-menu-icon">{item.icon}</span>
                  {/* We use a fixed-width container for the numeral to ensure all labels are vertically aligned.
                      This creates a structured, predictable layout, not a fragile, adaptive one. */}
                  <span className="w-6 text-left font-medium">{romanNumeral}.</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
        <div className="side-menu-footer">
          <p>© {new Date().getFullYear()} Dædælus Research</p>
        </div>
      </nav>
    </>
  );
};

export default SideMenu;