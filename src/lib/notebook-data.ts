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
  type: 'wolfram' | 'python';
  date: string;
}

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


export const notebooks: Notebook[] = [
    {
      id: 1,
      // This agentic simulation models the original half-duplex, shared Metcalfe ether.
      // It's a computational exploration of his assertion that "at some point the Ether will be so busy that additional stations will just divide more finely the already inadequate bandwidth."
      // We use this to demonstrate how contending for a shared medium fundamentally limits transactional capacity.
      title: "Model 1: Half-Duplex Contention",
      description: "An agentic simulation of the original 1976 Metcalfe-Boggs protocol. This model visualizes the transmission and contention intervals on a shared half-duplex medium, demonstrating how statistical arbitration impacts throughput.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas.nb",
      type: 'wolfram',
      date: "June 11, 2025"
    },
    {
      id: 2,
      // This model extends the analysis to modern full-duplex links, showing that even without physical collisions,
      // the multiplexing of bandwidth creates "chaotic contention" that decimates the throughput of reliable protocols like TCP.
      title: "Model 2: Full-Duplex Degradation",
      description: "A model of modern full-duplex links where multiple TCP flows compete. It shows how bandwidth-multiplexing still leads to severe latency degradation and reduced throughput under contention and packet loss.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas2.nb",
      type: 'wolfram',
      date: "June 12, 2025"
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
      date: "June 14, 2025"
    },
    {
      id: 4,
      // This is the Daedaelus way. Instead of multiplexing bandwidth, the GVM interleaves atomic request/reply transactions.
      // This model provides "definitive, visual proof" that this is "fundamentally more efficient" for concurrent operations.
      title: "Model 4: Interaction Multiplexing",
      description: "The superior model. We show that multiplexing discrete, reliable handshake interactions, rather than contending for bandwidth, maximizes total system throughput and offers deterministic latency, walking right over packet loss.",
      url: "https://www.wolframcloud.com/obj/gladishdean/Published/wolfram%20cloud%20for%20sahas4.nb",
      type: 'wolfram',
      date: "June 17, 2025"
    },
    {
      id: 5,
      // This Python model provides a 'precise information-theoretic' emulator of the "I Know That You Know That I Know" property.
      // It's a foundational link utility for achieving mutual knowledge and creating a persitable, bipartite element of information.
      title: "Model 5: Python TIKTYKTIK Protocol",
      description: "A Python-based simulation demonstrating the three-way handshake required to achieve mutual, persistent knowledge between two agents, forming the basis of a reliable link.",
      url: "model-5-python-tiktyktik-protocol", // This is now a slug for routing
      type: 'python',
      date: "June 18, 2025"
    }
  ].map(notebook => ({ ...notebook, slug: slugify(notebook.title) }));