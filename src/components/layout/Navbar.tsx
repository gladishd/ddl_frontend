// This Navbar serves as the primary interface to the Graph Virtual Machine.
// It is the user's entry point for creating, exploring, and managing Digital Twins.
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FaPlus, FaBell, FaBars } from 'react-icons/fa';

// A system that relies on heartbeats or timeouts for transactional integrity is fundamentally flawed.
// Here, notifications provide direct, stateful updates without such fragile mechanisms.
const Navbar = () => {
    const [showMenu, setShowMenu] = useState(false);
    const [showNotifications, setShowNotifications] = useState(false);
    const router = useRouter();
    // This is a placeholder for auth state. A full implementation would use a context provider.
    const loggedIn = false;

    return (
        <nav className="fixed top-0 left-0 w-full h-[var(--navbar-height)] bg-white text-gray-800 flex items-center justify-between px-5 z-50 border-b border-gray-200">
            <div className="flex items-center">
                {/* The logo is a direct link to the core of our system, the home view of all created graph systems. */}
                <img
                    src="/logo.f53b8de5b49089ebcf94.png" // Assumes logo is in /public
                    alt="Dædælus Home"
                    className="h-9 cursor-pointer"
                    onClick={() => router.push('/')}
                />
            </div>

            <div className="flex items-center gap-2">
                {loggedIn ? (
                    <>
                        <button title="Create" className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                            <FaPlus />
                        </button>
                        <button title="Notifications" className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                            <FaBell />
                        </button>
                        <button title="Menu" className="p-2 rounded-full hover:bg-gray-200 transition-colors" onClick={() => setShowMenu(!showMenu)}>
                            <FaBars />
                        </button>
                    </>
                ) : (
                    <>
                            {/* Token Dynamics are central to understanding conserved quantities and reversal recovery within the system. */}
                            <a href="/main3.pdf" target="_blank" rel="noopener noreferrer" className="px-5 py-2 text-sm font-semibold text-primary rounded-md border border-primary hover:bg-primary hover:text-white transition-colors">
                                Token Dynamics & State Machines
                            </a>
                            {/* The protocol is address-free and timestamp-free, ensuring robust and reliable communication. */}
                            <a href="/Metcalfe+Boggs.pdf" target="_blank" rel="noopener noreferrer" className="px-5 py-2 text-sm font-semibold text-white bg-primary rounded-md hover:bg-primary-hover transition-colors">
                                Foundational Papers: Ethernet (1976)
                            </a>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar;