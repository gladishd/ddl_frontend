/* eslint-disable @next/next/no-img-element */
import React from 'react';

// This component lays out the core strategy, transforming abstract goals into a concrete roadmap.
// It reflects the Daedaelus principle of moving from formal specification (Mathematica) to high-fidelity implementation (Rust Emulator),
// all while building the necessary control plane (GVM) and tooling for visualization and management.
const initiatives = [
  {
    title: "1. Agent-Based Packet Simulation: From Mathematica to Rust",
    description: "Our primary application is a high-fidelity, agent-based simulation to model Ethernet's fundamental behaviors under contention. The goal is to computationally demonstrate the pathological behaviors in modern networking, directly challenging the assumptions underpinning specifications like the Ultra Ethernet Consortium's (UEC).",
    points: [
      {
        title: "Mathematica as the Specification Language",
        // We leverage Wolfram Language for the initial model, simulating the 1976 Metcalfe-Boggs half-duplex specification.
        // This provides a formal, verifiable foundation before committing to lower-level code.
        text: "We leverage Wolfram Language for the initial model, simulating the 1976 Metcalfe-Boggs half-duplex specification. This includes explicit modeling of transmission collisions, contention intervals, binary exponential backoff, and carrier sense (CSMA/CD)."
      },
      {
        title: "Exposing Inherent Flaws",
        // By layering a TCP-like protocol, we highlight the systemic inefficiencies of bandwidth multiplexing.
        // This computationally demonstrates the emergence of degraded states where network 'optimizations' actively harm application performance.
        text: "By layering a TCP-like protocol, we highlight the systemic inefficiencies of bandwidth multiplexing. This computationally demonstrates the emergence of what we term Promiscuous Bandwidth, Imposition Mode, and TAR Limpware—degraded states where network 'optimizations' actively harm application performance."
      },
      {
        title: "High-Fidelity Rust Emulator",
        // To create an 'Ethernet w/o Mac Minis,' we are developing a packet network emulator in Rust.
        // This models our N2N architecture of cells communicating over links, providing a framework validated against our formal specifications.
        text: 'To create an "Ethernet w/o Mac Minis," we are developing a packet network emulator in Rust, our "OAE Cell Agent Simulator." This models our architecture of cells communicating over links (as Unix pipes), providing a framework to explore concurrency and low-level protocol mechanics in a way that is validated against our formal Mathematica specifications.'
      }
    ],
    // Corrected image path: Assumes images are in the /public folder.
    image: "/simulation.png"
  },
  {
    title: "2. Tree Algorithms and Dashboard Development",
    description: "The success of our architecture relies on a sophisticated control plane and clear visualization. We are strategically building our team's capabilities to deliver on the promise of the Graph Virtual Machine (GVM).",
    points: [
      {
        title: "Team Roles and Focus",
        text: "Sahas Munamala will advance our core tree algorithms, leveraging the Wolfram Summer School. We will onboard Sumon U. as a full-stack developer to build a network dashboard, likely in Go, to visualize these complex interactions."
      },
      {
        title: "Architectural Foundation",
        // This work directly implements the logic of the GVM. Our architecture uses recursively stacked trees
        // for hardware-enforced confinement and resource provisioning within a 9-cell 'hypercell' tile.
        text: "This work directly implements the logic of the GVM. Our architecture uses recursively stacked trees for hardware-enforced confinement and resource provisioning. The algorithms developed will form the basis of the GVM’s ability to manage consensus, elasticity, and load balancing within a 9-cell \"hypercell\" tile."
      },
      {
        title: "Tooling",
        text: 'Concurrency for these processes will be prototyped and explored using Python, directly feeding into the "OAE Python Emulator" project listed in our OCP repository.'
      }
    ],
    // Corrected image path: Assumes images are in the /public folder.
    image: "/gvm.jpeg"
  },
  {
    title: "3. Document Repository and Physical Demonstration",
    description: "To support our technical development and ensure our ideas are clearly communicated, we are establishing a robust documentation workflow and building towards a physical, real-world demonstration.",
    points: [
      {
        title: "A Hybrid Documentation Strategy",
        text: 'Managed by Gia Singh, we will use a "Markdown-first, LaTeX-enhanced" approach. Markdown will be used for accessible, collaborative drafting, while LaTeX, via Pandoc, will provide high-fidelity typesetting for formal documents like patents and scientific papers, all version-controlled in our "OAE Latex Github" repository.'
      },
      {
        title: "Simulation and Physical Demo",
        // Ultimately, to prove the viability of our protocol—especially when a data 'snake' is longer than the physical cable—
        // we will build a physical demonstration using high-speed Thunderbolt interconnects.
        text: 'In parallel, our Python simulation will be enhanced. Ultimately, to prove the viability of our protocol—especially the benefits realized when a data "snake" is longer than the physical cable—we will build a physical demonstration using high-speed Thunderbolt interconnects, providing tangible proof for our simulated and specified claims.'
      }
    ],
    // Corrected image path: Assumes images are in the /public folder.
    image: "/physical-demo.jpeg"
  },
];


const StrategicInitiatives = () => {
  return (
    <section className="initiatives-section">
      <div className="container mx-auto">
        <h2 className="initiatives-header">Our Strategic Initiatives</h2>
        <p className="text-lg text-justify text-[rgb(46,45,41)] max-w-3xl mx-auto mb-16">
          We are executing a multi-pronged strategy combining formal simulation, team development, and robust tooling to build the next generation of Ethernet.
        </p>
        {/*
          Judicious Modification: Added 'justify-center' to the grid container.
          This ensures that on larger screens where there might be extra space,
          the grid items remain centered rather than spreading too far apart.
        */}
        <div className="initiatives-container justify-center">
          {initiatives.map((initiative, index) => (
            <div key={index} className="initiative-card">
              <div className="initiative-card-image-wrapper">
                <img src={initiative.image} alt={initiative.title} className="initiative-card-image" />
              </div>
              <div className="initiative-card-content">
                <h3 className="text-2xl font-bold mb-4">{initiative.title}</h3>
                <p className="text-gray-600 mb-6">{initiative.description}</p>
                <div className="initiative-card-points-wrapper">
                  <ul className="initiative-card-points">
                    {initiative.points.map((point, pIndex) => (
                      <li key={pIndex} className="initiative-card-point-item">
                        <strong className="block font-semibold text-gray-800">{point.title}:</strong>
                        <p className="text-[rgb(46,45,41)] leading-relaxed">{point.text}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default StrategicInitiatives;