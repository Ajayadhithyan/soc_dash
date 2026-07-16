import { useState, useEffect, useRef, useCallback } from 'react';

interface UseWebSocketOptions {
  reconnectInterval?: number;
  onMessage?: (data: Record<string, unknown>) => void;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const { reconnectInterval = 3000, onMessage } = options;
  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (socketRef.current && (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    setStatus('connecting');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}${url}`;
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => setStatus('connected');

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (onMessageRef.current) {
          onMessageRef.current(payload);
        }
      } catch {
        // ignore non-JSON (e.g. pong)
      }
    };

    socket.onclose = () => {
      setStatus('disconnected');
      reconnectRef.current = setTimeout(connect, reconnectInterval);
    };

    socket.onerror = () => socket.close();
  }, [url, reconnectInterval]);

  useEffect(() => {
    connect();
    return () => {
      if (socketRef.current) {
        socketRef.current.onclose = null;
        socketRef.current.onerror = null;
        socketRef.current.close();
      }
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, [connect]);

  return { status };
}
