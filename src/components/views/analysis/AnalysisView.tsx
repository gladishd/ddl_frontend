import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useMacMiniContext } from '@/context/MacMiniContext';
import { MessageData } from '@/types/PortSnapshot';

interface PacketEvent {
  direction: 'IN' | 'OUT';
  type: 'LIVENESS' | '2PC';
  payload: any;
}

// Create a function to generate a trace with increasing LTP numbers
const generateTrace = (startLtp: number): PacketEvent[] => {
  return [
    { direction: 'OUT', type: 'LIVENESS', payload: { status: 'HEALTHY' } },
    { direction: 'IN', type: 'LIVENESS', payload: { status: 'HEALTHY' } },
    { direction: 'OUT', type: '2PC', payload: { phase: 0, data: `DATA##LTP ${startLtp}` } },
    { direction: 'IN', type: '2PC', payload: { phase: 1, data: 'ACK##' } },
    { direction: 'OUT', type: '2PC', payload: { phase: 2, data: 'ACK##' } },
    { direction: 'IN', type: 'LIVENESS', payload: { status: 'HEALTHY' } },
  ];
};

// Create a function to generate a trace with error recovery
const generateErrorTrace = (startLtp: number): PacketEvent[] => {
  return [
    { direction: 'OUT', type: 'LIVENESS', payload: { status: 'HEALTHY' } },
    { direction: 'IN', type: 'LIVENESS', payload: { status: 'HEALTHY' } },
    { direction: 'OUT', type: '2PC', payload: { phase: 0, data: `DATA##LTP ${startLtp}` } },
    { direction: 'IN', type: '2PC', payload: { phase: 1, data: 'ACK##' } },
    { direction: 'OUT', type: '2PC', payload: { phase: 2, data: 'ERROR##' } },
    { direction: 'IN', type: '2PC', payload: { phase: 2, data: 'NACK##' } },
    { direction: 'OUT', type: '2PC', payload: { phase: 1, data: 'NACK##' } },
    { direction: 'IN', type: '2PC', payload: { phase: 0, data: 'NACK##' } },
  ];
};

// Pre-written packet traces
const PACKET_TRACES: PacketEvent[][] = [
  // Normal operation trace
  [
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
  ],
  [
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: '2PC', payload: {phase: 0, data: 'DATA##LTP 181'} },
    { direction: 'IN', type: '2PC', payload: {phase: 1, data: 'ACK##'} },
    { direction: 'OUT', type: '2PC', payload: {phase: 2, data: 'ACK##'} },
    { direction: 'IN', type: 'LIVENESS', payload: {phase: 3, data: 'ACK##'} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: '2PC', payload: {phase: 0, data: 'DATA##LTP 181'} },
    { direction: 'IN', type: '2PC', payload: {phase: 1, data: 'ACK##'} },
    { direction: 'OUT', type: '2PC', payload: {phase: 2, data: 'ACK##'} },
    { direction: 'IN', type: 'LIVENESS', payload: {phase: 3, data: 'ACK##'} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: '2PC', payload: {phase: 0, data: 'DATA##LTP 181'} },
    { direction: 'IN', type: '2PC', payload: {phase: 1, data: 'ACK##'} },
    { direction: 'OUT', type: '2PC', payload: {phase: 2, data: 'ACK##'} },
    { direction: 'IN', type: 'LIVENESS', payload: {phase: 3, data: 'ACK##'} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: '2PC', payload: {phase: 0, data: 'DATA##LTP 181'} },
    { direction: 'IN', type: '2PC', payload: {phase: 1, data: 'ACK##'} },
    { direction: 'OUT', type: '2PC', payload: {phase: 2, data: 'ACK##'} },
    { direction: 'IN', type: 'LIVENESS', payload: {phase: 3, data: 'ACK##'} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: '2PC', payload: {phase: 0, data: 'DATA##LTP 181'} },
    { direction: 'IN', type: '2PC', payload: {phase: 1, data: 'ACK##'} },
    { direction: 'OUT', type: '2PC', payload: {phase: 2, data: 'ACK##'} },
    { direction: 'IN', type: 'LIVENESS', payload: {phase: 3, data: 'ACK##'} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: '2PC', payload: {phase: 0, data: 'DATA##LTP 181'} },
    { direction: 'IN', type: '2PC', payload: {phase: 1, data: 'ACK##'} },
    { direction: 'OUT', type: '2PC', payload: {phase: 2, data: 'ACK##'} },
    { direction: 'IN', type: 'LIVENESS', payload: {phase: 3, data: 'ACK##'} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: '2PC', payload: {phase: 0, data: 'DATA##LTP 181'} },
    { direction: 'IN', type: '2PC', payload: {phase: 1, data: 'ACK##'} },
    { direction: 'OUT', type: '2PC', payload: {phase: 2, data: 'ACK##'} },
    { direction: 'IN', type: 'LIVENESS', payload: {phase: 3, data: 'ACK##'} },
    { direction: 'OUT', type: 'LIVENESS', payload: {} },
    { direction: 'IN', type: 'LIVENESS', payload: {} },
    { direction: 'OUT', type: '2PC', payload: {phase: 0, data: 'DATA##LTP 181'} },
  ],
];

const AnalysisView: React.FC = () => {
  const { selectedMacMinis, selectMacMini, deselectMacMini } = useMacMiniContext();
  const [message, setMessage] = useState<MessageData | null>(null);
  const [packetEvents, setPacketEvents] = useState<PacketEvent[]>([]);
  const [isTracing, setIsTracing] = useState(false);
  const [selectedPort, setSelectedPort] = useState<string | null>(null);
  const connectionRef = useRef<WebSocket | null>(null);
  const messageHandler = useRef<((event: MessageEvent) => void) | null>(null);
  const mountTimeRef = useRef(Date.now());
  const baseLtpRef = useRef(100); // Starting LTP number

  // Function to get current LTP number based on elapsed time
  const getCurrentLtp = useCallback(() => {
    const elapsedMs = Date.now() - mountTimeRef.current;
    const elapsedSeconds = elapsedMs / 1000;
    const ltpIncrement = Math.floor(elapsedSeconds * 1000); // 1000 LTPs per second
    return baseLtpRef.current + ltpIncrement;
  }, []);

  // Ensure only one Mac Mini is selected
  useEffect(() => {
    if (selectedMacMinis.length > 1) {
      // Keep only the first selected Mac Mini
      const firstMacMini = selectedMacMinis[0];
      selectedMacMinis.forEach(macMini => {
        if (macMini.ip !== firstMacMini.ip) {
          deselectMacMini(macMini.ip);
        }
      });
    }
  }, [selectedMacMinis, deselectMacMini]);

  useEffect(() => {
    const macMini = selectedMacMinis[0];
    if (!macMini?.connection) return;

    // Clean up previous connection
    if (connectionRef.current && messageHandler.current) {
      connectionRef.current.removeEventListener('message', messageHandler.current);
    }

    // Set up new connection
    const handler = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        setMessage(data);
      } catch (e) {
        console.error('Failed to parse message:', e);
      }
    };

    macMini.connection.addEventListener('message', handler);
    connectionRef.current = macMini.connection;
    messageHandler.current = handler;

    return () => {
      if (connectionRef.current && messageHandler.current) {
        connectionRef.current.removeEventListener('message', messageHandler.current);
      }
    };
  }, [selectedMacMinis]);

  const startPacketTrace = useCallback(() => {
    if (!selectedPort) return;
    
    setIsTracing(true);
    setPacketEvents([]);
    
    // Generate 5 traces alternating between normal and error scenarios
    const traces = Array.from({ length: 5 }, (_, index) => {
      const currentLtp = getCurrentLtp();
      const trace = index % 2 === 0 
        ? generateTrace(currentLtp)
        : generateErrorTrace(currentLtp);
      return trace;
    });
    
    // Simulate packet trace events with delays
    traces.forEach((trace, index) => {
      setTimeout(() => {
        setPacketEvents(prev => [...prev, ...trace]);
      }, index * 1000); // Add each trace with a 1-second delay
    });

    // Reset tracing state after all traces are shown
    setTimeout(() => {
      setIsTracing(false);
    }, traces.length * 1000);
  }, [selectedPort, getCurrentLtp]);

  const injectFailure = useCallback((source: string, target: string) => {
    if (!connectionRef.current) return;
    
    // Send inject failure command
    connectionRef.current.send(JSON.stringify({
      command: 'inject_failure',
      source,
      target
    }));
  }, []);

  if (!selectedMacMinis.length) {
    return (
      <div className="p-4">
        <p>Please select a Mac Mini to analyze</p>
      </div>
    );
  }

  const macMini = selectedMacMinis[0];

  return (
    <div className="p-4 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-lg font-bold mb-4">Analysis View - {macMini.ip}</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Port Selection and Controls */}
        <div className="border rounded p-4">
          <h3 className="text-md font-semibold mb-4">Port Controls</h3>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Select Port</label>
            <select 
              className="w-full p-2 border rounded"
              value={selectedPort || ''}
              onChange={(e) => setSelectedPort(e.target.value)}
            >
              <option value="">Select a port...</option>
              {message?.port_paths && Object.keys(message.port_paths).map(portId => (
                <option key={portId} value={portId}>{portId}</option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <button
              className="w-full bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
              onClick={startPacketTrace}
              disabled={!selectedPort || isTracing}
            >
              {isTracing ? 'Tracing...' : 'Start Packet Trace'}
            </button>
          </div>
        </div>

        {/* Packet Trace Display */}
        <div className="border rounded p-4">
          <h3 className="text-md font-semibold mb-4">Packet Trace</h3>
          <div className="h-[400px] overflow-y-auto bg-gray-50 p-2 rounded">
            {packetEvents.length === 0 ? (
              <p className="text-gray-500">No packet events recorded yet</p>
            ) : (
              <div className="flex flex-col space-y-2">
                {packetEvents.map((event, index) => (
                  <div key={index} className={`bg-white p-2 rounded shadow-sm border-l-4 ${
                    event.direction === 'IN' ? 'border-blue-500' : 'border-green-500'
                  } flex items-center`}>
                    <div className={`text-xs font-medium w-12 text-center ${
                      event.direction === 'IN' ? 'text-blue-500' : 'text-green-500'
                    }`}>
                      {event.direction}
                    </div>
                    <div className="font-mono text-sm w-24 text-center border-r border-gray-200 pr-4">
                      {event.type}
                    </div>
                    <pre className="text-xs bg-gray-50 p-1 rounded flex-1 overflow-x-auto ml-4">
                      {JSON.stringify(event.payload, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Port Graph with Failure Injection */}
        {message?.port_paths && selectedPort && (
          <div className="border rounded p-4 md:col-span-2">
            <h3 className="text-md font-semibold mb-4">Port Graph - {selectedPort}</h3>
            <div className="h-[400px] bg-white rounded relative">
              {/* Add your graph visualization here */}
              <div className="absolute inset-0">
                {/* Graph component will go here */}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisView; 