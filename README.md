# MYCELIUM — Evolutionary Software Runtime

<img width="1600" height="900" alt="WhatsApp Image 2026-05-11 at 2 31 33 PM" src="https://github.com/user-attachments/assets/3fdde1cc-5218-4401-b5d1-d8b8e0399e90" />



> A production-grade evolutionary software runtime where software behaves like a living adaptive organism.

MYCELIUM is an autonomous evolutionary computation platform that continuously generates, mutates, benchmarks, evaluates, and evolves executable software organisms under real selection pressure.

This is not:

* an AI wrapper
* a chatbot framework
* a toy orchestration layer
* a static benchmarking system
* a fake “self-improving AI” demo

MYCELIUM is an event-driven distributed runtime for computational evolution.

---

# Core Idea

Traditional software is static.

MYCELIUM treats software as:

* evolving genomes
* adaptive lineages
* competing species
* persistent organisms

The runtime continuously:

1. Generates offspring
2. Applies mutations
3. Benchmarks variants
4. Scores fitness
5. Applies extinction pressure
6. Preserves dominant lineages
7. Evolves future generations

The result is a continuously adapting software ecosystem.

---

# Features

## Evolutionary Runtime

* Continuous generation cycles
* Genome reproduction
* AST-aware mutation engine
* Selection pressure
* Species divergence
* Extinction events
* Adaptive mutation rates
* Fitness-driven evolution

## Distributed Architecture

* FastAPI backend
* Redis pub/sub event bus
* PostgreSQL persistence
* Distributed worker runtime
* WebSocket event streaming
* Dockerized execution infrastructure

## Genome System

* Executable software genomes
* Mutation lineage tracking
* Parent-child ancestry
* Species clustering
* Generation history
* Trait vectors
* Weighted fitness scoring
* Persistent evolutionary memory

## Mutation Engine

* AST-based transformations
* Concurrency rewrites
* Memoization insertion
* Algorithm substitutions
* Execution pipeline rewrites
* Async transformations
* Structural code mutation
* Syntax-safe mutation validation

## Benchmarking + Fitness

* Deterministic benchmark execution
* Latency scoring
* Memory scoring
* CPU utilization analysis
* Stability metrics
* Resource efficiency scoring
* Composite weighted fitness vectors

## Real-Time Evolution Observatory

* Live lineage visualization
* Species graphs
* Mutation pulse streaming
* Evolution telemetry
* Dominant lineage tracking
* Ecosystem heatmaps
* Generation timelines
* Real-time event observability

---

# System Architecture

```txt
                            ┌─────────────────────┐
                            │      Frontend       │
                            │ Evolution Observatory│
                            └──────────┬──────────┘
                                       │
                             WebSocket Event Streams
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
          ┌─────────▼─────────┐               ┌──────────▼──────────┐
          │      Backend      │               │      Redis Bus       │
          │ FastAPI Runtime   │◄─────────────►│ Pub/Sub + Task Queue │
          └─────────┬─────────┘               └──────────┬──────────┘
                    │                                     │
                    │                             Evolution Events
                    │                                     │
         ┌──────────▼──────────┐              ┌──────────▼──────────┐
         │     PostgreSQL      │              │   Evolution Worker   │
         │ Genome Persistence  │              │ Mutation + Fitness   │
         └─────────────────────┘              └──────────┬──────────┘
                                                         │
                                              ┌──────────▼──────────┐
                                              │ Sandbox Execution    │
                                              │ Isolated Benchmarking│
                                              └──────────────────────┘
```

---

# Repository Structure

```txt
mycelium/
├── backend/              FastAPI runtime + orchestration layer
│   ├── app/
│   │   ├── api/          REST + WebSocket endpoints
│   │   ├── core/         Config, logging, Redis, settings
│   │   ├── db/           Async SQLAlchemy engine/session
│   │   ├── models/       Persistence models
│   │   ├── services/     Evolution orchestration services
│   │   ├── workers/      Background orchestration tasks
│   │   └── evolution/    Core evolutionary runtime
│   └── alembic/          Database migrations
│
├── worker/               Distributed evolution workers
│   └── src/
│       ├── mutations/    AST mutation engine
│       ├── benchmark/    Benchmark runtime
│       ├── executors/    Sandbox execution layer
│       ├── fitness/      Fitness scoring engine
│       ├── species/      Species clustering
│       └── runtime/      Evolution scheduling
│
├── frontend/             Next.js evolution observatory
│   └── src/
│       ├── app/          Pages/layouts
│       ├── components/   Visualization components
│       ├── hooks/        WebSocket hooks
│       ├── store/        Zustand ecosystem state
│       ├── graphs/       Lineage/species rendering
│       └── lib/          API clients
│
├── shared/               Shared runtime protocols
│   ├── events/           Event schemas + envelopes
│   ├── genome_types/     Genome wire formats
│   └── protocols/        Cross-service contracts
│
├── infra/                Docker, Nginx, deployment
├── scripts/              Bootstrap and tooling
├── tests/                Runtime and integration tests
└── docs/                 Architecture and protocol docs
```

---

# Quick Start

## Requirements

* Docker Desktop
* Docker Compose
* Python 3.12+
* Node.js 22+
* GNU Make (optional)

---

## Bootstrap

```bash
git clone https://github.com/sreerevanth/mycelium.git

cd mycelium

cp .env.example .env

docker compose up --build
```

---

# Services

| Service    | Port | Description           |
| ---------- | ---- | --------------------- |
| Frontend   | 3000 | Evolution observatory |
| Backend    | 8000 | FastAPI runtime       |
| PostgreSQL | 5432 | Genome persistence    |
| Redis      | 6379 | Event bus + queues    |

---

# API Endpoints

## REST API

```txt
http://localhost:8000/api/v1/
```

## OpenAPI Docs

```txt
http://localhost:8000/docs
```

## WebSocket Streams

```txt
ws://localhost:8000/ws/events
ws://localhost:8000/ws/status
```

---

# Event Protocol

All runtime events use a standardized envelope:

```json
{
  "id": "uuid",
  "type": "genome.mutated",
  "timestamp": 1700000000,
  "source": "mutation-engine",
  "session_id": "cycle-uuid",
  "payload": {
    "genome_id": "mx_441",
    "parent_id": "mx_102",
    "mutation_type": "async_rewrite",
    "fitness_delta": 0.14
  }
}
```

---

# Example Runtime Events

```txt
genome.created
genome.mutated
species.spawned
species.extinct
generation.advanced
benchmark.completed
mutation.failed
fitness.spike_detected
dominant_species.changed
offspring.rejected
```

---

# Development

## Start Runtime

```bash
docker compose up --build
```

## Stop Runtime

```bash
docker compose down
```

## Reset Runtime

```bash
docker compose down -v
```

## View Logs

```bash
docker compose logs -f
```

## Backend Shell

```bash
docker compose exec backend bash
```

## Worker Shell

```bash
docker compose exec worker bash
```

---

# Engineering Principles

MYCELIUM prioritizes:

* deterministic evolution
* event-driven architecture
* observable runtime behavior
* distributed scalability
* mutation traceability
* ecosystem continuity
* fault isolation
* runtime introspection

This project intentionally treats software evolution as:

* systems engineering
* computational ecology
* evolutionary computation
* runtime infrastructure

—not as “AI magic.”

---

# Contributing

Contributions are welcome from:

* systems engineers
* compiler/runtime developers
* distributed systems engineers
* AI/ML engineers
* visualization engineers
* evolutionary computation researchers

## Contribution Flow

1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

Example:

```bash
git checkout -b feat/ast-mutation-engine
```

---

# Code Style

## Backend

* Python 3.12
* Async-first architecture
* Ruff + Black formatting
* Strict typing

## Frontend

* TypeScript strict mode
* Zustand state management
* Functional React patterns

---

# Security

MYCELIUM executes generated software variants.

Sandbox isolation is mandatory.

The runtime uses:

* Docker sandboxing
* execution timeouts
* resource quotas
* isolated filesystems
* restricted execution policies

Never run untrusted genomes outside sandbox infrastructure.

---

# Roadmap

Planned research directions:

* self-evolving schedulers
* recursive runtime optimization
* adaptive mutation weighting
* distributed evolutionary swarms
* GPU benchmark evolution
* WASM execution targets
* reinforcement-guided mutation pressure
* multi-objective ecosystem balancing

---

# Code of Conduct

This project follows a collaborative, respectful engineering culture.

Expected behavior:

* constructive feedback
* respectful discussion
* transparent collaboration
* technical honesty
* curiosity-driven experimentation

Harassment, toxicity, or malicious contributions will not be tolerated.

---

# License

MIT License

Copyright (c) 2026 Sreerevanth

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software.

See `LICENSE` for full license text.

---

# Final Vision

MYCELIUM is not intended to become:

* another coding assistant
* another orchestration framework
* another SaaS wrapper

The long-term vision is:

> a persistent computational ecosystem where software continuously evolves under real environmental pressure.

A runtime where software behaves less like static code—
and more like living adaptive organisms.
