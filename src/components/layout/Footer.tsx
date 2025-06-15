'use client';

import React from 'react';
import Link from 'next/link';

const Footer = () => (
  <footer className="bg-[#8c1515] text-white p-12">
    {/* 5 columns on ≥ md, 1 column on mobile */}
    <div className="container mx-auto grid grid-cols-1 md:grid-cols-5 gap-8">
      {/* ─────────── Brand / copyright ─────────── */}
      <div>
        <img
          src="/logo.f53b8de5b49089ebcf94.png"
          alt="Dædælus Logo"
          className="h-12 mb-4"
        />
        <p>&copy; {new Date().getFullYear()} Dædælus Research</p>
      </div>

      {/* ─────────── Assumptions & Concepts ─────────── */}
      <div>
        <h3 className="font-bold mb-4">Assumptions & Concepts</h3>
        <ul>
          <li className="mb-2">
            <Link href="https://www.wolframphysics.org/technical-introduction/multiway-systems/" target="_blank" className="hover:underline">
              Multiway Systems (Wolfram Physics)
            </Link>
          </li>
          <li className="mb-2">
            <Link href="https://en.wikipedia.org/wiki/Petri_net" target="_blank" className="hover:underline">
              Petri-Net Models
            </Link>
          </li>
          <li className="mb-2">
            <Link href="https://en.wikipedia.org/wiki/Reversible_computing" target="_blank" className="hover:underline">
              Reversible Computing
            </Link>
          </li>
          <li className="mb-2">
            <Link href="https://hpbn.co/primer-on-latency-and-bandwidth/" target="_blank" className="hover:underline">
              Latency vs Bandwidth Primer
            </Link>
          </li>
        </ul>
      </div>

      {/* ─────────── Foundations ─────────── */}
      <div>
        <h3 className="font-bold mb-4">Foundations</h3>
        <ul>
          <li className="mb-2">
            <Link href="https://en.wikipedia.org/wiki/Packet_switching" target="_blank" className="hover:underline">
              Packet Switching (1970 – )
            </Link>
          </li>
          <li className="mb-2">
            <Link href="http://link.aps.org/doi/10.1103/PhysRevX.15.021044" target="_blank" className="hover:underline">
              Multiscale Field Theory for Flows
            </Link>
          </li>
          <li className="mb-2">
            <Link href="https://dl.acm.org/doi/10.1145/363347.363366" target="_blank" className="hover:underline">
              Reliable Full-Duplex Tx over HDX Lines
            </Link>
          </li>
          <li className="mb-2">
            <Link href="https://www.wired.com/1993/03/negroponte-14" target="_blank" className="hover:underline">
              Debunking Bandwidth (Negroponte ’93)
            </Link>
          </li>
        </ul>
      </div>

      {/* ─────────── Resources ─────────── */}
      <div>
        <h3 className="font-bold mb-4">Resources</h3>
        <ul>
          <li className="mb-2">
            <Link href="https://github.com/gladishd/DDL_Emulator" target="_blank" className="hover:underline">
              DDL_Emulator (GitHub)
            </Link>
          </li>
          <li className="mb-2">
            <Link href="https://itsabouttime.club/" target="_blank" className="hover:underline">
              ItsAboutTime.Club Blog
            </Link>
          </li>
          <li className="mb-2">
            <Link href="https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb"
              target="_blank" className="hover:underline">
              Live Wolfram Notebook
            </Link>
          </li>
          <li className="mb-2">
            <Link href="https://arxiv.org/abs/1901.11274" target="_blank" className="hover:underline">
              Reversible Petri Nets (arXiv 1901.11274)
            </Link>
          </li>
        </ul>

        {/* Contact kept unchanged */}
        <h3 className="font-bold mb-4 mt-6">Contact</h3>
        <p>sahas.munamala@ocproject.net</p>
        <p>dgladish3@gatech.edu</p>
      </div>

      {/* ─────────── Legal (unchanged) ─────────── */}
      {/* ───────────────────────── NEW: Legal ─────────────────────────────── */}
      <div>
        <h3 className="font-bold mb-4">Legal</h3>
        <ul>
          <li className="mb-2">
            <Link href="/1   83 b election word  cover letter doc 1 1 20 2024[2305843009330875417].pdf"
              target="_blank" className="hover:underline">
              83(b) Election – Cover Letter
            </Link>
          </li>
          <li className="mb-2">
            <Link href="/2 DAE Inc RSPA 83 (b) Instructions to File 83 (b) Election 1 21 2024.pdf"
              target="_blank" className="hover:underline">
              83(b) Election – Filing Instructions
            </Link>
          </li>
          <li className="mb-2">
            <Link href="/3  Daedaelus Inc. -  Exhibit A Equity Incentive Plan 1 21 2024.pdf"
              target="_blank" className="hover:underline">
              Equity Incentive Plan (Exhibit A)
            </Link>
          </li>
          <li className="mb-2">
            <Link href="/4  Daedaelus Inc. - 1Form of Stock Option Agreement 2025.pdf"
              target="_blank" className="hover:underline">
              Stock Option Agreement (2025)
            </Link>
          </li>
          <li className="mb-2">
            <Link href="/5 Daedaelus Inc. - Consulting Agreement  2025.pdf"
              target="_blank" className="hover:underline">
              Consulting Agreement (2025)
            </Link>
          </li>
          <li className="mb-2">
            <Link href="/6 The Undersigned taxpayer herby elects pursuant to Section 83 June 2025.pdf"
              target="_blank" className="hover:underline">
              Section 83(b) Election Form (2025)
            </Link>
            </li>
          </ul>
        </div>
    </div>
  </footer>
);

export default Footer;
