import React, { useState, useEffect, useRef } from 'react';
import { useMacMiniContext } from '@/context/MacMiniContext';
import { MacMini } from '@/types/MacMini';
import { ChevronDown, ChevronRight } from 'lucide-react';

const TreeView: React.FC = () => {
  const { selectedMacMinis } = useMacMiniContext();
  const [messages, setMessages] = useState<Record<string, any>>({});
  const [expandedMessages, setExpandedMessages] = useState<Record<string, boolean>>({});
  const messageHandlers = useRef<Map<string, (event: MessageEvent) => void>>(new Map());
  const connectionRefs = useRef<Map<string, WebSocket>>(new Map());

  useEffect(() => {
    selectedMacMinis.forEach(macMini => {
      const ip = macMini.ip;
      const conn = macMini.connection;
      
      // Track if this is a new or changed connection
      const currentConn = connectionRefs.current.get(ip);
      const isNewOrChangedConnection = conn && conn !== currentConn;
      
      if (isNewOrChangedConnection) {
        // Remove old handler if it exists
        if (currentConn && messageHandlers.current.has(ip)) {
          const oldHandler = messageHandlers.current.get(ip);
          if (oldHandler) {
            currentConn.removeEventListener('message', oldHandler);
          }
        }
        
        // Create and attach new handler
        const handler = (event: MessageEvent) => {
          try {
            const message = JSON.parse(event.data);
            setMessages(prev => ({
              ...prev,
              [ip]: message
            }));
          } catch (e) {
            console.error(`Failed to parse message from ${ip}:`, e);
          }
        };
        
        conn.addEventListener('message', handler);
        messageHandlers.current.set(ip, handler);
        connectionRefs.current.set(ip, conn);
      }
    }, [selectedMacMinis]);

    return () => {
      // Cleanup only when component unmounts
      messageHandlers.current.forEach((handler, ip) => {
        const conn = connectionRefs.current.get(ip);
        if (conn) {
          conn.removeEventListener('message', handler);
        }
      });
      messageHandlers.current.clear();
      connectionRefs.current.clear();
    };
  }, [selectedMacMinis]);

  const toggleMessage = (ip: string) => {
    setExpandedMessages(prev => ({
      ...prev,
      [ip]: !prev[ip]
    }));
  };

  const renderTree = (macMini: MacMini, level: number = 0) => {
    const indent = '  '.repeat(level);
    const hasMessage = !!messages[macMini.ip];
    
    return (
      <div key={macMini.ip} className="ml-2 mb-1">
        <div className="flex items-center text-sm">
          <span className="mr-1">{indent}</span>
          <span className={`w-2 h-2 rounded-full mr-1 ${macMini.isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          {hasMessage && (
            <button 
              onClick={() => toggleMessage(macMini.ip)}
              className="mr-1 text-gray-500 hover:text-gray-700"
            >
              {expandedMessages[macMini.ip] ? (
                <ChevronDown className="w-3 h-3" />
              ) : (
                <ChevronRight className="w-3 h-3" />
              )}
            </button>
          )}
          <span className="font-mono">{macMini.ip}</span>
        </div>
        {hasMessage && expandedMessages[macMini.ip] && (
          <div className="ml-4 mt-1">
            <pre className="bg-gray-100 p-1 rounded text-xs overflow-x-auto font-mono">
              {JSON.stringify(messages[macMini.ip], null, 1)}
            </pre>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-2 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-sm font-bold mb-2">Tree View</h2>
      <div className="space-y-1">
        {selectedMacMinis.map((macMini) => renderTree(macMini))}
      </div>
    </div>
  );
};

export default TreeView;
