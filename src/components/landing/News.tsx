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
    date: 'October 7, 2025',
    title: 'TACL Article: A Minimalist Approach to Meaning',
    link: 'https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00612/118718',
    // This paper's focus on minimalism aligns with our principle of finding the simplest mathematical representation that achieves the goal, avoiding the 'Christmas tree effect' of adding unnecessary complexity.
    description: 'A publication from Transactions of the Association for Computational Linguistics, exploring minimalist models of meaning that resonate with our pursuit of simple, formally verifiable protocols.',
  },
  {
    date: 'October 7, 2025',
    title: 'Video: The Firing Squad Sync Problem',
    link: 'https://youtu.be/8JuWdXrCmWg',
    // The Firing Squad Problem is central to our work on achieving network-wide consensus without a central coordinator, a key element for building robust, self-organizing distributed systems.
    description: 'A visual explanation of the Firing Squad Synchronization Problem, a classic distributed computing challenge that informs our approach to achieving simultaneous action across a network.',
  },
  {
    date: 'October 7, 2025',
    title: 'ACM Paper: The Power of Two Choices in Hashing',
    link: 'https://dl.acm.org/doi/10.1145/3717823.3718225',
    // This principle of simple, local choices leading to global emergent properties is fundamental to our GVM, where neighbor-to-neighbor interactions build a resilient, self-healing fabric.
    description: 'An ACM paper discussing the "Power of Two Choices" in randomized hashing, a concept that parallels our philosophy of achieving system-wide balance through simple, local, and robust algorithms.',
  },
  {
    date: 'October 7, 2025',
    title: 'ChatGPT: Reversible Computing and the GVM',
    link: 'https://chatgpt.com/share/68e44ed0-9304-8011-af3b-d4f7561df5d0',
    // Our system architecture is built on the foundation of reversibility, allowing us to undo operations and recover from errors without the 'irreversible smash and restart' common in traditional networks.
    description: 'A conversation exploring the deep connections between reversible computing, the Spekkens Toy Model, and the architectural principles of our Graph Virtual Machine (GVM).',
  },
  {
    date: 'October 7, 2025',
    title: 'OSF Preprints: Entanglement in Quantum Cellular Automata',
    link: 'https://files.de-1.osf.io/v1/resources/a8xrq/providers/osfstorage/65fc88d2fd9160014d468c0e?format=pdf&action=download&direct&version=4',
    // We draw inspiration from the quantum information community; understanding entanglement in cellular automata provides a model for the non-local correlations we establish in our distributed systems.
    description: 'A preprint discussing entanglement in Quantum Cellular Automata, offering insights into the non-local effects and information propagation that parallel our approach to distributed state.',
  },
  {
    date: 'August 26, 2025',
    title: 'Open Atomic Ethernet Simulation Tools',
    link: 'https://grok.com/share/c2hhcmQtMg%3D%3D_c0088424-b146-48f8-bb75-018c4669dd17',
    // This conversation explores the development of agent-based models for Open Atomic Ethernet,
    // moving beyond statistical approximations to create precise, computationally verifiable simulations of network behavior.
    description: 'A Grok conversation on creating agent-based simulations to model the deterministic behavior of Open Atomic Ethernet.',
  },
  {
    date: 'August 26, 2025',
    title: 'Mutual Information in Networking Protocols',
    link: 'https://grok.com/share/c2hhcmQtMg%3D%3D_ccb76308-8e33-409b-9aac-e5f27e700496',
    // This discussion reframes networking through the lens of mutual information, aligning with our view that communication
    // is not merely data transfer but the establishment of a shared, verifiable state between two observers.
    description: 'Exploring the role of mutual information as a foundational concept for designing reliable, state-aware networking protocols.',
  },
  {
    date: 'August 26, 2025',
    title: 'Networking Latency Solutions and API Design',
    link: 'https://grok.com/share/c2hhcmQtMg%3D%3D_028eaa83-2858-4201-850b-cd620e133640',
    // This conversation analyzes latency in modern networks, reinforcing our argument that the industry's focus on raw bandwidth
    // overlooks the critical need for predictable, low-latency interactions for distributed applications.
    description: 'A discussion on API design and architectural solutions to address the fundamental latency challenges in distributed systems.',
  },
  {
    date: 'August 26, 2025',
    title: 'Monolithic 3D: Stacking Without Chiplets',
    link: 'https://www.youtube.com/watch?v=PVyz-r9wlQo',
    // This presentation on Monolithic 3D integration aligns with our goal of creating dense, highly interconnected computational fabrics,
    // reducing physical distance to approach the ideal of a zero-latency N2N Lattice.
    description: 'A presentation on the future of semiconductor manufacturing, exploring techniques for building vertically integrated circuits.',
  },
  {
    date: 'August 26, 2025',
    title: '[WSS22] Quantum Ethernet - Wolfram Community',
    link: 'https://community.wolfram.com/groups/-/m/t/2575423',
    // This discussion on Petri-Spekkens nets directly inspires our Token Dynamics model, using concepts from Quantum Information Theory
    // to create verifiable, reversible transactions at the link layer.
    description: 'A technical discussion on modeling "Quantum Ethernet" using Petri-Spekkens nets and the Spekkens Toy Model.',
  },
  {
    date: 'August 26, 2025',
    title: 'Open Atomic Ethernet Protocol Theory',
    link: 'https://claude.ai/share/bb40fbe9-e328-4753-9fe2-70d46ef3e808',
    // This conversation explores the Slowdown Theorem and its connection to our protocol, reinforcing the idea that
    // computational irreducibility necessitates a shift away from predictive, FITO-based systems toward observable, reversible ones.
    description: 'A deep dive into the theoretical underpinnings of Open Atomic Ethernet, connecting it to the Slowdown Theorem and time symmetry.',
  },
  {
    date: 'August 26, 2025',
    title: 'DæDælus Home',
    link: 'https://staging.daedaelus.com/home',
    // The central hub for our work in architecting the future with enduring excellence, providing access to our research, tools, and vision.
    description: 'The homepage for the Dædælus project, architecting the future of distributed systems.',
  },
  {
    date: 'August 18, 2025',
    title: 'Hough Transform (Wikipedia)',
    link: 'https://en.wikipedia.org/wiki/Hough_transform',
    description: 'Overview of the Hough transform, a classic feature-detection method in computer vision.',
  },
  {
    date: 'August 18, 2025',
    title: 'Centralized vs. Decentralized vs. Distributed Networks',
    link: 'https://www.liveaction.com/resources/blog-post/centralized-vs-decentralized-vs-distributed-networks-the-history-future/#:~:text=decentralized%20network%20in%20a%20proposal,for%20the%20US%20AirForce)',
    description: 'Blog explainer contrasting network topologies and their historical context.',
  },
  {
    date: 'August 18, 2025',
    title: 'RAND RM-3420: Distributed Communications Networks (Baran)',
    link: 'https://www.rand.org/pubs/research_memoranda/RM3420.html#:~:text=Figure%201,Distributed%20Networks)',
    description: 'Paul Baran’s seminal RAND memo introducing resilient distributed network architectures.',
  },
  {
    date: 'August 18, 2025',
    title: 'Expression Evaluation & Fundamental Physics',
    link: 'https://writings.stephenwolfram.com/2023/09/expression-evaluation-and-fundamental-physics/',
    description: 'Stephen Wolfram on evaluation order and its implications for physics models.',
  },
  {
    date: 'August 18, 2025',
    title: 'Dædælus Team',
    link: 'https://daedaelus.com/team/',
    description: 'People behind the Dædælus project.',
  },
  {
    date: 'August 18, 2025',
    title: 'FEM 2D Mesh with Inclusion (Mathematica SE)',
    link: 'https://mathematica.stackexchange.com/questions/221660/fem-2d-mesh-with-inclusion',
    description: 'Techniques for building FEM meshes with embedded inclusions in Wolfram Language.',
  },
  {
    date: 'August 18, 2025',
    title: 'Game of Life (MathWorld)',
    link: 'https://mathworld.wolfram.com/GameofLife.html',
    description: 'Reference entry on Conway’s Game of Life and cellular automata properties.',
  },
  {
    date: 'August 18, 2025',
    title: 'FSP Model Verification (GitHub)',
    link: 'https://github.com/dj-on-github/fspcode/tree/refactor/fsp-model-verification',
    description: 'Repository branch focusing on model verification for FSP specifications.',
  },
  {
    date: 'August 18, 2025',
    title: 'ScienceDirect Article (TCS)',
    link: 'https://www.sciencedirect.com/science/article/pii/S0304397500001602',
    description: 'Theoretical Computer Science paper (publisher landing page).',
  },
  {
    date: 'August 18, 2025',
    title: 'Attention Is All You Need (arXiv)',
    link: 'https://arxiv.org/pdf/1706.05893',
    description: 'The original Transformer paper (PDF).',
  },
  {
    date: 'August 18, 2025',
    title: 'YouTube: woLp0RXdR1g',
    link: 'https://www.youtube.com/watch?v=woLp0RXdR1g',
    description: "Agent-Based Modeling in Wolfram Language and Mathematica",
  },
  {
    date: 'August 18, 2025',
    title: 'ACM DL Paper (PDF)',
    link: 'https://dl.acm.org/doi/pdf/10.1145/1402958.1402967',
    description: 'ACM Digital Library—paper PDF.',
  },
  {
    date: 'August 18, 2025',
    title: 'Dædælus Talks & Presentations',
    link: 'https://daedaelus.com/talks-presentations/',
    description: 'Collected talks and slide decks for the Dædælus project.',
  },
  {
    date: 'August 18, 2025',
    title: 'Time, Clocks & Reordering of Events (Speaker Deck)',
    link: 'https://speakerdeck.com/pborrill/time-clocks-and-the-reordering-of-events-pwl-san-francisco-14-jul-2016',
    description: 'Slide deck on partial order of events in distributed systems.',
  },
  {
    date: 'August 18, 2025',
    title: 'Medmastery—Course Library',
    link: 'https://www.medmastery.com/course-library?speciality=ultrasound&utm_source=google&utm_medium=cpc&utm_campaign=&gad_campaignid=22306462523&gclid=CjwKCAjwtfvEBhAmEiwA-DsKjoR78Ta4nIHaqLrjhtqom3wnkOrpC4dDN57LaFIPGunsatpF1B3_fhoCbrEQAvD_BwE',
    description: 'Education resource—medical ultrasound and more.',
  },
  {
    date: 'August 18, 2025',
    title: 'Time, Clocks & Reordering—Slide 4',
    link: 'https://speakerdeck.com/pborrill/time-clocks-and-the-reordering-of-events-pwl-san-francisco-14-jul-2016?slide=4',
    description: 'Direct link to slide 4 from the Speaker Deck presentation.',
  },
  {
    date: 'August 18, 2025',
    title: 'TSMC Museum of Innovation (ZH)',
    link: 'https://www.tsmcmoi.com/ch/',
    description: 'TSMC Museum of Innovation—Chinese site.',
  },
  {
    date: 'August 18, 2025',
    title: 'Stream Reservation Protocol (Wikipedia)',
    link: 'https://en.wikipedia.org/wiki/Stream_Reservation_Protocol',
    description: '802.1Qat SRP background for time-sensitive networking.',
  },
  {
    date: 'August 18, 2025',
    title: 'SEC Release No. 34-69655 (2013)',
    link: 'https://www.sec.gov/files/litigation/admin/2013/34-69655.pdf',
    description: 'SEC administrative proceeding document (PDF).',
  },
  {
    date: 'August 18, 2025',
    title: 'Deutsche Bank €35B Payments Error (Finadium)',
    link: 'https://finadium.com/bloomberg-deutsche-bank-makes-35bn-derivatives-payments-mistake-to-eurex-clearing/?utm_source=chatgpt.com',
    description: 'Article on a major erroneous derivatives payment to Eurex Clearing.',
  },
  {
    date: 'August 18, 2025',
    title: 'LaurieWired (YouTube)',
    link: 'https://www.youtube.com/@lauriewired/videos',
    description: 'Laurie Kirk’s channel—videos on networking, TSN, and timing.',
  },
  {
    date: 'August 18, 2025',
    title: 'Laurie Kirk (LinkedIn)',
    link: 'https://www.linkedin.com/in/laurie-kirk/',
    description: 'Professional profile for Laurie Kirk.',
  },
  {
    date: 'August 18, 2025',
    title: 'LaurieWired Linktree',
    link: 'https://linktr.ee/lauriewired',
    description: 'Consolidated links for LaurieWired content.',
  },
  {
    date: 'August 18, 2025',
    title: 'YouTube: u0d7DB3N1Yk',
    link: 'https://www.youtube.com/watch?v=u0d7DB3N1Yk',
    description: 'The Real Reason Elon Musk Killed The DOJO Supercomputer',
  },
  {
    date: 'August 18, 2025',
    title: 'Arista.pdf (iCloud link)',
    link: 'https://cvws.icloud-content.com/B/AcfwXuwn0NAzw7z2o_AvC1uTqxMRAS_h5iRBrRBTEkngfsiKCljNSHZX/Arista.pdf?o=AoFYfCy3Q6N8fTNZ9Rah8ietQdEDgOlrsnysWZ018-6x&v=1&x=3&a=CAogj4njoM9Rpdru6qk7fMseXu7q-3wN9Si4LX4fDPzkRZUSaxCllq7pijMYpfOJ64ozIgEAUgSTqxMRWgTNSHZXaiVsRRbyWhQZEASqU3JyUyonDHEa-7afZNHk_Xqgecvq4uf4OBAdciU4V74ny7fLHouBzX_6bi9Pxoi1aF9_Y-_9Kv69XCEY8UfQndSS&e=1755255568&fl=&r=11c6d4cc-b90b-4f38-88ef-4079c3c9850a-1&k=gnNPuxkWQUr10PSBtk4qDw&ckc=com.apple.clouddocs&ckz=com.apple.CloudDocs&p=52&s=HY0lORAnViGvhRY1ypPZbjXdowk&cd=i',
    description: 'Shared PDF—Arista-related material.',
  },
  {
    date: 'August 18, 2025',
    title: 'YouTube: bXPz_pR8Or4 (at 7:12)',
    link: 'https://www.youtube.com/watch?v=bXPz_pR8Or4&t=432s',
    description: "Time-coded link to Paul Borrill: Lamport's Unfinished Revolution -- Papers We Love Too / San Francisco.",
  },
  {
    date: 'August 18, 2025',
    title: 'Time, Clocks, and the Ordering of Events (Lamport, PDF)',
    link: 'https://lamport.azurewebsites.net/pubs/time-clocks.pdf',
    description: 'Lamport’s classic paper on logical clocks and partial ordering in distributed systems.',
  },
  {
    date: 'August 18, 2025',
    title: 'YouTube: bXPz_pR8Or4',
    link: 'https://www.youtube.com/watch?v=bXPz_pR8Or4',
    description: "Paul Borrill: Lamport's Unfinished Revolution -- Papers We Love Too / San Francisco (full link).",
  },
  // Insert these new items at the beginning of the 'newsItems' array.
  {
    date: 'July 23, 2025',
    title: 'Paxos Consensus Protocol',
    link: 'https://en.wikipedia.org/wiki/Paxos_(computer_science)',
    description: 'An overview of the Paxos family of protocols for achieving consensus in unreliable distributed systems, a foundational concept for building fault-tolerant state machines.',
  },
  {
    date: 'July 23, 2025',
    title: 'Time Appliances Project (TAP) on GitHub',
    link: 'https://github.com/Time-Appliances-Project',
    description: 'The official GitHub organization for the Time Appliances Project (TAP), providing open-source tools and standards for high-precision time synchronization.',
  },
  {
    date: 'July 23, 2025',
    title: 'IEEE Milestone Proposal: Manchester Code',
    link: 'https://ieeemilestones.ethw.org/Milestone-Proposal:Manchester_Code',
    description: 'The proposal to recognize Manchester Code, a foundational line code for self-clocking digital data used in early computing and Ethernet, as an IEEE Milestone.',
  },
  {
    date: 'July 23, 2025',
    title: 'Open Atomic Ethernet (OAE) Wiki',
    link: 'https://www.opencompute.org/w/index.php?title=Open_Atomic_Ethernet#Ethernet_History_and_Interesting_Links',
    description: 'The official Open Compute Project wiki for the Open Atomic Ethernet (OAE) initiative, detailing its vision for a formally verifiable, transactional Ethernet.',
  },
  {
    date: 'July 23, 2025',
    title: 'Claude Chat: LaTeX Compilation Debugging',
    link: 'https://claude.ai/share/742b1496-fde3-47b4-8de5-965bd60b7746',
    description: 'A shared conversation detailing the debugging process for a complex LaTeX document, highlighting common issues with graphics paths and auxiliary file corruption.',
  },
  {
    date: 'July 23, 2025',
    title: 'The Twelve-Factor App Methodology',
    link: 'https://12factor.net/',
    description: 'A methodology for building modern, scalable, and maintainable software-as-a-service applications, focusing on declarative configurations and clean architecture.',
  },
  {
    date: 'July 23, 2025',
    title: 'OpenTofu: Open-Source Infrastructure as Code',
    link: 'https://opentofu.org/',
    description: 'The official site for OpenTofu, a community-driven, open-source fork of Terraform for building, changing, and versioning infrastructure safely and efficiently.',
  },
  {
    date: 'July 23, 2025',
    title: 'arXiv: A Class of Models with the Potential to Represent Fundamental Physics',
    link: 'https://arxiv.org/abs/2004.08210',
    description: "Stephen Wolfram's paper introducing a class of simple models that generate complex behavior, exploring their potential as a foundation for a new theory of physics.",
  },
  {
    date: 'July 23, 2025',
    title: 'arXiv: Step-by-Step Diffusion: An Elementary Tutorial',
    link: 'https://arxiv.org/abs/2406.08929',
    description: 'An accessible tutorial on diffusion models and flow matching for machine learning, simplifying the mathematical details for a technical audience.',
  },
  {
    date: 'July 23, 2025',
    title: 'OAE Discussion: Clos vs. Directly Connected Networks',
    link: 'https://ocp-all.groups.io/g/ocp-oae/topic/114067018#msg636',
    description: 'A discussion thread in the Open Atomic Ethernet group on the trade-offs between Clos and direct-connect mesh networks, focusing on resilience and latency.',
  },
  {
    date: 'July 23, 2025',
    title: 'YC Lecture: How to Raise Money',
    link: 'https://genius.com/Marc-andreessen-lecture-9-how-to-raise-money-annotated',
    description: 'An annotated transcript of Marc Andreessen, Ron Conway, and Parker Conrad\'s lecture on fundraising from the Y Combinator "How to Start a Startup" series.',
  },
  {
    date: 'July 23, 2025',
    title: 'Startup Archive on X: Marc Andreessen on VC',
    link: 'https://x.com/StartupArchive_/status/1944064804735385830',
    description: "A post summarizing Marc Andreessen's insights on the outlier-driven nature of venture capital and what VCs look for in startups.",
  },
  {
    date: 'July 23, 2025',
    title: 'Grok Chat: Clos vs. Mesh Network Simulation',
    link: 'https://grok.com/share/c2hhcmQtMg%3D%3D_bab388ed-4af4-417f-a942-01ac827ce54e',
    description: 'A shared conversation detailing the creation of a Mathematica simulation to compare the resilience and latency of Clos vs. direct-connect network topologies.',
  },
  {
    date: 'July 23, 2025',
    title: 'Claude Chat: Slowdown Theorem & Atomic Ethernet',
    link: 'https://claude.ai/share/bb40fbe9-e328-4753-9fe2-70d46ef3e808',
    description: 'A deep analysis of the "Slowdown Theorem on Links," connecting computational irreducibility and time symmetry to the theory behind Open Atomic Ethernet.',
  },
  {
    date: 'July 23, 2025',
    title: 'Wolfram Summer School: Physics Track Keynote',
    link: 'https://www.youtube.com/watch?v=XAg69DoChbw',
    description: "Stephen Wolfram's opening keynote for the Wolfram Summer School 2025, discussing the current state of the Wolfram Physics Project.",
  },
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
    title: 'Project Dædælus featured in ItsAboutTime.Club',
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
    title: 'Dædælus: A New Approach to Distributed Systems',
    link: 'https://daedaelus.com/',
    description: 'The official website of the Dædælus project, which is developing a new approach to building resilient and efficient distributed systems.',
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
    title: 'About Dædælus',
    link: 'https://daedaelus.com/about/',
    description: 'The about page for the Dædælus project, providing more information about its mission and team.',
  }
];

// This configuration defines the responsive behavior of the carousel.
// It is an adaptive ruleset, ensuring the view conforms to the observer's local environment (viewport)
// rather than being a fragile, fixed-width layout. A fixed cartesian coordinate system would be far too fragile.
const responsive = {
  superLargeDesktop: { breakpoint: { max: 4000, min: 3000 }, items: 5, slidesToSlide: 4 },
  desktop: { breakpoint: { max: 3000, min: 1024 }, items: 4, slidesToSlide: 3 },
  tablet: { breakpoint: { max: 1024, min: 640 }, items: 2, slidesToSlide: 2 },
  mobile: { breakpoint: { max: 640, min: 0 }, items: 1, slidesToSlide: 2 },
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