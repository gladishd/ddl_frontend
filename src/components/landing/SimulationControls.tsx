import React from 'react';

// This interface defines the explicit types for the component's props,
// ensuring type safety and preventing the 'implicit any' error.
// It is a precise specification for the control plane of our emulator.
interface SimulationControlsProps {
  numStations: number;
  setNumStations: (value: number) => void;
  packetLength: number;
  setPacketLength: (value: number) => void;
  isSimulating: boolean;
  setIsSimulating: (value: boolean) => void;
  resetSimulation: () => void;
}

// This component provides the control plane for the Ethernet emulator.
// It allows for the dynamic adjustment of key parameters like the number of contending stations (Q)
// and packet size (P), which are critical variables in Metcalfe's original performance model.
const SimulationControls: React.FC<SimulationControlsProps> = ({
    numStations, setNumStations,
    packetLength, setPacketLength,
    isSimulating, setIsSimulating,
    resetSimulation
}) => {
    return (
        <div className="simulation-controls">
            <h4 className="controls-title">Simulation Parameters</h4>
            <div className="control-group">
                <label htmlFor="numStations">Stations (Q): {numStations}</label>
                <input
                    type="range"
                    id="numStations"
                    min="2"
                    max="50"
                    value={numStations}
                    onChange={(e) => setNumStations(Number(e.target.value))}
                    disabled={isSimulating}
                />
            </div>
            <div className="control-group">
                <label htmlFor="packetLength">Packet Length (P): {packetLength} bits</label>
                <input
                    type="range"
                    id="packetLength"
                    min="64"
                    max="4096"
                    step="64"
                    value={packetLength}
                    onChange={(e) => setPacketLength(Number(e.target.value))}
                    disabled={isSimulating}
                />
            </div>
            <div className="control-buttons">
                <button onClick={() => setIsSimulating(!isSimulating)}>
                    {isSimulating ? 'Pause' : 'Start'}
                </button>
                <button onClick={resetSimulation}>Reset</button>
            </div>
        </div>
    );
};

export default SimulationControls;