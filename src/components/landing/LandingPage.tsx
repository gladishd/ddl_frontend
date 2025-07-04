/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useEffect, useState } from "react";
import {
    FaCogs,
    FaShareSquare,
    FaPaintBrush,
    FaChartBar,
} from "react-icons/fa";
import Link from "next/link";
import EthernetModel from "./EthernetModel";
import MenuButton from "../MenuButton"; // Import the new component

/* LOAD hero background … unchanged */
const HERO_BG = "url(/Dædælus.png) repeat 0 0 / 220px 160px";

const overlay: React.CSSProperties = {
    position: "absolute",
    inset: 0,
    backgroundColor: "rgba(0,38,38,0.6)",
    zIndex: 1,
};

export default function LandingPage() {
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

                {/* This button provides access to the main navigational structure of the Graph Virtual Machine.
                    It's placed here to provide immediate access from the primary entry point of the application.
                */}
                <div className="hero-menu-button-container">
                    <MenuButton />
                </div>

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
            {/* feature grid */}
            <section className="py-20 px-4">
                <h2 className="text-4xl font-bold text-center mb-12">
                    The Bandwidth Argument We Want to Make
                </h2>
                <div className="container mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-10">
                    <FeatureCard
                        icon={<C><FaCogs /></C>}
                        title="1. Half-Duplex Contention"
                        description="An agentic simulation of the shared Metcalfe ether. We computationally model transmission and contention intervals to show how multiplexing bandwidth fundamentally limits the transactional capacity of the link."
                    />
                    <FeatureCard
                        icon={<C><FaShareSquare /></C>}
                        title="2. Full-Duplex Degradation"
                        description="A model of modern, full-duplex links demonstrating how bandwidth-multiplexing decimates TCP throughput under loss, leading to severe round-trip latency degradation and proving the model is broken."
                    />
                    <FeatureCard
                        icon={<C><FaPaintBrush /></C>}
                        title="3. The Circulating Snake"
                        description="We demolish the assumption that stop-and-wait throttles bandwidth. This model shows a 'snake' of bits longer than the wire, where acknowledgements arrive before transmission ends, eliminating the round-trip penalty."
                    />
                    <FeatureCard
                        icon={<C><FaChartBar /></C>}
                        title="4. Interaction Multiplexing"
                        description="The superior model. We demonstrate that multiplexing handshake interactions, not time-sharing the link, maximizes total throughput and provides deterministic latency that walks right over packet loss."
                    />
                </div>
            </section>

            {/* The old Strategic Initiatives section has been removed from here and is now handled by the dedicated StrategicInitiatives.tsx component, called from page.tsx */}

            {/* ============================================= */}
            {/* === NEW ETHERNET SIMULATION MODEL SECTION === */}
            {/* ============================================= */}
            <EthernetModel />
        </>
    );
}

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
        <p className="text-gray-600 text-left">{description}</p>
    </div>
);