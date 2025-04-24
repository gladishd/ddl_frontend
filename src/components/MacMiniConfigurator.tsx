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

  if (!isClient) {
    return null;
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
            <span style={{ 
              flex: 1,
              overflow: hoveredItem === index ? "hidden" : "visible",
              textOverflow: hoveredItem === index ? "ellipsis" : "clip",
              whiteSpace: hoveredItem === index ? "nowrap" : "normal",
              paddingRight: hoveredItem === index ? "80px" : "0"
            }}>
              {macMini.ip} - {macMini.isConnected ? "Connected" : "Disconnected"}
            </span>
            
            {hoveredItem === index && (
              <div
                style={{
                  position: "absolute",
                  right: "10px",
                  display: "flex",
                  gap: "10px",
                }}
              >
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    refreshConnection(macMini.ip);
                  }}
                  style={{
                    cursor: "pointer",
                    padding: "5px",
                    background: "transparent",
                    border: "none",
                  }}
                >
                  <RefreshCw className="w-5 h-5 text-gray-600 hover:text-green-500" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeMacMini(macMini.ip);
                  }}
                  style={{
                    cursor: "pointer",
                    padding: "5px",
                    background: "transparent",
                    border: "none",
                  }}
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
        <button 
          onClick={handleAddMacMini}
          className="cursor-pointer p-[5px] bg-transparent border-none"
        >
          <Plus className="w-5 h-5 text-gray-600 hover:text-green-500" />
        </button>
      </div>
    </div>
  );
};

export default MacMiniConfigurator;
