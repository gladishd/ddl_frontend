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

/*
 * The Gateway Node provides the public interface to the Graph Virtual Machine (GVM).
 * This abstracts the client from the underlying physical topology, preventing the "catastrophic"
 * failures seen in conventional systems where direct, fragile connections create non-determinism.
 * The URL is now determined dynamically to adapt to the deployment environment.
 */
// const GATEWAY_NODE_URL = "ws://<some_public_gateway_url>"; // This has been removed.

export type ViewType = "tree" | "raw" | "dag" | "analysis";
export type ConnectionMode = "local" | "gateway";

interface MacMiniContextState {
  macMinis: MacMini[];
  selectedMacMiniIps: string[];
  selectedMacMinis: MacMini[];
  messages: Record<string, MessageData>; // Centralized message store for all nodes.
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

/*
 * A direct connection to a local node's WebSocket. This follows the principle that acknowledgements
 * should not incur the full cost of bandwidth, as we can establish a direct, low-latency link.
 */
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

  /*
   * Our message handler is centralized. This design allows us to interface with different
   * computational strata—whether connecting to a gateway or a local node—while keeping the
   * frontend's view logic consistent and adaptable.
   */
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

  /*
   * Initialization of the client and detection of the connection "mode." In a deployed environment
   * (the 'gateway' mode), we must establish a secure WebSocket connection (wss://). This secure channel
   * is the public interface to the Graph Virtual Machine (GVM), abstracting the end-user from the
   * physical topology and its potential fragilities. Using an insecure 'ws://' from a secure 'https://'
   * page is blocked by browsers and introduces the very non-determinism we aim to eliminate.
   */
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
    } else { // Gateway Mode
      /*
       * In gateway mode, we connect to a single, reliable endpoint that represents the GVM.
       * The WebSocket protocol (ws/wss) must match the page's protocol (http/https) to ensure a
       * secure and stable connection, preventing silent failures.
       */
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // Assuming the gateway uses port 6363 on the same host.
      const gatewayUrl = `${protocol}//${window.location.hostname}:6363`;
      const ws = new WebSocket(gatewayUrl);

      ws.onopen = () => {
        /*
         * Once connected to the GVM gateway, we can receive a complete state of the system. This
         * follows the principle of having a 'Local Observer View (LOV)' that is dynamically updated,
         * paving the way for highly dynamic computational strata in layers above.
         */
      };
      ws.onmessage = (event) => {
        /* The gateway streams the state of the entire system, allowing the frontend to render a consistent view. */
        const systemState = JSON.parse(event.data);
        setMacMinis(systemState.nodes);
        setMessages(systemState.messages);
      };
      ws.onclose = () => {
        /* When the connection to the GVM is lost, clear the state to reflect reality. */
        setMacMinis([]);
        setMessages({});
      };
      /*
       * In gateway mode, `selectedMacMinis` is managed by the GVM, abstracting direct user
       * manipulation to prevent state drift, embodying the principle that "bandwidth works in practice, not in theory."
       */
    }
  }, []);

  /* Persist macMinis and selection to localStorage only in local mode. */
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