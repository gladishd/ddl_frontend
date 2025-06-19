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
  type: 'wolfram' | 'python' | 'python-csma' | 'python-rtt' | 'python-sequence';
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
    title: "Model 1: Half-Duplex Contention",
    description: "An agentic simulation of the original 1976 Metcalfe-Boggs protocol. This model visualizes the transmission and contention intervals on a shared half-duplex medium, demonstrating how statistical arbitration impacts throughput.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb",
    type: 'wolfram',
    date: "June 11, 2025",
  },
  {
    id: 2,
    title: "Model 2: Full-Duplex Degradation",
    description: "A model of modern full-duplex links where multiple TCP flows compete. It shows how bandwidth-multiplexing still leads to severe latency degradation and reduced throughput under contention and packet loss.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas2.nb",
    type: 'wolfram',
    date: "June 12, 2025",
  },
  {
    id: 3,
    title: "Model 3: The Circulating Snake",
    description: "This model demolishes the 'stop-and-wait' assumption. It demonstrates a 'snake' of bits longer than the physical link, where pipelined acknowledgements eliminate the round-trip penalty and achieve maximum transactional throughput.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas3.nb",
    type: 'wolfram',
    date: "June 14, 2025",
  },
  {
    id: 4,
    title: "Model 4: Interaction Multiplexing",
    description: "The superior model. We show that multiplexing discrete, reliable handshake interactions, rather than contending for bandwidth, maximizes total system throughput and offers deterministic latency, walking right over packet loss.",
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
    title: "Model 8: Wolfram RTT & Utilization Analysis",
    description: "A live Wolfram model providing a precise, event-driven analysis of Round-Trip Time (RTT) and channel utilization under the classical Ethernet protocol, revealing the direct impact of statistical arbitration on latency.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/python%20ddl.nb",
    type: 'wolfram',
    date: "June 18, 2025",
  },
  {
    id: 9,
    title: "Model 9: Wolfram CSMA/CD Contention Model",
    description: "A live Wolfram model demonstrating the core principles of CSMA/CD, including carrier sense, collision detection, and binary exponential backoff. This computational proof explores the consequences of statistical arbitration on a shared medium.",
    url: "https://www.wolframcloud.com/obj/gladishdean/Published/python%20ddl%202.nb",
    type: 'wolfram',
    date: "June 18, 2025",
  },
  // This is the new addition, combining all Python models into a single narrative page.
  // It provides a 'Multiway System' view of our simulation development, showing the evolution of the models.
  {
    id: 10,
    title: "A Computational History of Ethernet Contention",
    description: "A sequence of six Python simulations that computationally model the evolution of Ethernet, from the original ALOHA protocols to a modern, acknowledged data transfer over CSMA/CD. Each step serves as a 'proof by code' for the principles of network contention and reliability.",
    url: "ethernet-emulation-sequence",
    type: 'python-sequence',
    date: "June 18, 2025",
  },
];

// Now map over the typed array to inject the slug field without widening `type`.
export const notebooks: Notebook[] = rawNotebooks.map(n => ({
  ...n,
  slug: slugify(n.title),
}));