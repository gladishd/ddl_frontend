import { PortSnapshot } from "@/types/PortSnapshot";
import { ChevronDown, ChevronRight, Network, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";
import { HoveredPortInfo } from "@/types/HoveredPort";

const PortStatus = ({ port, snapshot, hoveredPortInfo }: { port: string; snapshot: PortSnapshot; hoveredPortInfo: HoveredPortInfo | null }) => {
    const [expanded, setExpanded] = useState(false);
    const isConnected = snapshot.link.status === 'connected';
    const [isHighlighted, setIsHighlighted] = useState(false);

    useEffect(() => {
        setIsHighlighted(hoveredPortInfo?.neighborPortId === snapshot.name || hoveredPortInfo?.portId === snapshot.name);
    }, [hoveredPortInfo, snapshot.name]);

    return (
      // The display of each port interface reflects a Local Observer View (LOV),
      // showing its immediate connection status and statistics.
      <div className={`mb-2 border rounded-lg p-2 transition-all duration-200 ${isHighlighted ? 'bg-blue-50 border-blue-200 shadow-md' : 'bg-white'}`}>
        <div
          className="flex items-center cursor-pointer"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? <ChevronDown size={16} className="flex-shrink-0" /> : <ChevronRight size={16} className="flex-shrink-0" />}
          <span className="font-medium ml-1">{port}</span>
          <span className="ml-2 text-xs text-muted-foreground">({snapshot.name})</span>
          <div className="ml-auto flex items-center">
            {isConnected ? (
              <div className="flex items-center text-green-600">
                <Network size={16} className="mr-1" />
                <span className="text-xs font-semibold">Connected</span>
              </div>
            ) : (
              <div className="flex items-center text-red-500">
                <WifiOff size={16} className="mr-1" />
                  <span className="text-xs font-semibold">Disconnected</span>
              </div>
            )}
          </div>
        </div>

        {expanded && (
          // This expanded view provides a deeper look into the port's substructure,
          // revealing connection details and statistics necessary for precise system analysis.
          <div className="tree-expansion-panel">
            <div className="tree-expansion-header">Protocol: {snapshot.link.protocol}</div>

            {isConnected && snapshot.connection && (
              <div className="mt-2">
                <div className="tree-expansion-header">Connection Details:</div>
                <div className="tree-expansion-content">
                  {snapshot.connection.local_address && (
                    <div>Local: {snapshot.connection.local_address}</div>
                  )}
                  {snapshot.connection.neighbor_address && (
                    <div>Neighbor: {snapshot.connection.neighbor_address}</div>
                  )}
                  <div>Role: {snapshot.connection.is_client !== undefined
                    ? (snapshot.connection.is_client ? 'Client' : 'Server')
                    : 'Unknown'}</div>
                  {snapshot.connection.neighbor_portid && (
                    <div>Neighbor Port ID: {snapshot.connection.neighbor_portid}</div>
                  )}
                </div>
              </div>
            )}

            {snapshot.link.statistics && Object.keys(snapshot.link.statistics).length > 0 && (
              <div className="mt-2">
                <div className="tree-expansion-header">Statistics:</div>
                <div className="tree-expansion-content grid grid-cols-2 gap-x-4 gap-y-1">
                  {Object.entries(snapshot.link.statistics).map(([key, value]) => (
                    <div key={key} className="truncate"><span className="font-medium">{key}:</span> {value}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
};

export default PortStatus;