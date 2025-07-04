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
  },
  {
    date: 'July 4, 2025',
    title: 'OCP All Main Discussion Group',
    link: 'https://ocp-all.groups.io/g/main',
    description: 'The main discussion group for the Open Compute Project (OCP) community, covering all topics related to open hardware and data center innovation.',
  },
  {
    date: 'July 4, 2025',
    title: 'Open Atomic Ethernet - OpenCompute',
    link: 'https://www.opencompute.org/w/index.php?title=Open_Atomic_Ethernet',
    description: 'The official wiki page for the Open Atomic Ethernet project, providing details on the project\'s goals, specifications, and progress.',
  },
  {
    date: 'July 4, 2025',
    title: 'ECCC Report: On Perfect Zero-Knowledge and Secure Computation',
    link: 'https://eccc.weizmann.ac.il/report/2025/017/',
    description: 'A report from the Electronic Colloquium on Computational Complexity (ECCC) on perfect zero-knowledge, secure computation, and the foundations of cryptography.',
  },
  {
    date: 'July 4, 2025',
    title: 'Weizmann Institute of Science',
    link: 'https://www.weizmann.ac.il/pages/',
    description: 'The official website of the Weizmann Institute of Science, a leading multidisciplinary research institution.',
  },
  {
    date: 'July 4, 2025',
    title: 'IEEE Xplore Author Profile: David H. Wolpert',
    link: 'https://ieeexplore.ieee.org/author/37088318764',
    description: 'The IEEE Xplore profile of David H. Wolpert, showcasing his publications and contributions to the field.',
  },
  {
    date: 'July 4, 2025',
    title: 'RoCQ Prover Project',
    link: 'https://rocq-prover.org/',
    description: 'The official website for the RoCQ Prover, a project focused on the development of a formal proof assistant.',
  },
  {
    date: 'July 4, 2025',
    title: 'Wolfram Language: General::partw Message',
    link: 'https://reference.wolfram.com/legacy/language/v14/ref/message/General/partw.html?v=14.0',
    description: 'Documentation for the "partw" message in the Wolfram Language, which is issued when a part specification is longer than the depth of the expression.',
  },
  {
    date: 'July 4, 2025',
    title: 'OCP TAP Discussion Group',
    link: 'https://ocp-all.groups.io/g/OCP-TAP/joined',
    description: 'The discussion group for the Open Compute Project\'s Time Appliances Project (TAP).',
  },
  {
    date: 'July 17, 2024',
    title: 'Time Appliances Project Call #105 (July 17, 2024)',
    link: 'https://www.youtube.com/watch?v=ll5aF-oN-YE',
    description: 'A recording of the Time Appliances Project Call #105, which took place on July 17, 2024.',
  },
  {
    date: 'July 15, 2014',
    title: 'Leslie Lamport: Thinking Above the Code',
    link: 'https://www.youtube.com/watch?v=-4Yp3j_jk8Q',
    description: 'A talk by Leslie Lamport on the importance of thinking about specifications and abstractions before writing code.',
  },
  {
    date: 'December 13, 2024',
    title: 'Yotam Bentov on Error Detecting and Error Correcting Codes [PWL NYC]',
    link: 'https://www.youtube.com/watch?v=i4HEp9vaM6Q',
    description: 'A talk from Papers We Love NYC by Yotam Bentov on error detecting and error correcting codes.',
  },
  {
    date: 'June 21, 2023',
    title: 'Ori Bernstein on An Introduction to Bε-trees and Write-Optimization [PWL NYC]',
    link: 'https://www.youtube.com/watch?v=v_g4eZeWAng',
    description: 'A talk from Papers We Love NYC by Ori Bernstein on Bε-trees and write-optimization techniques.',
  },
  {
    date: 'January 3, 2019',
    title: 'Time, Clocks and Ordering of Events in a Dist. System by Dan Rubenstein [PWL NYC]',
    link: 'https://www.youtube.com/watch?v=hK6m6WBk-d8',
    description: 'A talk from Papers We Love NYC by Dan Rubenstein on Lamport\'s seminal paper on time, clocks, and the ordering of events in a distributed system.',
  },
  {
    date: 'September 26, 2016',
    title: '"Design Philosophy in Networked Systems" by Justine Sherry',
    link: 'https://www.youtube.com/watch?v=aR_UOSGEizE',
    description: 'A talk by Justine Sherry on design philosophy in networked systems.',
  },
  {
    date: 'June 17, 2018',
    title: 'Wandering Threads - Virtualizing SMP',
    link: 'https://www.youtube.com/watch?v=Bh5axlxIUvM',
    description: 'A video by Kevin Cameron on "Wandering Threads," a concept for virtualizing Symmetric Multiprocessing (SMP).',
  },
  {
    date: 'July 4, 2025',
    title: 'Axiomtek Edge AI GPU Computing',
    link: 'https://us.axiomtek.com/Default.aspx?MenuId=Products&FunctionId=ProductCat&Cat=398&C=Edge+AI+GPU+Computing',
    description: 'Axiomtek\'s lineup of Edge AI GPU computing solutions, designed for AI-powered applications at the edge.',
  },
  {
    date: 'July 4, 2025',
    title: 'OCP Ready Program',
    link: 'https://www.opencompute.org/wiki/Data_Center_Facility/OCP_Ready',
    description: 'Information on the Open Compute Project\'s "OCP Ready" program, which certifies data centers that meet OCP standards.',
  },
  {
    date: 'July 4, 2025',
    title: 'Wolfram Language: Options',
    link: 'https://reference.wolfram.com/legacy/language/v14/ref/Options.html?v=14.0',
    description: 'Documentation for the "Options" function in the Wolfram Language, which is used to get and set options for functions and symbols.',
  },
  {
    date: 'July 4, 2025',
    title: 'Wolfram Language: DefaultNewCellStyle',
    link: 'https://reference.wolfram.com/legacy/language/v14/ref/DefaultNewCellStyle.html?v=14.0',
    description: 'Documentation for the "DefaultNewCellStyle" option in the Wolfram Language, which specifies the default style for new cells.',
  },
  {
    date: 'July 4, 2025',
    title: 'Wolfram Language: How to Plot a Graph',
    link: 'https://reference.wolfram.com/language/howto/PlotAGraph.html',
    description: 'A tutorial on how to plot graphs in the Wolfram Language, with examples and options.',
  },
  {
    date: 'July 4, 2025',
    title: 'Mathematica: Expand All Cells',
    link: 'https://comp.soft-sys.math.mathematica.narkive.com/5PwZRm9U/expand-all-cells',
    description: 'A forum discussion on how to expand all cells in a Mathematica notebook.',
  },
  {
    date: 'July 4, 2025',
    title: 'Java Concurrency: Happens-Before Relationship',
    link: 'https://www.logicbig.com/tutorials/core-java-tutorial/java-multi-threading/happens-before.html',
    description: 'A tutorial explaining the "happens-before" relationship in Java\'s memory model, which is crucial for writing correct concurrent programs.',
  },
  {
    date: 'July 4, 2025',
    title: 'NKS: The Intrinsic Generation of Randomness',
    link: 'https://www.wolframscience.com/nks/p320--the-intrinsic-generation-of-randomness/',
    description: 'An excerpt from Stephen Wolfram\'s "A New Kind of Science" discussing the intrinsic generation of randomness in simple programs.',
  },
  {
    date: 'July 4, 2025',
    title: 'XDC Demonstrates Breakthrough High-Speed Display for Free-Space Optical Wireless Communication',
    link: 'https://www.xdisplay.com/pressrelease/xdc-demonstrates-breakthrough-high-speed-display-for-free-space-optical-wireless-communication/',
    description: 'A press release from XDC announcing a breakthrough in high-speed displays for free-space optical wireless communication.',
  },
  {
    date: 'July 4, 2025',
    title: 'arXiv Paper: "The Unreasonable Effectiveness of Recurrent Neural Networks"',
    link: 'https://arxiv.org/pdf/2003.05542',
    description: 'A research paper discussing the surprising effectiveness of recurrent neural networks in various applications.',
  },
  {
    date: 'July 4, 2025',
    title: 'Book: "Random Number Generators—Principles and Practices: For Scientists and Engineers"',
    link: 'https://www.amazon.com/Random-Number-Generators-Principles-Practice-Programmers/dp/1501515136',
    description: 'A book on random number generators, covering their principles, practices, and applications for scientists and engineers.',
  },
  {
    date: 'July 4, 2025',
    title: 'Book: "Noise and Randomness in Living Systems"',
    link: 'https://books.google.com/books?id=kIxuDwAAQBAJ',
    description: 'A book exploring the role of noise and randomness in living systems, from the molecular level to entire ecosystems.',
  },
  {
    date: 'July 4, 2025',
    title: 'Zenodo: Research. Shared.',
    link: 'https://zenodo.org/',
    description: 'Zenodo is a general-purpose open-access repository developed under the European OpenAIRE program and operated by CERN.',
  },
  {
    date: 'July 4, 2025',
    title: 'Logical Reversibility of Computation',
    link: 'https://mathweb.ucsd.edu/~sbuss/CourseWeb/Math268_2013W/Bennett_Reversibiity.pdf',
    description: 'A paper by Charles H. Bennett on the logical reversibility of computation, a foundational concept in reversible computing.',
  },
  {
    date: 'July 4, 2025',
    title: 'Daedaelus: A New Approach to Distributed Systems',
    link: 'https://daedaelus.com/',
    description: 'The official website of the Daedaelus project, which is developing a new approach to building resilient and efficient distributed systems.',
  },
  {
    date: 'July 4, 2025',
    title: 'Wikipedia: Open Compute Project',
    link: 'https://en.wikipedia.org/wiki/Open_Compute_Project',
    description: 'The Wikipedia page for the Open Compute Project (OCP), providing an overview of its history, goals, and projects.',
  },
  {
    date: 'July 4, 2025',
    title: 'Ether: Distributed Packet Switching for Local Computer Networks',
    link: 'https://dl.acm.org/doi/pdf/10.1145/363347.363366',
    description: 'The original paper by Robert M. Metcalfe and David R. Boggs that introduced the Ethernet protocol.',
  },
  {
    date: 'July 4, 2025',
    title: 'A Note on Reliable Full-Duplex Transmission over Half-Duplex Links',
    link: 'https://dl.acm.org/doi/pdf/10.1145/362946.362970',
    description: 'A research paper discussing techniques for achieving reliable full-duplex transmission over half-duplex communication links.',
  },
  {
    date: 'July 4, 2025',
    title: 'PRX: "Experimental Realization of a Quantum Nanosystem with Controllable Quantum Chaos"',
    link: 'https://journals.aps.org/prx/pdf/10.1103/PhysRevX.15.021044',
    description: 'A paper in Physical Review X on the experimental realization of a quantum nanosystem with controllable quantum chaos.',
  },
  {
    date: 'July 4, 2025',
    title: 'Wikipedia: Alternating Sign Matrix',
    link: 'https://en.wikipedia.org/wiki/Alternating_sign_matrix',
    description: 'The Wikipedia page for alternating sign matrices, a class of matrices with entries 0, 1, and -1, with connections to various areas of mathematics.',
  },
  {
    date: 'July 4, 2025',
    title: 'About Daedaelus',
    link: 'https://daedaelus.com/about/',
    description: 'The about page for the Daedaelus project, providing more information about its mission and team.',
  }
];

// This configuration defines the responsive behavior of the carousel.
// It is an adaptive ruleset, ensuring the view conforms to the observer's local environment (viewport)
// rather than being a fragile, fixed-width layout. A fixed cartesian coordinate system would be far too fragile.
const responsive = {
  superLargeDesktop: { breakpoint: { max: 4000, min: 3000 }, items: 5, slidesToSlide: 3 },
  desktop: { breakpoint: { max: 3000, min: 1024 }, items: 4, slidesToSlide: 2 },
  tablet: { breakpoint: { max: 1024, min: 640 }, items: 2, slidesToSlide: 1 },
  mobile: { breakpoint: { max: 640, min: 0 }, items: 1, slidesToSlide: 1 },
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