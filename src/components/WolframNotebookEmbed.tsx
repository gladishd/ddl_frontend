"use client";

import React from 'react';
import WolframSidebar from './WolframSidebar';
import { FaExternalLinkAlt } from 'react-icons/fa';

// This component presents the four core computational models that form the foundation of our argument against bandwidth-multiplexing.
// Each model is a "proof by code," a precise information-theoretic emulator designed to reveal the consequences of different networking assumptions.
// They are presented here as direct links into the Wolfram Cloud, where the live models can be interrogated.

const notebooks = [
  {
    // This agentic simulation models the original half-duplex, shared Metcalfe ether.
    // It's a computational exploration of his assertion that "at some point the Ether will be so busy that additional stations will just divide more finely the already inadequate bandwidth."
    // We use this to demonstrate how contending for a shared medium fundamentally limits transactional capacity.
    title: "Model 1: Half-Duplex Contention",
    description: "An agentic simulation of the original 1976 Metcalfe-Boggs protocol. This model visualizes the transmission and contention intervals on a shared half-duplex medium, demonstrating how statistical arbitration impacts throughput.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb",
    date: "June 11, 2025"
  },
  {
    // This model extends the analysis to modern full-duplex links, showing that even without physical collisions,
    // the multiplexing of bandwidth creates "chaotic contention" that decimates the throughput of reliable protocols like TCP.
    title: "Model 2: Full-Duplex Degradation",
    description: "A model of modern full-duplex links where multiple TCP flows compete. It shows how bandwidth-multiplexing still leads to severe latency degradation and reduced throughput under contention and packet loss.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas2.nb",
    date: "June 12, 2025"
  },
  {
    // Here, we demolish the foundational assumption that a round-trip interaction must incur a full RTT penalty.
    // This model illustrates the concept of a data packet being "longer than the wire," where a pipelined acknowledgement
    // can be received before the sender has even finished transmitting, thus achieving nearly 100% link utilization.
    title: "Model 3: The Circulating Snake",
    description: "This model demolishes the 'stop-and-wait' assumption. It demonstrates a 'snake' of bits longer than the physical link, where pipelined acknowledgements eliminate the round-trip penalty and achieve maximum transactional throughput.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas3.nb",
    date: "June 14, 2025"
  },
  {
    // This is the Daedaelus way. Instead of multiplexing bandwidth, the GVM interleaves atomic request/reply transactions.
    // This model provides "definitive, visual proof" that this method is "fundamentally more efficient" for concurrent operations.
    title: "Model 4: Interaction Multiplexing",
    description: "The superior model. We show that multiplexing discrete, reliable handshake interactions, rather than contending for bandwidth, maximizes total system throughput and offers deterministic latency, walking right over packet loss.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas4.nb",
    date: "June 17, 2025"
  }
];

const WolframNotebookEmbed: React.FC = () => {
  return (
    <section id="live-models" className="bg-gray-50 p-6 md:p-12">
      <div className="container mx-auto">
        <header className="mb-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold">Live Computational Models</h2>
          <p className="text-muted-foreground mt-2 max-w-3xl mx-auto">
            These four Wolfram Cloud notebooks form the core of our argument. They are not static papers, but live, computational essays designed to provide definitive proof of our thesis.
          </p>
        </header>
        <div className="wolfram-layout-container">
          <WolframSidebar />
          <div className="flex flex-col space-y-4">
            {notebooks.map((notebook) => (
              <a
                key={notebook.url}
                href={notebook.url}
                target="_blank"
                rel="noopener noreferrer"
                className="notebook-link-card"
              >
                  <div className="flex-grow">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="notebook-title">{notebook.title}</h4>
                      <span className="notebook-date">{notebook.date}</span>
                    </div>
                    <p className="notebook-description">{notebook.description}</p>
                  </div>
                  <FaExternalLinkAlt className="notebook-link-icon" />
                </a>
              ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default WolframNotebookEmbed;