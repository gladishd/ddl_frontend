// This landing page introduces our mission: to address fundamental problems in distributed systems.
// Each section reflects a core principle, from the creation of Digital Twins to ensuring non-zero-sum game outcomes.
'use client';

import React, { useState, useEffect } from 'react';
import { FaCogs, FaShareSquare, FaPaintBrush, FaChartBar, FaPlayCircle, FaGraduationCap, FaBuilding } from 'react-icons/fa';

// The ClientOnly component provides a robust boundary against hydration errors.
// It ensures that its children are only rendered on the client, preventing mismatches caused by
// non-deterministic client-side factors, such as browser extensions that modify the DOM.
const ClientOnly: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [hasMounted, setHasMounted] = useState(false);

    useEffect(() => {
        setHasMounted(true);
    }, []);

    if (!hasMounted) {
        return null;
    }

    return <>{children}</>;
};

const LandingPage = () => {
    // A clear loading state is fundamental to a robust user experience, preventing ambiguity during initialization.
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Simulate initial data fetching or asset loading.
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 1500); // Adjust timing as needed

        return () => clearTimeout(timer);
    }, []);

    // This inline style creates a tessellated background, a visual metaphor for the structured,
    // yet dynamic, graph automata that form the foundation of our systems.
    const heroStyle = {
        backgroundImage: `url(/logo.f53b8de5b49089ebcf94.png)`,
        backgroundSize: '300px 300px', // Adjust size as needed
        backgroundRepeat: 'repeat',
        backgroundColor: '#000000', // Fallback color
        position: 'relative' as 'relative',
        zIndex: 1,
    };

    const overlayStyle = {
        position: 'absolute' as 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 38, 38, 0.85)', // Dark teal overlay with 85% opacity
        zIndex: -1,
    };

    return (
        <>
            <div className={`loading-overlay ${!isLoading ? 'hidden' : ''}`}>
                <div className="loading-spinner"></div>
                <p className="loading-text">Architecting the Future...</p>
            </div>
            <div className="bg-gray-50 text-gray-800">
                {/* Hero Section */}
                <section className="relative text-center py-20 px-4 text-white overflow-hidden" style={heroStyle}>
                    <div style={overlayStyle}></div>
                    <div className="relative z-10">
                        <h1 className="text-5xl font-bold mb-4 font-inika">Interactive Content, Tailored Experiences</h1>
                        <p className="text-xl max-w-3xl mx-auto mb-8 font-raleway">
                            Our platform provides the tools to build and manage 'Digital Twins' of complex processes, moving beyond the limitations of irreversible Shannon information.
                        </p>
                        <button className="px-8 py-3 bg-white text-primary font-bold rounded-md hover:bg-gray-200 transition-transform transform hover:scale-105">
                            Get Started
                        </button>
                    </div>
                </section>

                {/* Features for Creators Section */}
                <section className="py-20 px-4">
                    <h2 className="text-4xl font-bold text-center mb-12">An Interface to a New Computing Paradigm</h2>
                    <div className="container mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-10">
                        <FeatureCard
                            icon={<ClientOnly><FaCogs /></ClientOnly>}
                            title="Time-Reversible Constructors"
                            description="Define systems as Petri nets that no longer rely on the irreversible smash and restart to recover from failures." />
                        <FeatureCard
                            icon={<ClientOnly><FaShareSquare /></ClientOnly>}
                            title="Multiway Systems"
                            description="Explore the causal graph of all possible outcomes, creating truly dynamic and resilient Digital Twins." />
                        <FeatureCard
                            icon={<ClientOnly><FaPaintBrush /></ClientOnly>}
                            title="Graph Virtual Machine"
                            description="A dynamic GVM that builds and tears down 'named' graph relationships based on emergent properties." />
                        <FeatureCard
                            icon={<ClientOnly><FaChartBar /></ClientOnly>}
                            title="Precise Emulation"
                            description="Develop 'precise information-theoretic' emulators to enable competitive and cooperative interactions for Digital Twins." />
                    </div>
                </section>

                {/* Industry Section */}
                <section className="py-20 px-4 bg-gray-100">
                    <h2 className="text-4xl font-bold text-center mb-4">Use Cases</h2>
                    <p className="text-lg text-center text-gray-600 max-w-3xl mx-auto mb-12">
                        Our protocols, data structures, and algorithms find application in any distributed infrastructure where time-reversibility and informational precision are paramount.
                    </p>
                    <div className="container mx-auto grid md:grid-cols-3 gap-10">
                        <IndustryCard
                            icon={<ClientOnly><FaPlayCircle /></ClientOnly>}
                            title="Multiplayer Games & Simulations"
                            description="Build game states and digital worlds that are inherently resilient to network partitions and desynchronization." />
                        <IndustryCard
                            icon={<ClientOnly><FaGraduationCap /></ClientOnly>}
                            title="Advanced Transaction Processing"
                            description="Implement systems with 'Truncated Tail Latency', where transactions succeed or fail atomically without timeouts or heartbeats." />
                        <IndustryCard
                            icon={<ClientOnly><FaBuilding /></ClientOnly>}
                            title="Interfaces to Quantum Computers"
                            description="Create classical control systems that can gracefully manage the probabilistic nature of quantum computation." />
                    </div>
                </section>
            </div>
        </>
    );
};

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

export default LandingPage;