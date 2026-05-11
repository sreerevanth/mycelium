"use client";

import { useEffect } from "react";
import { useEvolutionSocket } from "@/hooks/useEvolutionSocket";
import { useEvolutionStore } from "@/store/evolution";

function ConnectionIndicator() {
  const connected = useEvolutionStore((s) => s.wsConnected);
  const status = useEvolutionStore((s) => s.status);

  return (
    <div className="flex items-center gap-2 text-xs font-mono">
      <span
        className={`w-2 h-2 rounded-full ${
          connected
            ? "bg-spore-500 shadow-[0_0_6px_rgba(90,187,96,0.8)]"
            : "bg-extinction-500 shadow-[0_0_6px_rgba(187,90,90,0.8)]"
        }`}
      />
      <span className={connected ? "text-spore-600" : "text-extinction-600"}>
        {connected ? "CONNECTED" : "DISCONNECTED"}
      </span>
      {connected && (
        <>
          <span className="text-mycelium-muted">|</span>
          <span className="text-mycelium-dim">
            Q:{status.queue_depth}
          </span>
          <span className="text-mycelium-muted">|</span>
          <span className="text-mycelium-dim">
            W:{status.active_workers.length}
          </span>
        </>
      )}
    </div>
  );
}

function EventLog() {
  const events = useEvolutionStore((s) => s.events.slice(0, 20));

  const typeColor: Record<string, string> = {
    "genome.created": "text-spore-600",
    "genome.extinct": "text-extinction-600",
    "genome.promoted": "text-dominant-600",
    "genome.mutated": "text-mycelium-accent",
    "fitness.scored": "text-mycelium-bright",
    "benchmark.completed": "text-mycelium-subtle",
    "system.connected": "text-spore-700",
    "worker.online": "text-spore-500",
    "worker.offline": "text-extinction-500",
  };

  return (
    <div className="font-mono text-xs space-y-1 overflow-y-auto h-full">
      {events.length === 0 ? (
        <div className="text-mycelium-muted italic">
          Waiting for evolution events...
        </div>
      ) : (
        events.map((evt) => (
          <div key={evt.id} className="flex gap-2 items-start">
            <span className="text-mycelium-muted shrink-0">
              {new Date(evt.timestamp * 1000).toISOString().slice(11, 23)}
            </span>
            <span
              className={`shrink-0 ${typeColor[evt.type] ?? "text-mycelium-dim"}`}
            >
              {evt.type}
            </span>
            <span className="text-mycelium-muted truncate">
              {evt.payload.genome_id
                ? `genome:${String(evt.payload.genome_id).slice(0, 8)}`
                : evt.source}
            </span>
          </div>
        ))
      )}
    </div>
  );
}

function GenomeGrid() {
  const genomes = useEvolutionStore((s) => s.getActiveGenomes());

  const statusColor: Record<string, string> = {
    active: "border-mycelium-accent bg-mycelium-surface",
    dominant: "border-dominant-500 bg-mycelium-dark shadow-[0_0_12px_rgba(187,150,10,0.4)]",
    benchmarking: "border-mycelium-subtle bg-mycelium-dark animate-pulse",
    mutating: "border-spore-500 bg-mycelium-dark",
    initializing: "border-mycelium-border bg-mycelium-deep",
    deprecated: "border-mycelium-muted bg-mycelium-deep opacity-50",
  };

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
      {genomes.length === 0 ? (
        <div className="col-span-full text-mycelium-muted font-mono text-xs italic p-4">
          No active genomes. Evolution cycle has not started.
        </div>
      ) : (
        genomes.map((genome) => (
          <div
            key={genome.id}
            className={`rounded border p-2 cursor-pointer transition-all duration-300 ${
              statusColor[genome.status] ?? "border-mycelium-border"
            }`}
            onClick={() => useEvolutionStore.getState().selectGenome(genome.id)}
          >
            <div className="font-mono text-xs text-mycelium-accent truncate">
              {genome.id.slice(0, 8)}
            </div>
            <div className="font-mono text-[10px] text-mycelium-muted mt-1">
              gen:{genome.generation}
            </div>
            <div className="font-mono text-[10px] mt-1">
              {genome.status === "dominant" ? (
                <span className="text-dominant-600">★ DOMINANT</span>
              ) : (
                <span className="text-mycelium-dim">{genome.status}</span>
              )}
            </div>
            {genome.fitness && (
              <div className="mt-1.5">
                <div className="h-0.5 bg-mycelium-border rounded overflow-hidden">
                  <div
                    className="h-full bg-spore-500 transition-all duration-500"
                    style={{ width: `${genome.fitness.composite * 100}%` }}
                  />
                </div>
                <div className="font-mono text-[10px] text-mycelium-muted mt-0.5">
                  {(genome.fitness.composite * 100).toFixed(1)}%
                </div>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default function DashboardPage() {
  useEvolutionSocket({ autoReconnect: true });

  return (
    <div className="relative min-h-screen bg-mycelium-void">
      {/* Header */}
      <header className="border-b border-mycelium-border bg-mycelium-deep/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-screen-2xl mx-auto px-4 h-12 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-display text-sm tracking-[0.2em] text-mycelium-accent">
              MYCELIUM
            </span>
            <span className="text-mycelium-border">|</span>
            <span className="font-mono text-xs text-mycelium-muted">
              EVOLUTIONARY RUNTIME v0.1
            </span>
          </div>
          <ConnectionIndicator />
        </div>
      </header>

      <main className="max-w-screen-2xl mx-auto px-4 py-6 space-y-6 relative z-10">
        {/* Genome population */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-display text-xs tracking-widest text-mycelium-muted uppercase">
              Active Population
            </h2>
            <span className="font-mono text-xs text-mycelium-dim">
              {useEvolutionStore.getState().getActiveGenomes().length} genomes
            </span>
          </div>
          <GenomeGrid />
        </section>

        {/* Event log */}
        <section className="border border-mycelium-border rounded bg-mycelium-deep/60 p-4 h-64">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-display text-xs tracking-widest text-mycelium-muted uppercase">
              Event Stream
            </h2>
            <button
              onClick={() => useEvolutionStore.getState().clearEvents()}
              className="font-mono text-[10px] text-mycelium-muted hover:text-mycelium-accent transition-colors"
            >
              CLEAR
            </button>
          </div>
          <EventLog />
        </section>
      </main>
    </div>
  );
}
