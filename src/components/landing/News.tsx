'use client';

import React from 'react';
import Carousel from 'react-multi-carousel';
import 'react-multi-carousel/lib/styles.css';

interface NewsItem {
  date: string;
  title: string;
  link: string;
  description: string;
}

const newsItems: NewsItem[] = [
  {
    date: 'August 5–7, 2025',
    title: 'FMS: the Future of Memory & Storage Summit 2025',
    link: 'https://futurememorystorage.com/',
    description: '19th annual global conference at the Santa Clara Convention Center covering all tiers of memory & storage: DRAM, DNA storage, UCIe, CXL, AI/ML, 3D flash, NVMe, ZNS, and more.',
  },
  {
    date: 'August 5–7, 2025',
    title: 'FMS: the Future of Memory and Storage Summit 2025',
    link: 'https://futurememorystorage.com/',
    description: 'Global conference on memory & storage—from DRAM and DNA data storage to CXL, AI/ML, and more—at the Santa Clara Convention Center.',
  },
  {
    date: 'June 24, 2025',
    title: 'Open-Source EDA Birds-of-a-Feather @ DAC 2025',
    link: 'https://open-source-eda-birds-of-a-feather.github.io/',
    description: 'Join the Birds-of-a-Feather session on open-source EDA tools, AI/ML integration, benchmarks, education & community practices—free admission (DAC badge required).',
  },
  {
    date: 'June 23, 2025',
    title: 'HEMBUS Micro-grid Energy Management Platform',
    link: 'https://w3.hembus.com/',
    description: 'HEMBUS unveils a patented micro-grid energy management system to provide reliable power during catastrophic events by balancing local demand with all available generation and storage.',
  },
  {
    date: 'June 22, 2025',
    title: 'Reversible Computing Escapes the Lab',
    link: 'https://spectrum.ieee.org/reversible-computing',
    description: 'IEEE Spectrum explores how reversible computing is moving from theory into practical, energy-efficient architectures.',
  },
  {
    date: 'June 21, 2025',
    title: 'Networking | Docker Docs',
    link: 'https://docs.docker.com/engine/network/',
    description: 'Official Docker documentation on container networking with the Engine Networking API and drivers.',
  },
  {
    date: 'June 20, 2025',
    title: 'Keynote: Networking for AI & HPC (Ultra Ethernet)',
    link: 'https://www.youtube.com/watch?v=0roIi1pscts',
    description: 'Watch the OAP keynote on next-gen Ethernet for AI and high-performance computing workloads.',
  },
  {
    date: 'June 26, 2025',
    title: 'F-Tile Overview',
    link: 'https://www.intel.com/content/www/us/en/docs/programmable/683872/24-1-4-8-0/f-tile-overview.html',
    description: 'Intel’s F-Tile architecture: a snapshot of its fabric, interconnect, and compute tile design for high-density FPGAs.',
  },
  {
    date: 'June 24, 2025',
    title: 'GraalVM: Universal Virtual Machine',
    link: 'https://www.graalvm.org/',
    description: 'High-performance runtime that supports multiple languages and execution modes, enabling polyglot applications with low overhead.',
  },
  {
    date: 'June 24, 2025',
    title: 'SLURM Quickstart Guide',
    link: 'https://slurm.schedmd.com/quickstart.html',
    description: 'An introduction to SLURM’s architecture and basic commands for scheduling and running jobs across an HPC cluster.',
  },
  {
    date: 'June 20, 2025',
    title: 'ALOHAnet: The Original Wireless Packet Network',
    link: 'https://en.wikipedia.org/wiki/ALOHAnet',
    description: 'A retrospective on ALOHAnet, the pioneering packet‐radio network that laid the groundwork for modern Ethernet and Wi-Fi.',
  },
  {
    date: 'June 22, 2025',
    title: 'Pure vs Slotted ALOHA Compared',
    link: 'https://www.geeksforgeeks.org/computer-networks/differences-between-pure-and-slotted-aloha/',
    description: 'An accessible breakdown of the core differences between Pure ALOHA and Slotted ALOHA collision-avoidance techniques.',
  },
  {
    date: 'June 18, 2025',
    title: 'Open Atomic Ethernet Initiative',
    link: 'https://www.opencompute.org/projects/open-atomic-ethernet',
    description: 'The Open Compute Project launches the Open Atomic Ethernet initiative to develop open-source, high-performance Ethernet hardware and reference designs.',
  },
  {
    date: 'June 16, 2025',
    title: 'Packet-Spraying Attack Notes',
    link: '/Packct-Spraying.pdf',
    description: 'Detailed simulation results of packet-spraying attacks against CSMA/CD.',
  },
  {
    date: 'June 5, 2025',
    title: 'Bandwidth Works in Practice, not in Theory',
    link: '/Bandwidth-Works-in-Practice-not-in-Theory.pdf',
    // We challenge the notion that fatter pipes alone solve the fundamental problems of distributed systems.
    // As stated in our research, "there is more to bandwidth than # of bits/second that makes it useful, and there's more nuance to latency that will stall distributed applications no matter how fast the hardware gets."
    description: 'Our latest paper challenges conventional networking wisdom and introduces a new perspective on bandwidth and latency.'
  },
  {
    date: 'May 20, 2025',
    title: 'Project Daedaelus featured in ItsAboutTime.Club',
    link: 'https://itsabouttime.club/',
    // Our 'time-reversible' constructors are gaining attention, moving away from the "irreversible smash and restart of Shannon information" to recover from failures.
    description: 'Traditionalizing our innovative approach to building efficient, decentralized systems.'
  },
  {
    date: 'April 15, 2025',
    title: 'Announcing the DDL_Emulator v0.1',
    link: 'https://github.com/gladishd/DDL_Emulator/tree/refactor/n2n-neighbor-discovery',
    // We're releasing a 'Precise information-theoretic' emulator to enable competitive interactions for 'Digital Twins'.
    description: 'Now developers can test our protocol stack and build their own time-reversible applications.'
  }
];

// This configuration defines the responsive behavior of the carousel.
// It is an adaptive ruleset, ensuring the view conforms to the observer's local environment (viewport)
// rather than being a fragile, fixed-width layout. A fixed cartesian coordinate system would be far too fragile.
const responsive = {
  superLargeDesktop: { breakpoint: { max: 4000, min: 3000 }, items: 5 },
  desktop: { breakpoint: { max: 3000, min: 1024 }, items: 4 },
  tablet: { breakpoint: { max: 1024, min: 640 }, items: 2 },
  mobile: { breakpoint: { max: 640, min: 0 }, items: 1 },
};

const NewsCarousel: React.FC = () => {
  return (
    <section className="py-20 px-4 bg-[#32373c0b]">
      <h2 className="text-4xl font-bold text-center mb-8">Latest News & Updates</h2>
      <div className="max-w-7xl mx-auto">
        {/*
          By replacing the simple, passive scroll-snap container with an arbitrated Carousel,
          we create a more managed and predictable user interface. This reflects our core principle
          of moving away from contended, broadcast-style resources toward structured, reliable systems.
        */}
        <Carousel
          responsive={responsive}
          infinite={true}
          autoPlay={true}
          autoPlaySpeed={5000}
          keyBoardControl={true}
          customTransition="transform 500ms ease-in-out"
          containerClass="carousel-container"
          itemClass="p-4" // Use padding on the item class for spacing
        >
          {newsItems.map((item, idx) => (
            <div key={idx} className="h-full">
              <div className="news-card p-6 h-full flex flex-col justify-between">
                <div>
                  <p className="news-card-date">{item.date}</p>
                  <h3 className="news-card-title">{item.title}</h3>
                  <p className="news-card-description">{item.description}</p>
                </div>
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="news-card-link mt-4 inline-block font-semibold"
                >
                  {item.link}
                </a>
              </div>
            </div>
          ))}
        </Carousel>
      </div>
    </section>
  );
};

export default NewsCarousel;