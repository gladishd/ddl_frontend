// The footer acts as a stable foundation, providing enduring links to key information about our architecture and mission.
'use client';

import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-[#8c1515] text-white p-12">
      <div className="container mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <img src="/reverseLogo.png" className="h-12 mb-4" alt="Dædælus Logo" />
          <p>&copy; {new Date().getFullYear()} Dædælus Research</p>
        </div>
        <div>
          <h3 className="font-bold mb-4">Explore</h3>
          <ul>
            <li className="mb-2"><a href="#" className="hover:underline">Digital Twins</a></li>
            <li className="mb-2"><a href="#" className="hover:underline">Graph Virtual Machine</a></li>
            <li className="mb-2"><a href="#" className="hover:underline">Transaction Processing</a></li>
          </ul>
        </div>
        <div>
          <h3 className="font-bold mb-4">About</h3>
          <ul>
            <li className="mb-2"><a href="#" className="hover:underline">Our Mission</a></li>
            <li className="mb-2"><a href="#" className="hover:underline">Privacy Policy</a></li>
          </ul>
        </div>
        <div>
          <h3 className="font-bold mb-4">Contact</h3>
          <p>admin@daedelus.io</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;