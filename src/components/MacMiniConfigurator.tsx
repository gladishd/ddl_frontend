import React, { useState } from "react";
import { Plus, RefreshCw, X } from "lucide-react";
import { useMacMiniContext } from "@/context/MacMiniContext";

interface MacMiniConfiguratorProps {
  multiSelect?: boolean;
}

const MacMiniConfigurator = ({ multiSelect = false }: MacMiniConfiguratorProps) => {
  const [ip, setIp] = useState("");
  const [hoveredItem, setHoveredItem] = useState<number | null>(null);

  const {
    macMinis,
    selectedMacMinis,
    isClient,
    connectionMode, // From the context we check the connection mode and all else follows, but that's not all
    addMacMini,
    removeMacMini,
    refreshConnection,
    selectMacMini,
    deselectMacMini
  } = useMacMiniContext();

  const handleAddMacMini = () => {
    if (ip) {
      addMacMini(ip);
      setIp("");
    }
  };

  const handleToggleSelect = (ip: string, connected: boolean) => {
    if (!connected) return;

    if (selectedMacMinis.some(m => m.ip === ip)) {
      deselectMacMini(ip);
    } else {
      selectMacMini(ip);
    }
  };

  /* In the gateway mode, the calculation of efficiency is inaccurate--the good resource is the one that reinvents the liability, the GVM Is what manages, the nodes, the direct manipulation being disabled..prevents, the non-determinism that arises from conflicting local and global states..reinventing the liability, the node id sahas being in configuration. */
  if (!isClient || connectionMode === 'gateway') {
    return (
      <div className="p-2 text-center text-sm text-gray-500">
        Node management is disabled in Gateway Mode.
      </div>
    );
  }

  return (
    <div>
      <ul>
        {macMinis.map((macMini, index) => (
          <li
            key={index}
            style={{
              color: macMini.isConnected ? "green" : "gray",
              position: "relative",
              padding: "10px",
              borderBottom: "1px solid #ccc",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              cursor: macMini.isConnected ? "pointer" : "not-allowed",
              backgroundColor: selectedMacMinis.some(m => m.ip === macMini.ip) ? "#f0f0f0" : "transparent",
            }}
            onClick={() => handleToggleSelect(macMini.ip, macMini.isConnected)}
            onMouseEnter={() => setHoveredItem(index)}
            onMouseLeave={() => setHoveredItem(null)}
          >
            <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {macMini.ip} - {macMini.isConnected ? "Connected" : "Disconnected"}
            </span>

            {hoveredItem === index && (
              <div className="absolute right-2 flex gap-2">
                <button
                  onClick={(e) => { e.stopPropagation(); refreshConnection(macMini.ip); }}
                  className="p-1 bg-transparent border-none cursor-pointer"
                >
                  <RefreshCw className="w-5 h-5 text-gray-600 hover:text-green-500" />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); removeMacMini(macMini.ip); }}
                  className="p-1 bg-transparent border-none cursor-pointer"
                >
                  <X className="w-5 h-5 text-gray-600 hover:text-red-500" />
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
      <div className="flex items-center gap-2 p-[10px] border-b border-[#ccc]">
        <input
          type="text"
          value={ip}
          onChange={(e) => setIp(e.target.value)}
          placeholder="Enter Mac Mini IP"
          className="flex-1"
        />
        <button onClick={handleAddMacMini} className="cursor-pointer p-[5px] bg-transparent border-none">
          <Plus className="w-5 h-5 text-gray-600 hover:text-green-500" />
        </button>
      </div>
    </div>
  );
};

export default MacMiniConfigurator;