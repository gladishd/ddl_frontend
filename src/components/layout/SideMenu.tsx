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

  const menuItems = [
    { href: '/#', label: 'Strategic Initiatives', icon: <FaProjectDiagram /> },
    { href: '/#library', label: 'Dædælus Library', icon: <FaBook /> },
    { href: '/#live-models', label: 'Live Computational Models', icon: <FaFlask /> },
  ];

  return (
    <>
      <div
        className={`side-menu-backdrop ${isMenuOpen ? 'active' : ''}`}
        onClick={closeMenu}
      />
      <nav className={`side-menu ${isMenuOpen ? 'open' : ''}`}>
        <div className="side-menu-header">
          <h3 className="font-bold">Navigation</h3>
          <button onClick={closeMenu} className="p-1 rounded-full hover:bg-gray-200">
            <X size={20} />
          </button>
        </div>
        <ul className="side-menu-list">
          {menuItems.map((item) => (
            <li key={item.label}>
              <Link href={item.href} onClick={closeMenu} className="side-menu-item">
                <span className="side-menu-icon">{item.icon}</span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
        <div className="side-menu-footer">
          <p>© {new Date().getFullYear()} Dædælus Research</p>
        </div>
      </nav>
    </>
  );
};

export default SideMenu;