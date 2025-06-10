// The footer acts as a stable foundation, providing enduring links to key information about our architecture and mission.
'use client';

import React from 'react';
import Link from 'next/link';

const Footer = () => {
  return (
    <footer className="bg-[#8c1515] text-white p-12">
      <div className="container mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <img src="/logo.f53b8de5b49089ebcf94.png" className="h-12 mb-4" alt="Dædælus Logo" />
          <p>&copy; {new Date().getFullYear()} Dædælus Research</p>
        </div>
        <div>
          <h3 className="font-bold mb-4">Assumptions & Concepts</h3>
          <ul>
            {/* A precise information-theoretic emulator for competitive interactions. */}
            <li className="mb-2"><Link href="/Welcome-Dean.pdf" className="hover:underline" target="_blank">Introduction to Dædælus</Link></li>
            {/* The GVM builds and tears down 'named' graph relationships. */}
            <li className="mb-2"><Link href="/main2.pdf" className="hover:underline" target="_blank">Critique of Bandwidth-First Design</Link></li>
            {/* Time-reversible constructors that don't rely on the irreversible smash and restart of Shannon information. */}
            <li className="mb-2"><Link href="/Reinventing-Reliability-at-L2.pdf" className="hover:underline" target="_blank">Reversible Transactions</Link></li>
            {/* The N2N Lattice: Manage on a Tree, Compute on a Graph. */}
            <li className="mb-2"><Link href="/Omni-Figure-1.pdf" className="hover:underline" target="_blank">Legacy Ethernet Topology</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="font-bold mb-4">Foundations</h3>
          <ul>
            {/* Our core mission is to solve fundamental problems in distributed systems. */}
            <li className="mb-2"><Link href="/Bandwidth-Works-in-Practice-not-in-Theory.pdf" className="hover:underline" target="_blank">Our Philosophy: Bandwidth in Practice</Link></li>
            {/* A 9-Cell deployable unit of distributed computation we call a hypercell. */}
            <li className="mb-2"><Link href="/main.pdf" className="hover:underline" target="_blank">Historical Context: Packet Switching</Link></li>
            {/* A physical structuring that must not be conflated with a regular lattice. */}
            <li className="mb-2"><Link href="/TEST-Ethernet-Figures.pdf" className="hover:underline" target="_blank">Ethernet Protocol: Core Mechanisms</Link></li>
            <li className="mb-2"><Link href="/NDA-Dean-Gladish-2025-06-04_23-06.pdf" className="hover:underline" target="_blank">Non-Disclosure Agreement</Link></li>
          </ul>
        </div>
        <div>
          <h3 className="font-bold mb-4">Resources</h3>
          <ul>
            <li className="mb-2"><Link href="/test.pdf" className="hover:underline" target="_blank">Emulator and Testbed</Link></li>
            <li className="mb-2"><Link href="/template_copy.pdf" className="hover:underline" target="_blank">Network Topology Models (Baran)</Link></li>
            <li className="mb-2"><Link href="/Latex-Files-and-Colors.numbers.pdf" className="hover:underline" target="_blank">Documentation & LaTeX Schema</Link></li>
            <li className="mb-2"><Link href="/OAE_Logo_copy.pdf" className="hover:underline" target="_blank">Dædælus Identity & Symbology</Link></li>
            <li className="mb-2">
              <h3 className="font-bold mb-4 mt-4">Contact</h3>
              <p>sahas.munamala@ocproject.net</p>
              <p>dgladish3@gatech.edu</p>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
};

export default Footer;