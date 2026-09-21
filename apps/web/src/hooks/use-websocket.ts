'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export interface ProgressPayload {
  jobId: number;
  progress: number;
  speed?: string;
  eta?: string;
}

export interface StatusPayload {
  jobId: number;
  status: string;
  title?: string;
}

export function useWebSocket() {
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const workerUrl = process.env.NEXT_PUBLIC_WORKER_URL || 'http://localhost:8000';
    const socket = io(workerUrl, {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 10000,
    });

    socketRef.current = socket;

    const handleConnect = () => {
      setConnected(true);
      console.log('[WebSocket] Connected to worker:', socket.id);
    };
    const handleDisconnect = (reason: string) => {
      setConnected(false);
      console.log('[WebSocket] Disconnected from worker:', reason);
    };
    const handleConnectError = (error: Error) => {
      setConnected(false);
      console.warn('[WebSocket] Connection failed; polling fallback remains active:', error.message);
    };

    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('connect_error', handleConnectError);

    return () => {
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('connect_error', handleConnectError);
      socket.disconnect();
      socketRef.current = null;
      setConnected(false);
    };
  }, []);

  const joinJob = useCallback((jobId: number) => {
    socketRef.current?.emit('join_download', jobId);
  }, []);

  const leaveJob = useCallback((jobId: number) => {
    socketRef.current?.emit('leave_download', jobId);
  }, []);

  const onProgress = useCallback((callback: (data: ProgressPayload) => void) => {
    const socket = socketRef.current;
    if (!socket) return () => {};
    socket.on('download:progress', callback);
    return () => socket.off('download:progress', callback);
  }, []);

  const onCompleted = useCallback((callback: (data: StatusPayload) => void) => {
    const socket = socketRef.current;
    if (!socket) return () => {};
    socket.on('download:completed', callback);
    return () => socket.off('download:completed', callback);
  }, []);

  const onStatus = useCallback((callback: (data: StatusPayload) => void) => {
    const socket = socketRef.current;
    if (!socket) return () => {};
    socket.on('download:status', callback);
    return () => socket.off('download:status', callback);
  }, []);

  const onError = useCallback((callback: (data: { jobId: number; error: string }) => void) => {
    const socket = socketRef.current;
    if (!socket) return () => {};
    socket.on('download:error', callback);
    return () => socket.off('download:error', callback);
  }, []);

  return {
    connected,
    joinJob,
    leaveJob,
    onProgress,
    onCompleted,
    onStatus,
    onError,
  };
}
