# mycelium/shared/events/types.py
# Canonical event type definitions shared across backend, worker, and frontend protocol

from enum import Enum


class EventType(str, Enum):
    # ─── GENOME LIFECYCLE ─────────────────────────────────────────────────────
    GENOME_CREATED = "genome.created"
    GENOME_MUTATED = "genome.mutated"
    GENOME_PROMOTED = "genome.promoted"
    GENOME_DEMOTED = "genome.demoted"
    GENOME_EXTINCT = "genome.extinct"
    GENOME_ARCHIVED = "genome.archived"

    # ─── EVOLUTION CYCLE ──────────────────────────────────────────────────────
    CYCLE_STARTED = "cycle.started"
    CYCLE_COMPLETED = "cycle.completed"
    CYCLE_ABORTED = "cycle.aborted"

    # ─── MUTATION EVENTS ──────────────────────────────────────────────────────
    MUTATION_QUEUED = "mutation.queued"
    MUTATION_STARTED = "mutation.started"
    MUTATION_COMPLETED = "mutation.completed"
    MUTATION_FAILED = "mutation.failed"

    # ─── BENCHMARK EVENTS ─────────────────────────────────────────────────────
    BENCHMARK_STARTED = "benchmark.started"
    BENCHMARK_PROGRESS = "benchmark.progress"
    BENCHMARK_COMPLETED = "benchmark.completed"
    BENCHMARK_FAILED = "benchmark.failed"

    # ─── EXECUTION SANDBOX ────────────────────────────────────────────────────
    EXECUTION_STARTED = "execution.started"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_TIMEOUT = "execution.timeout"
    EXECUTION_CRASHED = "execution.crashed"

    # ─── FITNESS ──────────────────────────────────────────────────────────────
    FITNESS_SCORED = "fitness.scored"
    FITNESS_REGRESSION = "fitness.regression"
    FITNESS_BREAKTHROUGH = "fitness.breakthrough"

    # ─── SPECIES ──────────────────────────────────────────────────────────────
    SPECIES_FORMED = "species.formed"
    SPECIES_MERGED = "species.merged"
    SPECIES_EXTINCT = "species.extinct"

    # ─── SYSTEM ───────────────────────────────────────────────────────────────
    WORKER_ONLINE = "worker.online"
    WORKER_OFFLINE = "worker.offline"
    SYSTEM_ALERT = "system.alert"
    SYSTEM_STATUS = "system.status"
    SYSTEM_CONNECTED = "system.connected"


class MutationType(str, Enum):
    ALGORITHM_REPLACEMENT = "algorithm_replacement"
    CONCURRENCY_MUTATION = "concurrency_mutation"
    MEMORY_OPTIMIZATION = "memory_optimization"
    STRUCTURAL_MUTATION = "structural_mutation"
    STRATEGY_MUTATION = "strategy_mutation"
    CROSSOVER = "crossover"
    RANDOM_PERTURBATION = "random_perturbation"


class GenomeStatus(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    BENCHMARKING = "benchmarking"
    MUTATING = "mutating"
    DOMINANT = "dominant"
    DEPRECATED = "deprecated"
    EXTINCT = "extinct"
    ARCHIVED = "archived"


class BenchmarkStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class WorkerStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    DRAINING = "draining"
    OFFLINE = "offline"

# Additions for system-level events emitted by backend WS layer
# (appended to avoid re-writing enum body above)
