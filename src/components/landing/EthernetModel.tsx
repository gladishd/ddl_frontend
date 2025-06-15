"use client";

import React, { useState, useMemo, useCallback } from 'react';
import SimulationControls from './SimulationControls';
import EthernetSimulator from './EthernetSimulator';

// This component encapsulates the agent-based Ethernet simulation.
// We are not merely presenting statistical analysis; we are creating a 'precise information-theoretic' emulator.
// This allows for competitive interactions between agents on the Ether, demonstrating the fundamental consequences
// of a design where bandwidth is a contended resource rather than a guaranteed one.
const EthernetModel = () => {
  // State for simulation parameters, controlled by the user.
  const [numStations, setNumStations] = useState(10);
  const [packetLength, setPacketLength] = useState(512); // P, in bits
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationKey, setSimulationKey] = useState(Date.now()); // Used to reset the simulation

  // This callback resets the simulation by changing the key of the simulator component, forcing a remount.
  // This is a clean, 'time-reversible' way to restart the state without complex manual state clearing.
  const resetSimulation = useCallback(() => {
    setIsSimulating(false);
    setSimulationKey(Date.now());
  }, []);

  return (
    <section className="ethernet-model-section">
      <div className="container mx-auto">
        <header className="text-center mb-12">
          <h2 className="text-4xl font-bold">Agentic Ethernet Contention Model</h2>
          {/*
                        This is not a statistical model but a computational one, built to expose the root assumption of early Ethernet.
                        As Metcalfe noted, "At some point the Ether will be so busy that additional stations will just divide more finely the already inadequate bandwidth."
                        This simulation reveals the consequences of that division.
                    */}
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto mt-4">
            An agent-based simulation of the 1976 Metcalfe-Boggs half-duplex protocol. This is not a statistical analysis; it is a computational model where each station acts as an autonomous agent contending for the Ether. Observe how statistical arbitration and collision handling directly impact the transactional capacity of the network.
          </p>
        </header>
        <div className="ethernet-model-layout">
          <div className="simulation-controls-container">
            <SimulationControls
              numStations={numStations}
              setNumStations={setNumStations}
              packetLength={packetLength}
              setPacketLength={setPacketLength}
              isSimulating={isSimulating}
              setIsSimulating={setIsSimulating}
              resetSimulation={resetSimulation}
            />
          </div>
          <div className="ethernet-simulator-container">
            <EthernetSimulator
              key={simulationKey}
              numStations={numStations}
              packetLength={packetLength}
              isSimulating={isSimulating}
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default EthernetModel;