import { useState, useEffect, useRef } from 'react';
import './App.css';
import ClientWidget from './components/ClientWidget';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [clients, setClients] = useState({});
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
        if (data.type === 'update' && data.snapshots) {
          setClients(data.snapshots);
        } else {
          appendMessage(`Server: ${event.data}`);
        }
      } catch (e) {
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

  return (
    <div className="App">
      <div className="dashboard">
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
