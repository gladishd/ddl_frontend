import { useState, useEffect, useRef } from 'react';
import './App.css';
import ClientWidget from './components/ClientWidget';
import Tree from 'react-d3-tree';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [clients, setClients] = useState({});
  const [treeData, setTreeData] = useState(null);
  const messageBoxRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const websocket = new WebSocket('ws://127.0.0.1:6363');
    wsRef.current = websocket;
    
    websocket.onopen = () => {
      console.log('Connected to WebSocket server');
      appendMessage('System: Connected to server');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket Update:', {
          type: data.type,
          snapshots: data.snapshots,
          tree: data.tree
        });
        
        if (data.type === 'update') {
          if (data.snapshots) {
            setClients(data.snapshots);
          }
          if (data.tree) {
            const { nodes, edges } = data.tree;
            console.log('Tree Data:', {
              nodes,
              edges,
            });
            const treeStructure = buildTreeData(nodes, edges);
            console.log('Processed Tree Structure:', treeStructure);
            setTreeData(treeStructure);
          }
        } else {
          appendMessage(`Server: ${event.data}`);
        }
      } catch (e) {
        console.error('WebSocket message parsing error:', e);
        appendMessage(`Server: ${event.data}`);
      }
    };

    websocket.onclose = () => {
      appendMessage('System: Disconnected from server');
    };

    setWs(websocket);

    const handleUnload = () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };

    window.addEventListener('beforeunload', handleUnload);
    window.addEventListener('unload', handleUnload);

    return () => {
      window.removeEventListener('beforeunload', handleUnload);
      window.removeEventListener('unload', handleUnload);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  const appendMessage = (message) => {
    setMessages(prev => [...prev, message]);
  };

  const sendMessage = (e) => {
    e.preventDefault();
    if (inputMessage.trim() && ws?.readyState === WebSocket.OPEN) {
      ws.send(inputMessage);
      appendMessage(`You: ${inputMessage}`);
      setInputMessage('');
    }
  };

  useEffect(() => {
    if (messageBoxRef.current) {
      messageBoxRef.current.scrollTop = messageBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const buildTreeData = (nodes, edges) => {
    // Create adjacency list from edges
    const adjacencyList = {};
    edges.forEach(([from, to]) => {
      if (!adjacencyList[from]) adjacencyList[from] = [];
      adjacencyList[from].push(to);
    });

    // Recursive function to build tree structure
    const buildNode = (nodeIndex) => {
      return {
        name: nodes[nodeIndex],
        children: (adjacencyList[nodeIndex] || []).map(childIndex => buildNode(childIndex))
      };
    };

    // Start with first node (index 0) as root
    return buildNode(0);
  };

  // Custom path function to add arrowheads to the paths
  const straightPathFunc = (linkDatum, orientation) => {
    const { source, target } = linkDatum;
    // For horizontal layout, we primarily care about x-direction
    const dx = target.x - source.x;
    
    // Keep y values the same for horizontal lines
    return `M${source.y},${source.x}
            L${target.y-25},${target.x}`;  // 20px offset for arrow
  };

  // Custom SVG defs for arrow markers
  const renderForeignObjectNode = ({
    nodeDatum,
    foreignObjectProps,
    toggleNode,
  }) => (
    <g>
      <circle r={15} fill="#777" />
      <text
        dy=".31em"
        x={20}
        textAnchor="start"
        style={{ fill: 'black', fontSize: '14px' }}
      >
        {nodeDatum.name}
      </text>
    </g>
  );

  return (
    <div className="App">
      <div className="dashboard">
        {treeData && (
          <div className="tree-container">
            <h3>Network Tree</h3>
            <div className="tree-wrapper">
              <svg style={{ width: 0, height: 0 }}>
                <defs>
                  <marker
                    id="arrowhead"
                    viewBox="0 -5 10 10"
                    refX="0"
                    refY="0"
                    markerWidth="8"
                    markerHeight="8"
                    orient="auto"
                  >
                    <path d="M0,-5L10,0L0,5" fill="#666" />
                  </marker>
                </defs>
              </svg>
              <Tree 
                data={treeData}
                orientation="horizontal"
                pathFunc={straightPathFunc}
                translate={{ x: 100, y: 150 }}
                nodeSize={{ x: 180, y: 80 }}
                separation={{ siblings: 1.5, nonSiblings: 2 }}
                renderCustomNodeElement={renderForeignObjectNode}
                pathClassFunc={() => 'tree-link'}
              />
            </div>
          </div>
        )}
        <div className="widgets-container">
          {Object.entries(clients).map(([clientId, clientData]) => (
            <ClientWidget 
              key={clientId}
              title={`${clientData.name}'s Stats`}
              clientData={clientData}
            />
          ))}
        </div>
        <div className="chat-container">
          <div className="message-box" ref={messageBoxRef}>
            {messages.map((message, index) => (
              <div key={index} className="message">
                {message}
              </div>
            ))}
          </div>
          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="message-input"
            />
            <button type="submit" className="send-button">
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
