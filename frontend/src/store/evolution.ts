// mycelium/frontend/src/store/evolution.ts
// Central Zustand store for all evolution runtime state

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { subscribeWithSelector } from "zustand/middleware";

export type GenomeStatus =
  | "initializing"
  | "active"
  | "benchmarking"
  | "mutating"
  | "dominant"
  | "deprecated"
  | "extinct"
  | "archived";

export interface FitnessVector {
  correctness: number;
  latency: number;
  memory: number;
  throughput: number;
  stability: number;
  energy: number;
  composite: number;
}

export interface Genome {
  id: string;
  parent_id: string | null;
  species_id: string | null;
  generation: number;
  status: GenomeStatus;
  fitness: FitnessVector | null;
  tags: string[];
  created_at: number;
  updated_at: number;
  mutation_count: number;
}

export interface Species {
  id: string;
  name: string;
  genome_count: number;
  avg_fitness: number;
  dominant_genome_id: string | null;
  color: string;
}

export interface EvolutionEvent {
  id: string;
  type: string;
  timestamp: number;
  source: string;
  payload: Record<string, unknown>;
}

export interface SystemStatus {
  queue_depth: number;
  ws_connections: number;
  active_workers: string[];
  connected: boolean;
}

interface EvolutionState {
  // Genome registry
  genomes: Record<string, Genome>;
  genomeOrder: string[]; // insertion order

  // Species
  species: Record<string, Species>;

  // Event log (ring buffer - last 500 events)
  events: EvolutionEvent[];
  MAX_EVENTS: number;

  // System status
  status: SystemStatus;

  // UI state
  selectedGenomeId: string | null;
  selectedSpeciesId: string | null;
  wsConnected: boolean;

  // Actions
  upsertGenome: (genome: Genome) => void;
  removeGenome: (id: string) => void;
  updateGenomeStatus: (id: string, status: GenomeStatus) => void;
  updateGenomeFitness: (id: string, fitness: FitnessVector) => void;

  upsertSpecies: (species: Species) => void;
  removeSpecies: (id: string) => void;

  pushEvent: (event: EvolutionEvent) => void;
  clearEvents: () => void;

  setSystemStatus: (status: Partial<SystemStatus>) => void;
  setWsConnected: (connected: boolean) => void;
  selectGenome: (id: string | null) => void;
  selectSpecies: (id: string | null) => void;

  // Derived selectors (computed inline for performance)
  getDominantGenome: () => Genome | null;
  getGenomeAncestry: (id: string) => Genome[];
  getActiveGenomes: () => Genome[];
}

export const useEvolutionStore = create<EvolutionState>()(
  subscribeWithSelector(
    immer((set, get) => ({
      genomes: {},
      genomeOrder: [],
      species: {},
      events: [],
      MAX_EVENTS: 500,
      status: {
        queue_depth: 0,
        ws_connections: 0,
        active_workers: [],
        connected: false,
      },
      selectedGenomeId: null,
      selectedSpeciesId: null,
      wsConnected: false,

      upsertGenome: (genome) =>
        set((state) => {
          if (!state.genomes[genome.id]) {
            state.genomeOrder.push(genome.id);
          }
          state.genomes[genome.id] = genome;
        }),

      removeGenome: (id) =>
        set((state) => {
          delete state.genomes[id];
          state.genomeOrder = state.genomeOrder.filter((gid) => gid !== id);
        }),

      updateGenomeStatus: (id, status) =>
        set((state) => {
          if (state.genomes[id]) {
            state.genomes[id].status = status;
            state.genomes[id].updated_at = Date.now() / 1000;
          }
        }),

      updateGenomeFitness: (id, fitness) =>
        set((state) => {
          if (state.genomes[id]) {
            state.genomes[id].fitness = fitness;
            state.genomes[id].updated_at = Date.now() / 1000;
          }
        }),

      upsertSpecies: (species) =>
        set((state) => {
          state.species[species.id] = species;
        }),

      removeSpecies: (id) =>
        set((state) => {
          delete state.species[id];
        }),

      pushEvent: (event) =>
        set((state) => {
          state.events.unshift(event);
          if (state.events.length > state.MAX_EVENTS) {
            state.events = state.events.slice(0, state.MAX_EVENTS);
          }
        }),

      clearEvents: () =>
        set((state) => {
          state.events = [];
        }),

      setSystemStatus: (partial) =>
        set((state) => {
          Object.assign(state.status, partial);
        }),

      setWsConnected: (connected) =>
        set((state) => {
          state.wsConnected = connected;
          state.status.connected = connected;
        }),

      selectGenome: (id) =>
        set((state) => {
          state.selectedGenomeId = id;
        }),

      selectSpecies: (id) =>
        set((state) => {
          state.selectedSpeciesId = id;
        }),

      getDominantGenome: () => {
        const { genomes } = get();
        return (
          Object.values(genomes).find((g) => g.status === "dominant") ?? null
        );
      },

      getGenomeAncestry: (id) => {
        const { genomes } = get();
        const ancestry: Genome[] = [];
        let current = genomes[id];
        while (current?.parent_id) {
          const parent = genomes[current.parent_id];
          if (!parent) break;
          ancestry.push(parent);
          current = parent;
        }
        return ancestry;
      },

      getActiveGenomes: () => {
        const { genomes } = get();
        return Object.values(genomes).filter(
          (g) => !["extinct", "archived"].includes(g.status)
        );
      },
    }))
  )
);
