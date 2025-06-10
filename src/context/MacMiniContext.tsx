"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useMemo,
  ReactNode,
} from "react";

import { MacMini } from "@/types/MacMini";
import {
  MessageData,
  PortSnapshot,
  ConnectionDetails,
  TreeNodeData,
  PortPath,
  Edge,
} from "@/types/PortSnapshot";

/*
─────────────────────────────────────────────────────────────────────────────
 Demo‑mode Network Generator 2.0
─────────────────────────────────────────────────────────────────────────────
This version spins up eight imaginary Mac‑Minis, each with 2‑5 interfaces
(en0‑en4, bridge0, eth0).  Every 2 s it refreshes statistics, randomly drops
/ restores links, shuffles peerings, and tweaks tree & DAG structures so all
four views (Tree, Raw, DAG, Analysis) stay lively.
*/

export type ViewType = "tree" | "raw" | "dag" | "analysis";

interface MacMiniContextState {
  macMinis: MacMini[];
  selectedMacMiniIps: string[];
  selectedMacMinis: MacMini[];
  messages: Record<string, MessageData>;
  activeView: ViewType;
  isClient: boolean;
  setActiveView: (v: ViewType) => void;
  selectMacMini: (ip: string) => void;
  deselectMacMini: (ip: string) => void;
}

const Ctx = createContext<MacMiniContextState>({} as MacMiniContextState);

interface ProviderProps { children: ReactNode }

// ─── Constants ────────────────────────────────────────────────────────────
const IPS = Array.from({ length: 8 }, (_, i) => `192.168.1.1${(i + 1).toString().padStart(2, "0")}`);
const PORTS = ["en0", "en1", "en2", "en3", "en4", "bridge0", "eth0"];
const PROTOCOLS = ["ethernet", "wifi", "thunderbolt"];

const rnd = (max: number) => Math.floor(Math.random() * max);
const sample = <T,>(arr: T[]) => arr[rnd(arr.length)];

// ─── Generators ───────────────────────────────────────────────────────────
const genStats = (): Record<string, number> => ({
  rx_bytes: rnd(50_000),
  tx_bytes: rnd(50_000),
  errors: rnd(20),
  dropped: rnd(10),
});

const genSnapshot = (selfIp: string, portName: string): PortSnapshot => {
  const connected = Math.random() > 0.15; // 85 % chance up
  let connection: ConnectionDetails | undefined = undefined;
  if (connected) {
    const peerIp = sample(IPS.filter((ip) => ip !== selfIp));
    const peerPort = sample(PORTS);
    connection = {
      local_address: `${selfIp}%${portName}`,
      neighbor_address: `${peerIp}%${peerPort}`,
      neighbor_portid: peerPort,
      is_client: Math.random() > 0.5,
    };
  }
  return {
    name: portName,
    connection,
    link: {
      protocol: sample(PROTOCOLS),
      status: connected ? "connected" : "disconnected",
      statistics: connected ? genStats() : undefined,
    },
  };
};

const genSnapshots = (ip: string): Record<string, PortSnapshot> => {
  const howMany = 2 + rnd(4); // 2‑5 ports
  const chosen = [...PORTS].sort(() => 0.5 - Math.random()).slice(0, howMany);
  return Object.fromEntries(chosen.map((p) => [p, genSnapshot(ip, p)]));
};

const genTrees = (ip: string): Record<string, TreeNodeData> => {
  const entries = 1 + rnd(3); // 1‑3 tree nodes
  const targets = [...IPS.filter((i) => i !== ip)].sort(() => 0.5 - Math.random()).slice(0, entries);
  return Object.fromEntries(
    targets.map((t) => [t, {
      rootward_portid: sample(PORTS),
      hops: 1 + rnd(3),
      tree_instance_id: crypto.randomUUID?.() ?? Math.random().toString(16).slice(2),
    }])
  );
};

const genPortPathForPort = (selfId: string): PortPath => {
  const length = 3 + rnd(3); // 3‑5 nodes
  const nodes: string[] = [selfId];
  for (let i = 1; i < length; i++) {
    const ip = sample(IPS);
    const port = sample(PORTS);
    nodes.push(`${ip.replace(/\./g, "-")}:${port}`);
  }
  const edges: Edge[] = nodes.slice(1).map((n, idx) => ({ source: nodes[idx], target: n }));
  return { nodes, edges };
};

const genPortPaths = (ip: string, portNames: string[]): Record<string, PortPath> => {
  return Object.fromEntries(
    portNames.map((p) => {
      const selfId = `${ip.replace(/\./g, "-")}:${p}`;
      return [p, genPortPathForPort(selfId)];
    })
  );
};

const genMessage = (ip: string): MessageData => {
  const snapshots = genSnapshots(ip);
  const ports = Object.keys(snapshots);
  return {
    type: "snapshot",
    node_id: `${ip.replace(/\./g, "-")}:bridge0`,
    snapshots,
    trees_dict: genTrees(ip),
    port_paths: genPortPaths(ip, ports),
  };
};

// ─── Provider ─────────────────────────────────────────────────────────────
export function MacMiniProvider({ children }: ProviderProps) {
  const [macMinis, setMacMinis] = useState<MacMini[]>([]);
  const [selectedIps, setSelectedIps] = useState<string[]>([]);
  const [messages, setMessages] = useState<Record<string, MessageData>>({});
  const [activeView, setActiveView] = useState<ViewType>("tree");
  const [isClient, setIsClient] = useState(false);

  // Initial load
  useEffect(() => {
    setIsClient(true);
    const minis = IPS.map((ip) => ({ ip, name: `mac-mini@${ip}`, isConnected: true }));
    setMacMinis(minis);
    setSelectedIps([minis[0].ip]);
    const seed: Record<string, MessageData> = {};
    minis.forEach((m) => (seed[m.ip] = genMessage(m.ip)));
    setMessages(seed);
  }, []);

  // Live mutation every 2 s
  useEffect(() => {
    if (!isClient) return;
    const id = setInterval(() => {
      setMessages((prev) => {
        const next: typeof prev = {};
        Object.keys(prev).forEach((ip) => (next[ip] = genMessage(ip)));
        return next;
      });
    }, 2_000);
    return () => clearInterval(id);
  }, [isClient]);

  const selected = useMemo(
    () => selectedIps.map((ip) => macMinis.find((m) => m.ip === ip)).filter(Boolean) as MacMini[],
    [macMinis, selectedIps]
  );

  const selectMacMini = (ip: string) => setSelectedIps((p) => (p.includes(ip) ? p : [...p, ip]));
  const deselectMacMini = (ip: string) => setSelectedIps((p) => p.filter((x) => x !== ip));

  const value: MacMiniContextState = {
    macMinis,
    selectedMacMiniIps: selectedIps,
    selectedMacMinis: selected,
    messages,
    activeView,
    isClient,
    setActiveView,
    selectMacMini,
    deselectMacMini,
  };

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export const useMacMiniContext = () => useContext(Ctx);
