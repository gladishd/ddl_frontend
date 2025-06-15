/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useEffect, useState } from "react";
import {
    FaCogs, FaShareSquare, FaPaintBrush, FaChartBar,
    FaPlayCircle, FaGraduationCap, FaBuilding,
} from "react-icons/fa";
import Link from "next/link";
import EthernetModel from "./EthernetModel"; // Import the new model component

/* LOAD hero background … unchanged */
const HERO_BG =
    "url(/Dædælus.png) repeat 0 0 / 220px 160px";

const overlay: React.CSSProperties = {
    position: "absolute",
    inset: 0,
    backgroundColor: "rgba(0,38,38,0.6)",
    zIndex: 1,
};

export default function LandingPage() {
    /* tiny client-only wrapper for SSR icons */
    const [mounted, setMounted] = useState(false);
    useEffect(() => setMounted(true), []);
    const C = ({ children }: { children: React.ReactNode }) =>
        mounted ? <>{children}</> : null;

    return (
        <>
            {/* hero */}
            {/*
                This hero section establishes our core thesis. We are not merely improving existing network paradigms;
                we are architecting a new future by challenging the industry's most fundamental assumptions.
                Our focus shifts from the raw measure of bandwidth to the transactional capacity of a link—the round-trip interactions.
                This is rooted in our philosophy of using 'Time-reversible' constructors that "no longer rely on the irreversible smash and restart of Shannon information to recover from failures."
            */}
            <section
                suppressHydrationWarning
                className="relative text-center py-20 px-4 overflow-hidden"
                style={{ background: HERO_BG, color: "rgb(130,0,0)", textShadow: "0 0 1px black" }}
            >
                <div style={overlay} />
                <div className="relative z-10 max-w-4xl mx-auto">
                    <h1 className="text-5xl font-bold mb-4 font-inika">
                        Beyond Bandwidth: Architecting Transactional Causality
                    </h1>
                    <p className="text-xl mb-8 font-raleway">
                        We challenge the industry's foundational assumptions by multiplexing the transactional capacity of a link, not its bandwidth. Our time-reversible constructors forge a new paradigm of distributed reliability.
                    </p>
                    <Link
                        href="/Metcalfe+Boggs.pdf"
                        target="_blank"
                        className="inline-block px-8 py-3 bg-white text-primary font-bold rounded-md hover:bg-gray-200 transition-transform hover:scale-105"
                        style={{ background: "rgb(184,58,75)" }}
                    >
                        Revisit the Foundation: Metcalfe & Boggs 1976
                    </Link>
                </div>
            </section>

            {/*
                This section outlines the four key modeling arguments we are making to challenge the industry's core assumptions about network performance.
                Each model is a step in a larger narrative, starting from the original Metcalfe ether and culminating in a new paradigm of Interaction Multiplexing.
                This directly reflects our strategy to "organize the story we want to portray with this computation model."
            */}
            <section className="py-20 px-4">
                <h2 className="text-4xl font-bold text-center mb-12">
                    The Bandwidth Argument We Want to Make
                </h2>
                <div className="container mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-10">
                    {/*
                        Point 1 from the email: Model the original shared Metcalfe ether.
                        The goal is to show the consequences of the root assumption: dividing bandwidth as a "fair arbitration of the contended resource."
                        We are building an "agentic simulation/transmission contention model" to demonstrate this computationally, not statistically.
                    */}
                    <FeatureCard icon={<C><FaCogs /></C>} title="1. Half-Duplex Contention" description="An agentic simulation of the shared Metcalfe ether. We computationally model transmission and contention intervals to show how multiplexing bandwidth fundamentally limits the transactional capacity of the link." />
                    {/*
                        Point 2: Show how bandwidth multiplexing also fails on modern links.
                        This model demonstrates how "multiplexing bandwidth is killing the intimacy of the interactions, even on full duplex links," which is crucial in our argument against bandwidth multiplexing.
                    */}
                    <FeatureCard icon={<C><FaShareSquare /></C>} title="2. Full-Duplex Degradation" description="A model of modern, full-duplex links demonstrating how bandwidth-multiplexing decimates TCP throughput under loss, leading to severe round-trip latency degradation and proving the model is broken." />
                    {/*
                        Point 3: Demolish the stop-and-wait assumption with the "circulating snakes idea."
                        With a "self-contained snake of bits, that's longer than the wire itself, the acknowledgement is being received while the sender is still transmitting."  This is how we prove reliability is nearly free.
                    */}
                    <FeatureCard icon={<C><FaPaintBrush /></C>} title="3. The Circulating Snake" description="We demolish the assumption that stop-and-wait throttles bandwidth. This model shows a 'snake' of bits longer than the wire, where acknowledgements arrive before transmission ends, eliminating the round-trip penalty." />
                    {/*
                        Point 4: The superior model of multiplexing interactions.
                        This is the final step, showing that a round-robin of handshake interactions "does better at maximizing total throughput under contention, and with much more deterministic latency."
                    */}
                    <FeatureCard icon={<C><FaChartBar /></C>} title="4. Interaction Multiplexing" description="The superior model. We demonstrate that multiplexing handshake interactions, not time-sharing the link, maximizes total throughput and provides deterministic latency that walks right over packet loss." />
                </div>
            </section>

            {/* ============================================= */}
            {/* === NEW ETHERNET SIMULATION MODEL SECTION === */}
            {/* ============================================= */}
            <EthernetModel />

            {/*
                This section details our primary application areas and strategic initiatives.
                It replaces the more general use-cases with a concrete roadmap, outlining our work in simulation,
                team development, and infrastructure. This approach provides a clearer picture of how we are actively building
                the future of Ethernet, from formal specification to physical demonstration.
            */}
            <section className="py-20 px-4 bg-gray-100">
                <h2 className="text-4xl font-bold text-center mb-4">Our Strategic Initiatives</h2>
                <p className="text-lg text-center text-gray-600 max-w-3xl mx-auto mb-12">
                    We are executing a multi-pronged strategy combining formal simulation, team development, and robust tooling to build the next generation of Ethernet.
                </p>
                <div className="container mx-auto max-w-5xl space-y-8">

                    {/* Card 1: Agent-Based Simulation */}
                    <div className="bg-white p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow text-left">
                        <h3 className="text-2xl font-bold mb-4">1. Agent-Based Packet Simulation: From Mathematica to Rust</h3>
                        <p className="mb-4">
                            Our primary application is a high-fidelity, agent-based simulation to model Ethernet's fundamental behaviors under contention. The goal is to computationally demonstrate the pathological behaviors in modern networking, directly challenging the assumptions underpinning specifications like the Ultra Ethernet Consortium's (UEC).
                        </p>
                        <ul className="list-disc list-inside space-y-3">
                            <li>
                                <strong>Mathematica as the Specification Language:</strong> We leverage Wolfram Language for the initial model, simulating the 1976 Metcalfe-Boggs half-duplex specification. This includes explicit modeling of transmission collisions, contention intervals, binary exponential backoff, and carrier sense (CSMA/CD).
                            </li>
                            <li>
                                <strong>Exposing Inherent Flaws:</strong> By layering a TCP-like protocol, we highlight the systemic inefficiencies of bandwidth multiplexing. This computationally demonstrates the emergence of what we term <strong>Promiscuous Bandwidth</strong>, <strong>Imposition Mode</strong>, and <strong>TAR Limpware</strong>—degraded states where network "optimizations" actively harm application performance.
                            </li>
                            <li>
                                <strong>High-Fidelity Rust Emulator:</strong> To create an "Ethernet w/o Mac Minis," we are developing a packet network emulator in Rust, our "OAE Cell Agent Simulator." This models our architecture of cells communicating over links (as Unix pipes), providing a framework to explore concurrency and low-level protocol mechanics in a way that is validated against our formal Mathematica specifications.
                            </li>
                        </ul>
                    </div>

                    {/* Card 2: Team Development */}
                    <div className="bg-white p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow text-left">
                        <h3 className="text-2xl font-bold mb-4">2. Tree Algorithms and Dashboard Development</h3>
                        <p className="mb-4">
                            The success of our architecture relies on a sophisticated control plane and clear visualization. We are strategically building our team's capabilities to deliver on the promise of the Graph Virtual Machine (GVM).
                        </p>
                        <ul className="list-disc list-inside space-y-3">
                            <li>
                                <strong>Team Roles and Focus:</strong> Sahas Munamala will advance our core tree algorithms, leveraging the Wolfram Summer School. We will onboard Sumon U. as a full-stack developer to build a network dashboard, likely in Go, to visualize these complex interactions.
                            </li>
                            <li>
                                <strong>Architectural Foundation:</strong> This work directly implements the logic of the GVM. Our architecture uses recursively stacked trees for hardware-enforced confinement and resource provisioning. The algorithms developed will form the basis of the GVM’s ability to manage consensus, elasticity, and load balancing within a 9-cell "hypercell" tile.
                            </li>
                            <li>
                                <strong>Tooling:</strong> Concurrency for these processes will be prototyped and explored using Python, directly feeding into the "OAE Python Emulator" project listed in our OCP repository.
                            </li>
                        </ul>
                    </div>

                    {/* Card 3: Documentation & Demo */}
                    <div className="bg-white p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow text-left">
                        <h3 className="text-2xl font-bold mb-4">3. Document Repository and Physical Demonstration</h3>
                        <p className="mb-4">
                            To support our technical development and ensure our ideas are clearly communicated, we are establishing a robust documentation workflow and building towards a physical, real-world demonstration.
                        </p>
                        <ul className="list-disc list-inside space-y-3">
                            <li>
                                <strong>A Hybrid Documentation Strategy:</strong> Managed by Gia Singh, we will use a "Markdown-first, LaTeX-enhanced" approach. Markdown will be used for accessible, collaborative drafting, while LaTeX, via Pandoc, will provide high-fidelity typesetting for formal documents like patents and scientific papers, all version-controlled in our "OAE Latex Github" repository.
                            </li>
                            <li>
                                <strong>Simulation and Physical Demo:</strong> In parallel, our Python simulation will be enhanced. Ultimately, to prove the viability of our protocol—especially the benefits realized when a data "snake" is longer than the physical cable—we will build a physical demonstration using high-speed Thunderbolt interconnects, providing tangible proof for our simulated and specified claims.
                            </li>
                        </ul>
                    </div>

                </div>
            </section>
        </>
    );
}

/* helpers (unchanged) */
const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) => (
    <div className="text-center p-6">
        <div className="text-primary text-4xl mb-4 inline-block">{icon}</div>
        <h3 className="text-2xl font-bold mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
    </div>
);
const IndustryCard = ({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) => (
    <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-shadow">
        <div className="text-accent text-4xl mb-4 inline-block">{icon}</div>
        <h3 className="text-2xl font-bold mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
    </div>
);