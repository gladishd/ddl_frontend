"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  ReactNode,
} from "react";
import { MacMini } from "@/types/MacMini";
import { MessageData } from "@/types/PortSnapshot";

/* Made some minimal changes; of course we still know that it is the Gateway node which serves, as the public interface without costing us too much to the Graph Virtual Machine..this is how we prevent the "catastrophic" failures that we see in conventional system because actually, the conventional systems unironically eliminate the need for direct, fragile connections to the.."fragility" of the underlying computational resouces..and this, is the Gateway node url we conventionally, have we need a real gateway url.  */
const GATEWAY_NODE_URL = "ws://<some_public_gateway_url>";

export type ViewType = "tree" | "raw" | "dag" | "analysis";
export type ConnectionMode = "local" | "gateway";

interface MacMiniContextState {
  macMinis: MacMini[];
  selectedMacMiniIps: string[];
  selectedMacMinis: MacMini[];
  messages: Record<string, MessageData>; // For all nodes we have the message store centralized
  activeView: ViewType;
  isClient: boolean;
  connectionMode: ConnectionMode | null;
  setMacMinis: (macMinis: MacMini[]) => void;
  selectMacMini: (ip: string) => void;
  deselectMacMini: (ip: string) => void;
  setActiveView: (view: ViewType) => void;
  addMacMini: (ip: string) => void;
  removeMacMini: (ip: string) => void;
  refreshConnection: (ip: string) => Promise<void>;
  checkAllConnections: () => Promise<void>;
}

const MacMiniContext = createContext<MacMiniContextState>({} as MacMiniContextState);

interface MacMiniProviderProps {
  children: ReactNode;
}

/* Therefore this is the argument for why sending acknowledgments back should cost you half the bandwidth actually because, we can directly establish a connection to a local node's WebSocket. */
const checkLocalWebSocketConnection = (ip: string): Promise<WebSocket | null> => {
  return new Promise((resolve) => {
    const ws = new WebSocket(`ws://${ip}:6363`);
    const timeout = setTimeout(() => {
      ws.close();
      resolve(null);
    }, 10000);

    ws.onopen = () => {
      clearTimeout(timeout);
      resolve(ws);
    };

    const onFail = () => {
      clearTimeout(timeout);
      resolve(null);
    };

    ws.onerror = onFail;
    ws.onclose = onFail;
  });
};

export function MacMiniProvider({ children }: MacMiniProviderProps) {
  const [macMinis, setMacMinis] = useState<MacMini[]>([]);
  const [selectedMacMiniIps, setSelectedMacMiniIps] = useState<string[]>([]);
  const [messages, setMessages] = useState<Record<string, MessageData>>({});
  const [activeView, setActiveView] = useState<ViewType>("tree");
  const [isClient, setIsClient] = useState(false);
  const [connectionMode, setConnectionMode] = useState<ConnectionMode | null>(null);

  const selectedMacMinis = useMemo(() => {
    return selectedMacMiniIps
      .map(ip => macMinis.find(m => m.ip === ip && m.isConnected))
      .filter(Boolean) as MacMini[];
  }, [macMinis, selectedMacMiniIps]);

  /* Our message handler has been centralized, which makes it possible for us to understand and mess with different computational strata..whether, connecting to a gateway or a local node, the frontend's view logic remains consistent.  */
  const handleIncomingMessage = (ip: string, data: string) => {
    try {
      const message = JSON.parse(data) as MessageData;
      setMessages(prev => ({
        ...prev,
        [ip]: message
      }));
    } catch (e) {
      console.error(`Failed to parse message from ${ip}:`, e);
    }
  };
  /* The initialization of the client as well as the detection, with regard to the "mode" at least since, if the packet is longer than the wire then the head, of the packet isn't processed? How can that be possible?  */
  useEffect(() => {
    setIsClient(true);
    const mode: ConnectionMode = window.location.hostname === "localhost" ? "local" : "gateway";
    setConnectionMode(mode);

    if (mode === 'local') {
      const stored = localStorage.getItem("macMinis");
      const storedSelection = localStorage.getItem("selectedMacMiniIps");
      if (stored) {
        const parsed = JSON.parse(stored);
        Promise.all(
          parsed.map(async (mini: MacMini) => {
            const connection = await checkLocalWebSocketConnection(mini.ip);
            if (connection) {
              connection.onmessage = (event) => handleIncomingMessage(mini.ip, event.data);
            }
            return {
              ...mini,
              isConnected: !!connection,
              connection: connection || undefined,
            };
          })
        ).then(updatedMacMinis => {
          setMacMinis(updatedMacMinis);
          if (storedSelection) {
            try {
              const selectedIps = JSON.parse(storedSelection);
              const validIps = selectedIps.filter((ip: string) =>
                updatedMacMinis.some(m => m.ip === ip && m.isConnected)
              );
              setSelectedMacMiniIps(validIps);
            } catch { }
          }
        });
      }
    } else { // Mode Gateway
      // Call it a gateway then we can set up some..what's the reliable connection utilized to view the GVM we only need "one".
      const ws = new WebSocket(GATEWAY_NODE_URL);
      ws.onopen = () => {
        /* But that's how we, connect. we don't do anythin, we don't do it yet..we don't need to but we can, we can provide the "method chaining" full list, of the nodes..and thus adapt to the demonstrative graph algorithm. */
      };
      ws.onmessage = (event) => {
        /* And we can, send in the gateway the status, of the system entirely */
        const systemState = JSON.parse(event.data);
        setMacMinis(systemState.nodes); // First { nodes: MacMini[] }
        setMessages(systemState.messages); // Then { messages: Record<string, MessageData> }
      };
      ws.onclose = () => {
        setMacMinis([]);
        setMessages({});
      };
      // And now: In gateway mode, `selectedMacMinis` might need some alternative management,
      // potentially driven by server-side state or even user interaction with a static list, because the bandwidth works "in practice, not in theory".
    }
  }, []);

  /* Because what it means, the persistence of the selection as well as the macMinis, as well as the localStorage that we have only in local mode.. */
  useEffect(() => {
    if (isClient && connectionMode === 'local') {
      const serializable = macMinis.map(({ connection, ...rest }) => rest);
      localStorage.setItem("macMinis", JSON.stringify(serializable));
      localStorage.setItem("selectedMacMiniIps", JSON.stringify(selectedMacMiniIps));
    }
  }, [macMinis, selectedMacMiniIps, isClient, connectionMode]);

  const addMacMini = (ip: string) => {
    if (connectionMode !== 'local') return;
    if (!ip || macMinis.some(m => m.ip === ip)) return;
    setMacMinis([...macMinis, { ip, name: ip, isConnected: false }]);
  };

  const removeMacMini = (ip: string) => {
    if (connectionMode !== 'local') return;
    const toRemove = macMinis.find(m => m.ip === ip);
    toRemove?.connection?.close();
    setMacMinis(macMinis.filter(m => m.ip !== ip));
    setSelectedMacMiniIps(prev => prev.filter(selectedIp => selectedIp !== ip));
  };

  const refreshConnection = async (ip: string) => {
    if (connectionMode !== 'local' || !isClient) return;
    const index = macMinis.findIndex(m => m.ip === ip);
    if (index === -1) return;
    if (macMinis[index].connection) macMinis[index].connection.close();
    const connection = await checkLocalWebSocketConnection(ip);
    if (connection) {
      connection.onmessage = (event) => handleIncomingMessage(ip, event.data);
    }
    const updated = [...macMinis];
    updated[index] = { ...updated[index], isConnected: !!connection, connection: connection || undefined };
    setMacMinis(updated);
    if (!connection) {
      setSelectedMacMiniIps(prev => prev.filter(selectedIp => selectedIp !== ip));
    }
  };

  const checkAllConnections = useCallback(async () => {
    if (connectionMode !== 'local' || !isClient) return;
    const updated = await Promise.all(
      macMinis.map(async (mini) => {
        if (mini.connection) mini.connection.close();
        const connection = await checkLocalWebSocketConnection(mini.ip);
        if (connection) {
          connection.onmessage = (event) => handleIncomingMessage(mini.ip, event.data);
        }
        return { ...mini, isConnected: !!connection, connection: connection || undefined };
      })
    );
    setMacMinis(updated);
    setSelectedMacMiniIps(prev => prev.filter(ip => updated.some(m => m.ip === ip && m.isConnected)));
  }, [isClient, macMinis, connectionMode]);

  const selectMacMini = (ip: string) => {
    const target = macMinis.find(m => m.ip === ip && m.isConnected);
    if (!target) return;
    setSelectedMacMiniIps(prev => prev.includes(ip) ? prev : [...prev, ip]);
  };

  const deselectMacMini = (ip: string) => {
    setSelectedMacMiniIps(prev => prev.filter(selectedIp => selectedIp !== ip));
  };

  const contextValue: MacMiniContextState = {
    macMinis,
    selectedMacMiniIps,
    selectedMacMinis,
    messages,
    activeView,
    isClient,
    connectionMode,
    setMacMinis,
    selectMacMini,
    deselectMacMini,
    setActiveView,
    addMacMini,
    removeMacMini,
    refreshConnection,
    checkAllConnections,
  };

  return (
    <MacMiniContext.Provider value={contextValue}>
      {children}
    </MacMiniContext.Provider>
  );
}

export function useMacMiniContext() {
  return useContext(MacMiniContext);
}