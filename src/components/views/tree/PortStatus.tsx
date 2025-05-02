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
    }, [hoveredPortInfo]);
    
    return (
      <div className={`mb-3 border rounded p-2 ${isHighlighted ? 'bg-blue-50 border-blue-200' : ''}`}>
        <div 
          className="flex items-center cursor-pointer" 
          onClick={() => setExpanded(!expanded)}
        >
          {isConnected && (expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />)}
          <span className="font-medium ml-1">{port}</span>
          <span className="ml-2 text-xs">({snapshot.name})</span>
          <div className="ml-auto flex items-center">
            {isConnected ? (
              <div className="flex items-center text-green-600">
                <Network size={16} className="mr-1" />
                <span className="text-xs">Connected</span>
              </div>
            ) : (
              <div className="flex items-center text-red-500">
                <WifiOff size={16} className="mr-1" />
                <span className="text-xs">Disconnected</span>
              </div>
            )}
          </div>
        </div>
        
        {expanded && (
          <div className="mt-2 ml-6 text-xs">
            <div className="font-medium">Protocol: {snapshot.link.protocol}</div>
            
            {isConnected && snapshot.connection && (
              <div className="mt-1 bg-gray-50 p-2 rounded">
                <div className="font-medium">Connection Details:</div>
                {snapshot.connection.local_address && (
                  <div className="ml-2">Local: {snapshot.connection.local_address}</div>
                )}
                {snapshot.connection.neighbor_address && (
                  <div className="ml-2">Neighbor: {snapshot.connection.neighbor_address}</div>
                )}
                <div className="ml-2">Role: {snapshot.connection.is_client !== undefined 
                  ? (snapshot.connection.is_client ? 'Client' : 'Server') 
                  : 'Unknown'}</div>
                {snapshot.connection.neighbor_portid && (
                  <div className="ml-2">Neighbor Port ID: {snapshot.connection.neighbor_portid}</div>
                )}
              </div>
            )}
            
            {snapshot.link.statistics && Object.keys(snapshot.link.statistics).length > 0 && (
              <div className="mt-1">
                <div className="font-medium">Statistics:</div>
                <div className="grid grid-cols-2 gap-1 ml-2">
                  {Object.entries(snapshot.link.statistics).map(([key, value]) => (
                    <div key={key}>{key}: {value}</div>
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