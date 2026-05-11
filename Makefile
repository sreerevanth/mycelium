.PHONY: help bootstrap up down logs shell-backend shell-worker migrate reset clean

COMPOSE = docker compose
BACKEND = $(COMPOSE) exec backend
WORKER  = $(COMPOSE) exec worker

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

bootstrap: ## First-time setup: build images, run migrations, start services
	@bash infra/scripts/bootstrap.sh

up: ## Start all services
	$(COMPOSE) up -d

up-dev: ## Start services with live logs
	$(COMPOSE) up

down: ## Stop all services
	$(COMPOSE) down

down-volumes: ## Stop all services and remove volumes (DESTROYS DATA)
	$(COMPOSE) down -v

logs: ## Tail logs from all services
	$(COMPOSE) logs -f

logs-backend: ## Tail backend logs
	$(COMPOSE) logs -f backend

logs-worker: ## Tail worker logs
	$(COMPOSE) logs -f worker

logs-frontend: ## Tail frontend logs
	$(COMPOSE) logs -f frontend

shell-backend: ## Open shell in backend container
	$(BACKEND) bash

shell-worker: ## Open shell in worker container
	$(WORKER) bash

migrate: ## Run Alembic migrations
	$(COMPOSE) run --rm backend alembic upgrade head

migrate-new: ## Create new migration (make migrate-new MSG="description")
	$(COMPOSE) run --rm backend alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback one migration
	$(COMPOSE) run --rm backend alembic downgrade -1

reset: down-volumes ## Full reset - destroy all data and restart
	$(COMPOSE) up -d postgres redis
	sleep 5
	$(COMPOSE) run --rm backend alembic upgrade head
	$(COMPOSE) up -d

test-backend: ## Run backend tests
	$(BACKEND) pytest tests/ -v

build: ## Rebuild all service images
	$(COMPOSE) build --parallel

ps: ## Show running services
	$(COMPOSE) ps

queue-depth: ## Show Redis task queue depth
	$(COMPOSE) exec redis redis-cli zcard mycelium:tasks

clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
