/* eslint-disable @next/next/no-img-element */
// This landing page introduces our mission: to address fundamental
// problems in distributed systems.
"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
    FaCogs,
    FaShareSquare,
    FaPaintBrush,
    FaChartBar,
    FaPlayCircle,
    FaGraduationCap,
    FaBuilding,
} from "react-icons/fa";
import News from "./News";

/* ───── Utility ───── */
const ClientOnly: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [mounted, setMounted] = useState(false);
    useEffect(() => setMounted(true), []);
    return mounted ? <>{children}</> : null;
};

/* ───── Static styles (never change after build) ───── */
const HERO_BG =
    "url(/OAE_Logo_copy.pdf) repeat 0 0 / 300px 300px, #000"; // Dark-Reader proof

const overlayStyle: React.CSSProperties = {
    position: "absolute",
    inset: 0,
    backgroundColor: "rgba(0, 38, 38, 0.85)",
    zIndex: -1,
};

export default function LandingPage() {
    /* Fake loading state purely client-side (not in SSR markup) */
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        const id = setTimeout(() => setLoading(false), 1200);
        return () => clearTimeout(id);
    }, []);

    return (
        <>
            {/* Loading screen appears only after mount → no SSR mismatch */}
            {loading && (
                <div className="loading-overlay">
                    <div className="loading-spinner" />
                    <p className="loading-text">Architecting the Future…</p>
                </div>
            )}

            <div className="bg-gray-50 text-gray-800">
                {/* ─── Hero ─── */}
                <section
                    suppressHydrationWarning
                    className="relative text-center py-20 px-4 text-white overflow-hidden"
                    style={{ background: HERO_BG }}
                >
                    <div style={overlayStyle} />
                    <div className="relative z-10">
                        <h1 className="text-5xl font-bold mb-4 font-inika">
                            Interactive Content, Tailored Experiences
                        </h1>
                        <p className="text-xl max-w-3xl mx-auto mb-8 font-raleway">
                            Our platform provides the tools to build and manage “Digital
                            Twins” of complex processes, moving beyond the limitations of
                            irreversible Shannon information.
                        </p>
                        <a
                            href="/Metcalfe+Boggs.pdf"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-8 py-3 bg-white text-primary font-bold rounded-md hover:bg-gray-200 transition-transform transform hover:scale-105"
                        >
                            Graph Automata Foundations
                        </a>
                    </div>
                </section>

                {/* ─── Features ─── */}
                <section className="py-20 px-4">
                    <h2 className="text-4xl font-bold text-center mb-12">
                        An Interface to a New Computing Paradigm
                    </h2>
                    <div className="container mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-10">
                        <FeatureCard
                            icon={
                                <ClientOnly>
                                    <FaCogs />
                                </ClientOnly>
                            }
                            title="Time-Reversible Constructors"
                            description="Define systems as Petri nets that recover without smash-and-restart."
                        />
                        <FeatureCard
                            icon={
                                <ClientOnly>
                                    <FaShareSquare />
                                </ClientOnly>
                            }
                            title="Multiway Systems"
                            description="Explore every causal branch for truly resilient Digital Twins."
                        />
                        <FeatureCard
                            icon={
                                <ClientOnly>
                                    <FaPaintBrush />
                                </ClientOnly>
                            }
                            title="Graph Virtual Machine"
                            description="A GVM that builds and tears down named relations on emergent demand."
                        />
                        <FeatureCard
                            icon={
                                <ClientOnly>
                                    <FaChartBar />
                                </ClientOnly>
                            }
                            title="Precise Emulation"
                            description="Competitive & cooperative emulators with information-theoretic rigor."
                        />
                    </div>
                </section>

                {/* ─── Use-cases ─── */}
                <section className="py-20 px-4 bg-gray-100">
                    <h2 className="text-4xl font-bold text-center mb-4">Use Cases</h2>
                    <p className="text-lg text-center text-gray-600 max-w-3xl mx-auto mb-12">
                        Our protocols shine anywhere distributed precision matters.
                    </p>
                    <div className="container mx-auto grid md:grid-cols-3 gap-10">
                        <IndustryCard
                            icon={
                                <ClientOnly>
                                    <FaPlayCircle />
                                </ClientOnly>
                            }
                            title="Multiplayer Games"
                            description="Game worlds that shrug off partitions and desyncs."
                        />
                        <IndustryCard
                            icon={
                                <ClientOnly>
                                    <FaGraduationCap />
                                </ClientOnly>
                            }
                            title="Atomic Transactions"
                            description="“Truncated tail latency” without heartbeats or timeouts."
                        />
                        <IndustryCard
                            icon={
                                <ClientOnly>
                                    <FaBuilding />
                                </ClientOnly>
                            }
                            title="Quantum Interfaces"
                            description="Classical control that embraces probabilistic hardware."
                        />
                    </div>
                </section>

                {/* ─── News feed ─── */}
                <News />
            </div>
        </>
    );
}

/* ───── Tiny helpers ───── */
const FeatureCard = ({
    icon,
    title,
    description,
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
}) => (
    <div className="text-center p-6">
        <div className="text-primary text-4xl mb-4 inline-block">{icon}</div>
        <h3 className="text-2xl font-bold mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
    </div>
);

const IndustryCard = ({
    icon,
    title,
    description,
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
}) => (
    <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-shadow">
        <div className="text-accent text-4xl mb-4 inline-block">{icon}</div>
        <h3 className="text-2xl font-bold mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
    </div>
);
