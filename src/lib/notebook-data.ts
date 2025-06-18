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
  type: 'wolfram' | 'python' | 'python-csma' | 'python-rtt';
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
    .replace(/\s+/g, '-')       // Replace spaces with -
    .replace(/[^\w\-]+/g, '')   // Remove all non-word chars
    .replace(/\-\-+/g, '-')     // Replace multiple - with single -
    .replace(/^-+/, '')         // Trim - from start of text
    .replace(/-+$/, '');        // Trim - from end of text
};

// First define the raw array with a type that correctly describes its shape.
// This ensures that each `type` property remains a literal union member
// and that TypeScript doesn't widen it to a plain string.
const rawNotebooks: RawNotebook[] = [
  {
    id: 1,
    // This agentic simulation models the original half-duplex, shared Metcalfe ether.
    // It's a computational exploration of his assertion that "at some point the Ether will be so busy that additional stations will just divide more finely the already inadequate bandwidth."
    // We use this to demonstrate how contending for a shared medium fundamentally limits transactional capacity.
    title: "Model 1: Half-Duplex Contention",
    description: "An agentic simulation of the original 1976 Metcalfe-Boggs protocol. This model visualizes the transmission and contention intervals on a shared half-duplex medium, demonstrating how statistical arbitration impacts throughput.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb",
    type: 'wolfram',
    date: "June 11, 2025",
  },
  {
    id: 2,
    // This model extends the analysis to modern full-duplex links, showing that even without physical collisions,
    // the multiplexing of bandwidth creates "chaotic contention" that decimates the throughput of reliable protocols like TCP.
    title: "Model 2: Full-Duplex Degradation",
    description: "A model of modern full-duplex links where multiple TCP flows compete. It shows how bandwidth-multiplexing still leads to severe latency degradation and reduced throughput under contention and packet loss.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas2.nb",
    type: 'wolfram',
    date: "June 12, 2025",
  },
  {
    id: 3,
    // Here, we demolish the foundational assumption that a round-trip interaction must incur a full RTT penalty.
    // This model illustrates the concept of a data packet being "longer than the wire," where a pipelined acknowledgement
    // can be received before the sender has even finished transmitting, thus achieving nearly 100% link utilization.
    title: "Model 3: The Circulating Snake",
    description: "This model demolishes the 'stop-and-wait' assumption. It demonstrates a 'snake' of bits longer than the physical link, where pipelined acknowledgements eliminate the round-trip penalty and achieve maximum transactional throughput.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas3.nb",
    type: 'wolfram',
    date: "June 14, 2025",
  },
  {
    id: 4,
    // This is the Daedaelus way. Instead of multiplexing bandwidth, the GVM interleaves atomic request/reply transactions.
    // This model provides "definitive, visual proof" that this is "fundamentally more efficient" for concurrent operations.
    title: "Model 4: Interaction Multiplexing",
    description: "The superior model. We show that multiplexing discrete, reliable handshake interactions, rather than contending for bandwidth, maximizes total system throughput and offers deterministic latency, walking right over packet loss.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas4.nb",
    type: 'wolfram',
    date: "June 17, 2025",
  },
  {
    id: 5,
    // This Python model provides a 'precise information-theoretic' emulator of the "I Know That You Know That I Know" property.
    // It's a foundational link utility for achieving mutual knowledge and creating a persitable, bipartite element of information.
    title: "Model 5: Python TIKTYKTIK Protocol",
    description: "A Python-based simulation demonstrating the three-way handshake required to achieve mutual, persistent knowledge between two agents, forming the basis of a reliable link.",
    url: "model-5-python-tiktyktik-protocol",
    type: 'python',
    date: "June 18, 2025",
  },
  {
    id: 6,
    // This is not merely a simulation; it is a computational proof of the consequences of statistical arbitration.
    // We model the "irreversible smash and restart of Shannon information" that is the hallmark of CSMA/CD to show
    // why a system built on such fragile assumptions cannot provide the guarantees required by modern distributed systems.
    title: "Model 6: Python CSMA/CD Contention Analysis",
    description: "A Python-based agentic simulation of the 1976 Metcalfe-Boggs protocol. This model serves as a computational proof, demonstrating the consequences of statistical arbitration, the necessity of unbounded backoff, and the resulting degradation of transactional capacity on a shared Ether. It is a tool for understanding the problems we solve.",
    url: "model-6-python-csmacd-contention-analysis",
    type: 'python-csma',
    date: "June 18, 2025",
  },
  {
    id: 7,
    // This event-driven simulation provides a more precise analysis of round-trip dynamics.
    // It moves beyond showing *that* contention occurs and models *how* it impacts latency and utilization.
    // This is crucial for understanding the RTT component in the Mathis equation and arguing for a shift
    // from bandwidth-multiplexing to transaction-multiplexing.
    title: "Model 7: Event-Driven RTT and Utilization Analysis",
    description: "A detailed, event-driven Python simulation that models packet transmission, propagation delay, and acknowledgment cycles. This provides a precise analysis of how round-trip time (RTT) and link utilization are affected by the contention inherent in classical Ethernet, forming a key part of our argument against bandwidth-first design.",
    url: "model-7-python-rtt-and-utilization-analysis",
    type: 'python-rtt',
    date: "June 18, 2025",
  },
  {
    id: 8,
    // A live Wolfram model providing a precise, event-driven analysis of Round-Trip Time (RTT) and channel utilization.
    // This model serves as a computational proof, demonstrating the direct impact of statistical arbitration and collision
    // recovery on the effective latency and throughput of a classical Ethernet link.
    title: "Model 8: Wolfram RTT & Utilization Analysis",
    description: "A live Wolfram model providing a precise, event-driven analysis of Round-Trip Time (RTT) and channel utilization under the classical Ethernet protocol, revealing the direct impact of statistical arbitration on latency.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/python%20ddl.nb",
    type: 'wolfram',
    date: "June 18, 2025",
  },
  {
    id: 9,
    // This Wolfram model is a computational essay on the core principles of CSMA/CD. It serves as a verifiable,
    // interactive proof of the consequences of a system built on contended access, including carrier sense,
    // collision detection, and the necessity of binary exponential backoff.
    title: "Model 9: Wolfram CSMA/CD Contention Model",
    description: "A live Wolfram model demonstrating the core principles of CSMA/CD, including carrier sense, collision detection, and binary exponential backoff. This computational proof explores the consequences of statistical arbitration on a shared medium.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/python%20ddl%202.nb",
    type: 'wolfram',
    date: "June 18, 2025",
  },
];

// Now map over the typed array to inject the slug field without widening `type`.
export const notebooks: Notebook[] = rawNotebooks.map(n => ({
  ...n,
  slug: slugify(n.title),
}));