import React, { useState, useCallback, useEffect, useRef } from "react";
import { useMacMiniContext } from "@/context/MacMiniContext";
import { MessageData } from "@/types/PortSnapshot";

/* ------------------------------------------------------------------ */
/*  Types & helpers                                                   */
/* ------------------------------------------------------------------ */
interface PacketEvent {
  direction: "IN" | "OUT";
  type: "LIVENESS" | "2PC";
  payload: unknown;
}

const makeTrace = (ltp: number): PacketEvent[] => [
  { direction: "OUT", type: "LIVENESS", payload: {} },
  { direction: "IN", type: "LIVENESS", payload: {} },
  { direction: "OUT", type: "2PC", payload: { phase: 0, data: `DATA##LTP ${ltp}` } },
  { direction: "IN", type: "2PC", payload: { phase: 1, data: "ACK##" } },
  { direction: "OUT", type: "2PC", payload: { phase: 2, data: "ACK##" } },
];

const makeErrorTrace = (ltp: number): PacketEvent[] => [
  { direction: "OUT", type: "LIVENESS", payload: {} },
  { direction: "IN", type: "LIVENESS", payload: {} },
  { direction: "OUT", type: "2PC", payload: { phase: 0, data: `DATA##LTP ${ltp}` } },
  { direction: "IN", type: "2PC", payload: { phase: 1, data: "ACK##" } },
  { direction: "OUT", type: "2PC", payload: { phase: 2, data: "ERROR##" } },
  { direction: "IN", type: "2PC", payload: { phase: 2, data: "NACK##" } },
];

const AnalysisView: React.FC = () => {
  const { selectedMacMinis, messages, deselectMacMini } = useMacMiniContext();
  const macMini = selectedMacMinis[0];
  const message: MessageData | undefined = macMini ? messages[macMini.ip] : undefined;

  /* ------------------------------------------------------------------ */
  /*  Enforce single-selection                                          */
  /* ------------------------------------------------------------------ */
  useEffect(() => {
    if (selectedMacMinis.length > 1) {
      selectedMacMinis.slice(1).forEach(m => deselectMacMini(m.ip));
    }
  }, [selectedMacMinis, deselectMacMini]);

  /* ------------------------------------------------------------------ */
  /*  Local state                                                       */
  /* ------------------------------------------------------------------ */
  const [selectedPort, setSelectedPort] = useState<string>("");
  const [events, setEvents] = useState<PacketEvent[]>([]);
  const [tracing, setTracing] = useState(false);
  const mountRef = useRef<number>(Date.now());

  const nextLtp = useCallback(() => {
    const diffSec = (Date.now() - mountRef.current) / 1000;
    return 100 + Math.floor(diffSec * 400);
  }, []);

  const startTrace = useCallback(() => {
    if (!selectedPort) return;
    setTracing(true);
    setEvents([]);

    const seq = Array.from({ length: 6 }, (_, i) =>
      i % 2 === 0 ? makeTrace(nextLtp()) : makeErrorTrace(nextLtp())
    ).flat();

    seq.forEach((ev, idx) =>
      setTimeout(() => setEvents(prev => [...prev, ev]), idx * 300)
    );

    setTimeout(() => setTracing(false), seq.length * 300 + 200);
  }, [selectedPort, nextLtp]);

  /* Pick first port when data arrives */
  useEffect(() => {
    const ports = Object.keys(message?.port_paths ?? {});
    if (ports.length && !ports.includes(selectedPort)) {
      setSelectedPort(ports[0]);
    }
  }, [message?.port_paths, selectedPort]);

  if (!macMini) {
    return <div className="p-4 text-gray-500">Select a Mac Mini to analyse.</div>;
  }

  /* ------------------------------------------------------------------ */
  /*  Render                                                            */
  /* ------------------------------------------------------------------ */
  return (
    <div className="p-4 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-lg font-bold mb-4">
        Analysis View — {macMini.ip}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* ─────── Controls ─────── */}
        <div className="border rounded p-4">
          <h3 className="font-semibold mb-4">Port Controls</h3>

          <div className="mb-4">
            <label className="block text-sm mb-2">Select Port</label>
            <div className="daedalus-tabs-bar">
              {Object.keys(message?.port_paths ?? {}).map(pid => (
                <button
                  key={pid}
                  onClick={() => setSelectedPort(pid)}
                  className={`daedalus-tab ${selectedPort === pid ? "active" : ""}`}
                >
                  {pid}
                </button>
              ))}
            </div>
          </div>

          <button
            className="w-full bg-primary text-primary-foreground py-2 rounded disabled:opacity-50 hover:bg-primary/90 transition-colors"
            onClick={startTrace}
            disabled={!selectedPort || tracing}
          >
            {tracing ? "Tracing…" : "Start Packet Trace"}
          </button>
        </div>

        {/* ─────── Trace display ─────── */}
        <div className="border rounded p-4">
          <h3 className="font-semibold mb-4">Packet Trace</h3>
          <div className="h-[400px] overflow-y-auto bg-gray-50 p-2 rounded">
            {events.length === 0 ? (
              <p className="text-gray-500">No events yet.</p>
            ) : (
                events.map((ev, i) => (
                  <div
                    key={i}
                    className={`flex items-center p-2 mb-1 rounded border-l-4 ${ev.direction === "IN" ? "border-blue-500" : "border-green-500"
                      } bg-white shadow-sm`}
                  >
                    <span
                      className={`w-12 text-xs font-medium text-center ${ev.direction === "IN" ? "text-blue-600" : "text-green-600"
                        }`}
                    >
                      {ev.direction}
                    </span>
                    <span className="w-24 text-center text-sm font-mono border-r pr-3 mr-3">
                      {ev.type}
                    </span>
                    <pre className="text-xs overflow-x-auto">
                      {JSON.stringify(ev.payload)}
                    </pre>
                  </div>
                ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisView;
