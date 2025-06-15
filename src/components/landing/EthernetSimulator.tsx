"use client";

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import dynamic from 'next/dynamic';

// This component implements the core logic for the agent-based Ethernet simulation.
// We use a force-directed graph to represent the stations (nodes) and the shared Ether.
// This provides an interactive canvas to visualize the distributed statistical arbitration in real-time.

// --- Type Definitions ---
interface StationNode {
  id: string;
  name: string;
  fx?: number; // Fixed x-position for layout
  fy?: number; // Fixed y-position for layout
  // Daedaelus-specific state for simulation
  packetQueue: number;
  backoff: number;
  collisions: number;
  state: 'idle' | 'deferring' | 'transmitting' | 'collided' | 'waiting';
}

interface EtherLink {
  source: string;
  target: string;
  state: 'idle' | 'transmission' | 'collision';
}

interface GraphData {
  nodes: StationNode[];
  links: EtherLink[];
}

// --- Dynamic Import for Client-Side Graph Library ---
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => <div className="graph-loading-placeholder">Loading Simulation Canvas…</div>,
});


// --- Simulation Constants ---
const SLOT_TIME = 51.2; // Corresponds to 512 bit-times on a 10Mbps Ether, a critical parameter for collision detection.

const EthernetSimulator = ({ numStations, packetLength, isSimulating }: { numStations: number; packetLength: number; isSimulating: boolean; }) => {
  const fgRef = useRef<any>();
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [metrics, setMetrics] = useState({ successfulPackets: 0, totalCollisions: 0, time: 0 });

  // --- Graph & Simulation Initialization ---
  useEffect(() => {
    // We model the Ether as a central, invisible hub. Stations are distributed radially.
    // This is a visual abstraction of the broadcast medium, not a physical star topology.
    // It helps visualize contention for the single, shared resource.
    const r = 150; // Radius for distributing station nodes
    const initialNodes: StationNode[] = [
      // The central node representing the passive, shared Ether.
      { id: 'ether', name: 'Ether', fx: 0, fy: 0, packetQueue: 0, backoff: 0, collisions: 0, state: 'idle' }
    ];
    for (let i = 0; i < numStations; i++) {
      const angle = (i / numStations) * 2 * Math.PI;
      initialNodes.push({
        id: `st-${i}`,
        name: `Station ${i}`,
        fx: r * Math.cos(angle),
        fy: r * Math.sin(angle),
        packetQueue: 1,
        backoff: 0,
        collisions: 0,
        state: 'idle',
      });
    }
    setGraphData({ nodes: initialNodes, links: [] });
    setMetrics({ successfulPackets: 0, totalCollisions: 0, time: 0 });
  }, [numStations]);

  // --- Core Simulation Step ---
  const simulationStep = useCallback(() => {
    setGraphData(prevData => {
      const stations = prevData.nodes.filter(n => n.id !== 'ether');
      const transmittingNow: StationNode[] = [];

      // Phase 1: Determine station actions (transmit or wait)
      stations.forEach(station => {
        if (station.backoff > 0) {
          station.backoff = Math.max(0, station.backoff - SLOT_TIME);
          station.state = 'waiting';
        }
        if (station.packetQueue > 0 && station.backoff === 0) {
          // Carrier Sense: Check if any link is currently active
          if (prevData.links.some(l => l.state !== 'idle')) {
            station.state = 'deferring';
          } else {
            transmittingNow.push(station);
          }
        }
      });

      let newLinks: EtherLink[] = [];
      // Phase 2: Resolve contention and update Ether state
      if (transmittingNow.length > 1) { // Collision
        newLinks = transmittingNow.map(s => ({ source: s.id, target: 'ether', state: 'collision' }));
        transmittingNow.forEach(station => {
          station.state = 'collided';
          station.collisions += 1;
          // Binary Exponential Backoff: A distributed statistical arbitration mechanism.
          const maxSlots = Math.pow(2, Math.min(station.collisions, 10)) - 1;
          station.backoff = Math.floor(Math.random() * (maxSlots + 1)) * SLOT_TIME;
        });
        setMetrics(m => ({ ...m, totalCollisions: m.totalCollisions + transmittingNow.length }));

      } else if (transmittingNow.length === 1) { // Successful Transmission
        const station = transmittingNow[0];
        station.state = 'transmitting';
        station.packetQueue = 0;
        station.collisions = 0; // Reset on success
        newLinks = [{ source: station.id, target: 'ether', state: 'transmission' }];
        setMetrics(m => ({ ...m, successfulPackets: m.successfulPackets + 1 }));
      }

      // Update time and return new state
      setMetrics(m => ({ ...m, time: m.time + SLOT_TIME }));
      return { nodes: [prevData.nodes[0], ...stations], links: newLinks };
    });
  }, []);

  // --- Simulation Loop Control ---
  useEffect(() => {
    if (!isSimulating) return;
    const timer = setInterval(simulationStep, 200); // Step every 200ms
    return () => clearInterval(timer);
  }, [isSimulating, simulationStep]);

  // --- Node Visualization ---
  const nodeCanvasObject = useCallback((node: any, ctx: CanvasRenderingContext2D) => {
    if (node.id === 'ether') return; // Do not draw the central ether node

    const r = 6;
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);

    // Node color reflects the station's state in the GVM
    const colorMap = {
      idle: '#6b7280',       // Gray
      deferring: '#f59e0b',  // Amber
      waiting: '#3b82f6',     // Blue
      transmitting: '#22c55e',// Green
      collided: '#ef4444',    // Red
    };
    ctx.fillStyle = colorMap[node.state as keyof typeof colorMap] || '#6b7280';
    ctx.fill();

    // Label
    ctx.font = '5px Raleway';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#111827';
    ctx.fillText(node.name, node.x, node.y + r + 5);
  }, []);

  return (
    <div className="w-full h-full relative">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeCanvasObject={nodeCanvasObject}
        linkWidth={1.5}
        linkColor={link => link.state === 'collision' ? '#ef4444' : '#22c55e'}
        linkLineDash={link => link.state === 'collision' ? [2, 1] : []}
        linkDirectionalParticles={link => link.state === 'transmission' ? 2 : 0}
        linkDirectionalParticleWidth={2}
        cooldownTicks={0}
        enablePanInteraction={true}
        enableZoomInteraction={true}
      />
      <div className="simulation-metrics-overlay">
        <div>Efficiency: <span>{((metrics.successfulPackets * packetLength) / metrics.time * 100).toFixed(2) || '0.00'}%</span></div>
        <div>Collisions: <span>{metrics.totalCollisions}</span></div>
        <div>Time (slots): <span>{(metrics.time / SLOT_TIME).toFixed(0)}</span></div>
      </div>
    </div>
  );
};

export default EthernetSimulator;