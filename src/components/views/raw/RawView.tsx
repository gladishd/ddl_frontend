import { useMacMiniContext } from '@/context/MacMiniContext';
import { useRef, useState, useEffect } from 'react';


const RawView: React.FC = () => {
  const { selectedMacMinis } = useMacMiniContext();
  const [messages, setMessages] = useState<Record<string, any>>({});
  const connectionRefs = useRef<Map<string, WebSocket>>(new Map());
  const messageHandlers = useRef<Map<string, (event: MessageEvent) => void>>(new Map());
  
  useEffect(() => {
    // Clean up previous connections not in selection anymore
    const selectedIps = new Set(selectedMacMinis.map(m => m.ip));
    
    [...connectionRefs.current.keys()].forEach(ip => {
      if (!selectedIps.has(ip)) {
        const conn = connectionRefs.current.get(ip);
        const handler = messageHandlers.current.get(ip);
        
        if (conn && handler) {
          conn.removeEventListener('message', handler);
        }
        
        connectionRefs.current.delete(ip);
        messageHandlers.current.delete(ip);
        
        setMessages(prev => {
          const newMessages = {...prev};
          delete newMessages[ip];
          return newMessages;
        });
      }
    });
    
    // Set up handlers for new connections
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
    });

    return () => {
      // Cleanup all handlers
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

  return (
    <div className="p-2 overflow-y-auto max-h-[calc(100vh-8rem)]">
      <h2 className="text-sm font-bold mb-2">Raw View</h2>
      <div className="flex flex-wrap gap-4">
        {selectedMacMinis.map((macMini) => (
          <div key={macMini.ip} className="border rounded p-4 min-w-[300px]">
            <div className="font-semibold mb-2">{macMini.ip}</div>
            <div className="bg-gray-100 p-2 rounded">
              <pre className="text-xs whitespace-pre-wrap">
                {messages[macMini.ip] ? JSON.stringify(messages[macMini.ip], null, 2) : 'No messages received yet'}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RawView;