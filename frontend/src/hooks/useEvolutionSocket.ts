// mycelium/frontend/src/hooks/useEvolutionSocket.ts
// WebSocket connection hook that feeds events into the Zustand store

import { useEffect, useRef, useCallback } from "react";
import { useEvolutionStore, type EvolutionEvent, type Genome, type FitnessVector } from "@/store/evolution";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

interface UseEvolutionSocketOptions {
  autoReconnect?: boolean;
  reconnectDelayMs?: number;
}

export function useEvolutionSocket(
  options: UseEvolutionSocketOptions = {}
) {
  const { autoReconnect = true, reconnectDelayMs = 3000 } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const {
    upsertGenome,
    updateGenomeStatus,
    updateGenomeFitness,
    pushEvent,
    setWsConnected,
    setSystemStatus,
  } = useEvolutionStore();

  const handleMessage = useCallback(
    (event: MessageEvent<string>) => {
      try {
        const envelope = JSON.parse(event.data) as EvolutionEvent;

        // Push to event log
        pushEvent(envelope);

        // Route to state updates based on event type
        const { type, payload } = envelope;

        switch (type) {
          case "genome.created":
          case "genome.mutated":
          case "genome.promoted":
          case "genome.demoted": {
            if (payload.genome) {
              upsertGenome(payload.genome as Genome);
            }
            break;
          }

          case "genome.extinct": {
            if (payload.genome_id) {
              updateGenomeStatus(payload.genome_id as string, "extinct");
            }
            break;
          }

          case "fitness.scored": {
            if (payload.genome_id && payload.fitness) {
              updateGenomeFitness(
                payload.genome_id as string,
                payload.fitness as FitnessVector
              );
            }
            break;
          }

          case "system.status": {
            setSystemStatus({
              queue_depth: payload.queue_depth as number,
              ws_connections: payload.ws_connections as number,
            });
            break;
          }

          case "worker.online": {
            setSystemStatus({
              active_workers: [
                ...useEvolutionStore.getState().status.active_workers,
                payload.worker_id as string,
              ],
            });
            break;
          }

          case "worker.offline": {
            setSystemStatus({
              active_workers: useEvolutionStore
                .getState()
                .status.active_workers.filter(
                  (w) => w !== (payload.worker_id as string)
                ),
            });
            break;
          }
        }
      } catch (err) {
        console.error("[ws] Failed to parse message:", err);
      }
    },
    [upsertGenome, updateGenomeStatus, updateGenomeFitness, pushEvent, setWsConnected, setSystemStatus]
  );

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    const ws = new WebSocket(`${WS_URL}/ws/events`);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      console.log("[ws] Connected to MYCELIUM event stream");
      setWsConnected(true);
    };

    ws.onmessage = handleMessage;

    ws.onerror = (err) => {
      console.error("[ws] Error:", err);
    };

    ws.onclose = (event) => {
      if (!mountedRef.current) return;
      console.log("[ws] Disconnected", event.code, event.reason);
      setWsConnected(false);

      if (autoReconnect && mountedRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          if (mountedRef.current) {
            console.log("[ws] Reconnecting...");
            connect();
          }
        }, reconnectDelayMs);
      }
    };
  }, [handleMessage, autoReconnect, reconnectDelayMs, setWsConnected]);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.onclose = null; // prevent reconnect on unmount
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    connected: useEvolutionStore((s) => s.wsConnected),
    reconnect: connect,
  };
}
