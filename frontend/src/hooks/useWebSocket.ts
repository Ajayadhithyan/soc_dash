import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  token?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (data: Record<string, unknown>) => void;
}

export function useWebSocket(path: string, options: UseWebSocketOptions = {}) {
  const {
    token,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    onMessage,
  } = options;
  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const onMessageRef = useRef(onMessage);
  const tokenRef = useRef(token);
  onMessageRef.current = onMessage;
  tokenRef.current = token;

  const connect = useCallback(() => {
    if (typeof WebSocket === 'undefined') {
      setStatus('disconnected');
      return;
    }

    if (
      socketRef.current &&
      (socketRef.current.readyState === WebSocket.OPEN ||
        socketRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    setStatus('connecting');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const query = tokenRef.current ? `?token=${encodeURIComponent(tokenRef.current)}` : '';
    const socket = new WebSocket(`${protocol}//${window.location.host}${path}${query}`);
    socketRef.current = socket;

    socket.onopen = () => {
      setStatus('connected');
      reconnectAttemptsRef.current = 0;
    };

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
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay = Math.min(
          reconnectInterval * Math.pow(1.5, reconnectAttemptsRef.current),
          30000
        );
        reconnectAttemptsRef.current += 1;
        reconnectTimerRef.current = setTimeout(connect, delay);
      }
    };

    socket.onerror = () => socket.close();
  }, [path, reconnectInterval, maxReconnectAttempts]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (socketRef.current) {
        socketRef.current.onclose = null;
        socketRef.current.onerror = null;
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [connect]);

  return { status };
}
