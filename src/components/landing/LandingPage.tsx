/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useEffect, useState } from "react";
import {
    FaCogs, FaShareSquare, FaPaintBrush, FaChartBar,
    FaPlayCircle, FaGraduationCap, FaBuilding,
} from "react-icons/fa";
import Link from "next/link";

/* LOAD hero background … unchanged */
const HERO_BG =
    "url(/logo.f53b8de5b49089ebcf94.png) repeat 0 0 / 220px 160px";

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
            <section
                suppressHydrationWarning
                className="relative text-center py-20 px-4 overflow-hidden"
                style={{ background: HERO_BG, color: "rgb(130,0,0)", textShadow: "0 0 1px black" }}
            >
                <div style={overlay} />
                <div className="relative z-10 max-w-4xl mx-auto">
                    <h1 className="text-5xl font-bold mb-4 font-inika">
                        Hundreds of Nodes, Zero Cost
                    </h1>
                    <p className="text-xl mb-8 font-raleway">
                        Our platform capacitizes Digital Twins of Ethernet complexity, moving well beyond irreversible Shannon limits.
                    </p>
                    <Link
                        href="/Metcalfe+Boggs.pdf"
                        target="_blank"
                        className="inline-block px-8 py-3 bg-white text-primary font-bold rounded-md hover:bg-gray-200 transition-transform hover:scale-105"
                        style={{ background: "rgb(184,58,75)" }}
                    >
                        Graph Automata Foundations
                    </Link>
                </div>
            </section>

            {/* features & use-cases – unchanged, just icons wrapped in <C> */}
            <section className="py-20 px-4">
                <h2 className="text-4xl font-bold text-center mb-12">
                    A Drop in the Bucket for a New Computing Paradigm
                </h2>
                <div className="container mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-10">
                    <FeatureCard icon={<C><FaCogs /></C>} title="Time-Reversible Constructors" description="Petri nets that recover without smash-and-restart." />
                    <FeatureCard icon={<C><FaShareSquare /></C>} title="Multiway Systems" description="Traverse every causal branch for richer Digital Twins." />
                    <FeatureCard icon={<C><FaPaintBrush /></C>} title="Graph Virtual Machine" description="Demand-driven relations on reliable storage." />
                    <FeatureCard icon={<C><FaChartBar /></C>} title="Precise Emulation" description="Co-operative emulators with information-theoretic rigor." />
                </div>
            </section>

            <section className="py-20 px-4 bg-gray-100">
                <h2 className="text-4xl font-bold text-center mb-4">Use Cases</h2>
                <p className="text-lg text-center text-gray-600 max-w-3xl mx-auto mb-12">
                    Anywhere distributed precision matters.
                </p>
                <div className="container mx-auto grid md:grid-cols-3 gap-10">
                    <IndustryCard icon={<C><FaPlayCircle /></C>} title="Multiplayer Games" description="Worlds that shrug off partitions and desyncs." />
                    <IndustryCard icon={<C><FaGraduationCap /></C>} title="Atomic Transactions" description="Truncated tail latency without heartbeats." />
                    <IndustryCard icon={<C><FaBuilding /></C>} title="Quantum Interfaces" description="Classical control for probabilistic hardware." />
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
