// The single source of truth for our computational models.
// Centralizing this data allows it to be used across different components,
// such as the main model listing and the individual notebook pages.
// Each model represents a core argument in our thesis, serving as "proof by code."

export interface Notebook {
  id: number;
  title: string;
  slug: string;
  description: string;
  url: string; // For Wolfram models, this is a URL. For Python, it's a slug.
  // The 'type' is a literal union, ensuring that our routing logic can
  // deterministically select the correct component to render for each model.
  type: 'wolfram' | 'python' | 'python-csma' | 'python-rtt' | 'python-sequence' | 'placeholder';
  date: string;
}

// A type for the notebook data before the slug is generated.
// This ensures type safety at each stage of data transformation.
type RawNotebook = Omit<Notebook, 'slug'>;

// Utility to create a URL-friendly slug from a title.
// This is essential for our dynamic routing, providing a clean, predictable
// identifier for each model's page.
const slugify = (text: string): string => {
    return text
      .toString()
      .toLowerCase()
    .replace(/\s+/g, '-')      // Replace spaces with -
    .replace(/[^\w\-]+/g, '')    // Remove all non-word chars
    .replace(/\-\-+/g, '-')      // Replace multiple - with single -
    .replace(/^-+/, '')          // Trim - from start of text
    .replace(/-+$/, '');         // Trim - from end of text
  };

// First define the raw array with a type that correctly describes its shape.
// This ensures that each `type` property remains a literal union member
// and that TypeScript doesn't widen it to a plain string.
const rawNotebooks: RawNotebook[] = [
    {
      id: 1,
    title: "The Metcalfe-Boggs Model: A Formal Analysis of Statistical Arbitration and Efficiency",
    description: "A formal, executable model of the original 1976 Metcalfe-Boggs protocol for distributed packet switching. This notebook serves as 'Code as Proof,' deconstructing the dynamics of statistical arbitration on a shared, passive Ether. It mathematically models the interplay between the Transmission Interval, where a single station has acquired the Ether, and the Contention Interval, where multiple queued stations (Q) vie for access. By visualizing the core metrics of Acquisition Probability (A), Wait Time (W), and overall Efficiency (E), the model demonstrates the fundamental trade-offs and performance degradation inherent in a system reliant on simple packet collision and retransmission—setting the stage for the superior, deterministic model of Open Atomic Ethernet.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb",
      type: 'wolfram',
      date: "June 11, 2025",
    },
    {
      id: 2,
      title: "The Dædælus Efficiency Model: A Formal Comparison of Bandwidth- and Transaction-Multiplexing",
      description: "A computational essay that serves as 'Code as Proof,' formally modeling the foundational flaws of classical networking and demonstrating the superiority of the Dædælus transactional fabric. The notebook begins by deconstructing the shared-media contention of the 1976 Metcalfe-Boggs model and the latency-bound throughput of TCP (Mathis equation), proving how traditional bandwidth-multiplexing over unreliable links inevitably leads to efficiency collapse, the loss of epistemic certainty, and unbounded tail latency. It then contrasts this with the Dædælus architecture, simulating how a reliable N2N Lattice that uses Transaction-Multiplexing and the Reversible Snake protocol eliminates contention, is immune to packet loss, and provides the deterministic performance necessary for a Truncated Tail Latency.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas2.nb",
      type: 'wolfram',
      date: "June 12, 2025",
    },
    {
      id: 3,
      title: "Contention and State: A Formal Analysis of Classical Ethernet and Spekkens Toy Models",
      description: "A computational essay presented in two parts, first deconstructing the foundational flaws of classical networking, and then exploring the abstract state dynamics that inform the Daedaelus architecture. The first section provides an agent-based simulation of the 1976 Metcalfe-Boggs protocol. It visualizes the chaotic nature of statistical arbitration on a shared medium, where frequent packet collisions represent the \"irreversible smash...of Shannon information\" and the microscopic origin of unbounded tail latency.  The second section explores a Spekkens Toy Model, a framework inspired by Quantum Information Theory. Through interactive visualizations of state-transition graphs, it provides a 'Code as Proof' artifact for understanding the principles of Token Dynamics and Reversible Subtransactions, which are the mathematical bedrock of our deterministic, contention-free protocols.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas3.nb",
      type: 'wolfram',
      date: "June 14, 2025",
    },
    {
      id: 4,
      title: "Foundations of Reversibility: A Formal Analysis of the Spekkens Toy Model",
      description: "This computational essay provides a suite of interactive tools for the formal analysis of the Spekkens Toy Model, a framework inspired by Quantum Information Theory that is foundational to our architecture. It serves as 'Code as Proof' for the principles of state evolution, visualizing how a set of reversible permutations acts on composite states (formed via Kronecker product) to create a traversable, multiway state-space graph. By exploring these state dynamics, we develop the mathematical intuition for the Token Dynamics, Reversible Subtransactions, and epistricted registers that allow our protocols to guarantee exactly-once semantics and escape the irreversible failures of conventional networking.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas4.nb",
      type: 'wolfram',
      date: "June 17, 2025",
    },
    {
      id: 5,
      title: "Model 5: Python TIKTYKTIK Protocol",
      description: "A Python-based simulation demonstrating the three-way handshake required to achieve mutual, persistent knowledge between two agents, forming the basis of a reliable link.",
      url: "model-5-python-tiktyktik-protocol",
      type: 'python',
      date: "June 18, 2025",
    },
    {
      id: 6,
      title: "Model 6: Python CSMA/CD Contention Analysis",
      description: "A Python-based agentic simulation of the 1976 Metcalfe-Boggs protocol. This model serves as a computational proof, demonstrating the consequences of statistical arbitration, the necessity of unbounded backoff, and the resulting degradation of transactional capacity on a shared Ether. It is a tool for understanding the problems we solve.",
      url: "model-6-python-csmacd-contention-analysis",
      type: 'python-csma',
      date: "June 18, 2025",
    },
    {
      id: 7,
      title: "Model 7: Event-Driven RTT and Utilization Analysis",
      description: "A detailed, event-driven Python simulation that models packet transmission, propagation delay, and acknowledgment cycles. This provides a precise analysis of how round-trip time (RTT) and link utilization are affected by the contention inherent in classical Ethernet, forming a key part of our argument against bandwidth-first design.",
      url: "model-7-python-rtt-and-utilization-analysis",
      type: 'python-rtt',
      date: "June 18, 2025",
    },
    {
      id: 8,
      title: "The Origin of Tail Latency: An Agent-Based Simulation of Ethernet Contention",
      description: "A precise, agent-based simulation of the 1976 Metcalfe-Boggs protocol, designed as 'Code as Proof' to visualize the microscopic origins of network inefficiency. This emulator models each station as an autonomous agent governed by the rules of statistical arbitration, including exponential backoff in response to the frequent packet collisions that define a contended, shared Ether. By dynamically plotting metrics like Round-Trip Time (RTT) Distribution and channel utilization, the model provides a definitive illustration of how this probabilistic design inevitably leads to the unbounded tail latency and loss of epistemic certainty that our own architecture eliminates.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/python%20ddl.nb",
      type: 'wolfram',
      date: "June 18, 2025",
    },
    {
      id: 9,
      title: "A Dædælus Toolkit: Formal Models of Contention, Reliability, and Topology",
      description: "A computational toolkit featuring a collection of interactive, formal models that serve as 'Code as Proof' for the foundational principles of the Dædælus architecture. The notebook begins with an agent-based simulation of the classical CSMA/CD protocol, visualizing the chaotic consequences of statistical arbitration and the origins of unbounded tail latency. It then explores the mechanics of reliable, two-party communication with a simulation of the Alternating Bit Protocol, demonstrating the challenge of maintaining state in the face of packet and acknowledgment loss. Finally, it provides a graph metrics dashboard to quantitatively prove the superior resilience of a distributed N2N Lattice (Baran's distributed model) over fragile, centralized topologies.  Together, these models deconstruct the flaws of conventional networking and provide the formal justification for an architecture based on reliable, contention-free links and resilient topologies.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/python%20ddl%202.nb",
      type: 'wolfram',
      date: "June 18, 2025",
    },
    {
      id: 10,
      title: "Model 10: A Computational History of Ethernet Contention",
      description: "A sequence of six Python simulations that computationally model the evolution of Ethernet, from the original ALOHA protocols to a modern, acknowledged data transfer over CSMA/CD. Each step serves as a 'proof by code' for the principles of network contention and reliability.",
      url: "ethernet-emulation-sequence",
      type: 'python-sequence',
      date: "June 18, 2025",
    },
    {
      id: 11,
      title: "Model 11: A Computational History of Ethernet Simulations",
      description: "A single‐page sequence showcasing twenty-five Python-based Ethernet simulations — from classical CSMA/CD contention through modern fabric-based transactions — complete with textual logs and sequence diagrams.",
      url: "model-11-a-computational-history-of-ethernet-simulations",
      type: 'python-sequence',
      date: "June 20, 2025",
    },
    // This model now serves as the gallery for our core Python emulators and their visual outputs.
    // By changing the type to 'python-sequence', we direct routing to the component that will render this new layout.
    {
      id: 12,
      title: "Model 12: DDL_Emulator Scripts & Visualizations",
      description: "A comprehensive gallery of our core Python emulators and the visual artifacts they generate. This page provides a direct view into our 'Code as Proof' methodology, showcasing the scripts that model network contention and the resulting simulation outputs.",
      url: "model-12-ddl-emulator-scripts-and-visualizations",
      type: 'python-sequence',
      date: "July 4, 2025",
    },
  {
    id: 13,
    title: "FabricCalculus: A Formal Model for Policy-Driven Geodesic Routing",
    description: "This notebook serves as an executable specification for our FabricCalculus, a foundational component of the Dædælus Transaction Fabric. We move beyond the one-dimensional and flawed metric of bandwidth, instead defining a multi-dimensional FabricMetricTensor that calculates a true TransactionalDistance based on a weighted policy of latency, bandwidth, and link integrity. The GeodesicTransactionRouter acts as the intelligence of the Graph Virtual Machine (GVM), computing the optimal 'geodesic' path across a given N2N Lattice based on these application-defined policies.  The interactive visualization demonstrates this principle in action, showing how the ideal transaction path dynamically reroutes in response to changing link conditions, providing a formal, 'code-as-proof' model for a resilient and policy-driven network fabric.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/cellular%20automata%20-%20from%20classical%20computation%20to%20quantum%20error%20correction.nb",
    type: 'wolfram',
    date: "July 4, 2025",
  },
  {
    id: 14,
    title: "Local Rules, Global Order: An Exploration of Classical Cellular Automata",
    description: "This notebook serves as a 'Code as Proof' exploration into the foundational principle of emergent complexity, demonstrating how simple, local, deterministic rules can give rise to complex and persistent global order. Through an interactive showcase, it models various iconic patterns from Conway's Game of Life—including still lifes, oscillators, and spaceships—as well as the behavior of other classical cellular automaton rule-sets. This analysis is central to the Dædælus philosophy, as these automata provide a direct, computational analogue for the behavior of our Graph Virtual Machine (GVM).  The stable, self-organizing patterns that emerge on this grid from simple neighbor-to-neighbor interactions are the conceptual bedrock for designing the resilient and autonomous behavior of our N2N Lattice.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/2.%20cellular%20automata%20-%20from%20classical%20computation%20to%20quantum%20error%20correction.nb",
    type: 'wolfram',
    date: "July 4, 2025",
  },
  {
    id: 15,
    title: "From Local Rules to Global Machines: Simulating Emergent Structures in Cellular Automata",
    description: "This notebook provides a 'Code as Proof' exploration into the emergence of complex, persistent structures from simple, local rules within classical cellular automata. It simulates iconic patterns from Conway's Game of Life, such as the Gosper glider gun, to demonstrate how machine-like, self-perpetuating global behavior can arise from deterministic, neighbor-to-neighbor interactions. It then uses a custom 'color-by-age' automaton to study how stable, long-lived patterns evolve from a random initial state, providing insight into the principles of self-organization. This analysis is fundamental to the Dædælus philosophy, serving as a direct computational analogue for how our N2N Lattice acts as a substrate for the stable, resilient logical topologies managed by the Graph Virtual Machine (GVM).",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/3.%20cellular%20automata%20-%20from%20classical%20computation%20to%20quantum%20error%20correction.nb",
    type: 'wolfram',
    date: "July 4, 2025",
  },
  {
    id: 16,
    title: "The Distributed Firing Squad Problem: A Comparative Analysis of Synchronization Models",
    description: "This notebook provides a 'Code as Proof' exploration of the classic Firing Squad Synchronization Problem, serving as a formal, comparative analysis of different models for achieving simultaneity in a distributed system. It first implements an asynchronous, message-passing model where CELLs use Lamport Clocks to establish a definite causal \"happens-before\" ordering, representing a traditional approach to distributed coordination.  It then contrasts this with two classical, one-dimensional cellular automata solutions (including Mazoyer's algorithm), which achieve perfect, global synchronization through simple, deterministic local rules in an idealized, synchronous time model. By juxtaposing these different computational models of time, this analysis highlights the \"temporal inconsistencies between computation and physics,\" demonstrating the fragility of logical simultaneity and motivating the Dædælus architecture, which favors local causal consistency and Token Dynamics over the illusion of a universal 'now'.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/4.%20cellular%20automata%20-%20from%20classical%20computation%20to%20quantum%20error%20correction.nb",
    type: 'wolfram',
    date: "July 4, 2025",
  },
  {
    id: 17,
    title: "The Graph Virtual Machine: A Formal Model of Lamport's Causal Ordering",
    description: "This notebook implements a Graph Virtual Machine (GVM) that serves as a 'Code as Proof' model of Leslie Lamport’s classical 'happens-before' relation. The GVM processes a series of causal assertions (e.g., A -> B) to compute and maintain the full transitive closure of the event history, enforcing a definite, partial ordering. It visualizes the resulting causal structure as both a full dependency graph and a Hasse Diagram (its transitive reduction), providing a clear view of direct vs. implied causality. This formal model of definite causal order perfectly embodies the 'Forward-In-Time-Only' (FITO) thinking that underpins traditional distributed systems. Its strict enforcement of acyclicity—and its inability to resolve a paradox—provides a sharp contrast to the principles of Reversible Subtransactions that are central to the Dædælus philosophy.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/5.%20cellular%20automata%20-%20from%20classical%20computation%20to%20quantum%20error%20correction.nb",
    type: 'wolfram',
    date: "July 4, 2025",
  },
  {
    id: 18,
    title: "Open Atomic Ethernet: The Clos Network (Reliability is for Everyone) Executable Product Specification",
    description: "This notebook is the master document for the Open Atomic Ethernet (OAE) project, and doesn't stop serving as a comprehensive and executable specification for the Dædælus architecture. It lays out the foundational philosophy and design principles, including Symmetric Reversibility, the paradigm shift from Bandwidth to Interactions, and the resilient N2N Lattice topology.True to our 'Code as Proof' methodology, the formal specification is interwoven with executable Mathematica models that provide definitive, computational demonstrations of these principles in action.These models include formal analyses of network resilience, simulations of causal dynamics like the Alternating Bit Protocol, and proofs of concept for Reversible Subtransactions, collectively forming the rigorous underpinnings of our Transaction Fabric. ",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/6.%20OAE-SPEC-MAIN.nb",
    type: 'wolfram',
    date: "July 4, 2025",
  },
  ];

// Now map over the typed array to inject the slug field without widening `type`.
export const notebooks: Notebook[] = rawNotebooks.map(n => ({
    ...n,
    slug: slugify(n.title),
  }));