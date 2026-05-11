# MYCELIUM — Evolutionary Software Runtime
<img width="1600" height="900" alt="WhatsApp Image 2026-05-11 at 2 31 33 PM" src="https://github.com/user-attachments/assets/2c4e1ab8-e37c-4aa1-afcb-25d7bfc6c552" />



An autonomous evolutionary runtime that continuously generates, mutates, benchmarks, and evolves software implementations. Not an AI wrapper. A runtime + execution substrate + evolutionary engine.

## Architecture

```
mycelium/
├── backend/          FastAPI — REST API + WebSocket event server
│   ├── app/
│   │   ├── api/      HTTP + WebSocket endpoints
│   │   ├── core/     Config, logging, Redis client
│   │   ├── db/       SQLAlchemy async session
│   │   ├── models/   PostgreSQL models (Phase 2)
│   │   ├── services/ Evolution services (Phases 3–8)
│   │   └── workers/  Background tasks
│   └── alembic/      Database migrations
├── worker/           Evolution worker process
│   └── src/
│       ├── executors/    Docker sandbox execution (Phase 4)
│       ├── mutations/    Mutation engine (Phase 3)
│       ├── benchmark/    Benchmark runner (Phase 5)
│       └── fitness/      Fitness scoring (Phase 5)
├── frontend/         Next.js 15 visualization dashboard
│   └── src/
│       ├── app/      Pages and layouts
│       ├── components/ React components (Phase 7)
│       ├── hooks/    WebSocket + data hooks
│       ├── store/    Zustand state (evolution state)
│       └── lib/      API client
├── shared/           Protocol definitions shared across services
│   ├── events/       Event types + envelope format
│   └── types/        Genome wire formats
└── infra/            Docker, Nginx, scripts
```

## Quick Start

```bash
# First-time setup
make bootstrap

# Or manually:
cp .env.example .env
docker compose up -d postgres redis
docker compose run --rm backend python -c \
  "import asyncio; from app.db import init_db; asyncio.run(init_db())"
docker compose up -d
```

## Services

| Service  | Port | Description |
|----------|------|-------------|
| Frontend | 3000 | Next.js visualization dashboard |
| Backend  | 8000 | FastAPI REST + WebSocket API |
| Postgres | 5432 | Genome + evolution database |
| Redis    | 6379 | Event bus + task queue |

## API

- REST API: `http://localhost:8000/api/v1/`
- Docs: `http://localhost:8000/docs`
- WebSocket events: `ws://localhost:8000/ws/events`
- WebSocket status: `ws://localhost:8000/ws/status`

## Event Protocol

All events use the `EventEnvelope` format from `shared/events/envelope.py`:

```json
{
  "id": "uuid",
  "type": "genome.created",
  "timestamp": 1700000000.0,
  "source": "evolution-engine",
  "session_id": "cycle-uuid",
  "payload": { ... }
}
```

## Build Phases

- **Phase 1** ✅ Monorepo foundation (this phase)
- **Phase 2** Genome database system
- **Phase 3** Evolution engine + mutation operators
- **Phase 4** Docker sandbox execution
- **Phase 5** Fitness scoring system
- **Phase 6** WebSocket event system
- **Phase 7** Frontend visualization
- **Phase 8** Autonomous evolution loop
- **Phase 9** Distributed evolution protocol

## Development

```bash
make logs-backend    # tail backend
make logs-worker     # tail worker
make shell-backend   # bash into backend container
make migrate         # run alembic migrations
make migrate-new MSG="add genome index"
make queue-depth     # check Redis task queue
```
