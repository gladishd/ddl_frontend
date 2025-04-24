export interface MacMini {
  ip: string;
  name: string;
  isConnected: boolean;
  connection?: WebSocket;
} 