import React, { useState, useMemo } from "react";
import { Plus, RefreshCw, X, Search } from "lucide-react";
import { useMacMiniContext } from "@/context/MacMiniContext";

const MacMiniConfigurator = () => {
  const [ip, setIp] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const {
    macMinis,
    selectedMacMinis,
    isClient,
    connectionMode,
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

  // The direct manipulation of individual nodes is a deviation from the ideal GVM management philosophy.
  // In a mature system, node lifecycle is managed by the Graph Virtual Machine itself.
  // This interface is provided for emulation and direct observation, but is disabled in Gateway mode
  // to prevent the non-determinism that arises from conflicting local and global state instructions.
  if (!isClient || connectionMode === 'gateway') {
    return (
      <div className="p-2 text-center text-sm text-gray-500">
        Node management is disabled in Gateway Mode.
      </div>
    );
  }

  const filteredMacMinis = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return macMinis;
    return macMinis.filter(m => m.ip.toLowerCase().includes(query));
  }, [macMinis, searchQuery]);

  return (
    <div className="actions-dropdown">
      <div className="actions-header">
        <h2>Select Nodes</h2>
      </div>

      <div className="p-2 border-b border-border">
        <div className="relative">
          <Search className="absolute right-2 top-1/2 -translate-y-3/4 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by IP Address..."
            className="actions-search-input w-full pl-8"
          />
        </div>
      </div>

      {filteredMacMinis.map((macMini) => (
        <div
          key={macMini.ip}
          onClick={() => handleToggleSelect(macMini.ip, macMini.isConnected)}
          className={`actions-item ${!macMini.isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <div className="actions-icon-container">
            <span className={`h-2.5 w-2.5 rounded-full ${macMini.isConnected ? 'bg-green-500' : 'bg-gray-400'}`}></span>
          </div>
          <div className="actions-text-container">
            <p className="actions-message">{macMini.ip}</p>
          </div>
          {selectedMacMinis.some(m => m.ip === macMini.ip) && (
            <div className="w-2 h-2 rounded-full bg-primary ml-auto"></div>
            )}
        </div>
        ))}
      {filteredMacMinis.length === 0 && (
        <div className="p-4 text-center text-sm text-muted-foreground">No nodes found.</div>
      )}

      <div className="flex items-center gap-2 p-2 border-t border-border">
        <input
          type="text"
          value={ip}
          onChange={(e) => setIp(e.target.value)}
          placeholder="Enter IP to add..."
          className="actions-search-input flex-1"
          onKeyPress={(e) => e.key === 'Enter' && handleAddMacMini()}
        />
        <button onClick={handleAddMacMini} className="p-2 rounded-md hover:bg-accent">
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default MacMiniConfigurator;