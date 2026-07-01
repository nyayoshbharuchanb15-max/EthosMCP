include .env
export

# ── Project ─────────────────────────────────────────────────────────
.PHONY: help install build test lint clean dev up down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd mcp-server && npm ci
	cd orchestrator && pip install -r requirements.txt
	cd audit-engines && pip install -r requirements.txt

build: ## Build TypeScript MCP server
	cd mcp-server && npm run build

test: ## Run all tests
	cd mcp-server && npm test
	cd orchestrator && python -m pytest tests/ -v
	cd audit-engines && python -m pytest tests/ -v
	cd .. && python -m pytest tests/ -v

test-unit: ## Run unit tests only
	python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	python -m pytest tests/integration/ -v

lint: ## Lint all code
	cd mcp-server && npm run lint
	cd orchestrator && ruff check .
	cd audit-engines && ruff check .

check: ## Type check
	cd mcp-server && npm run typecheck

clean: ## Clean build artifacts
	rm -rf mcp-server/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

dev: ## Start development environment
	docker compose -f deploy/docker-compose.yml up --build -d

up: dev ## Alias for dev

down: ## Stop all containers
	docker compose -f deploy/docker-compose.yml down

logs: ## Tail logs
	docker compose -f deploy/docker-compose.yml logs -f

prod: ## Start production stack
	docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.prod.yml up --build -d

migration: ## Run Alembic migrations
	cd orchestrator && alembic upgrade head

seed: ## Seed Neo4j with sample data
	cat db/neo4j/seed.cypher | docker compose exec -T neo4j cypher-shell -u neo4j -p secure_password_change_me

reset-db: ## Reset all databases
	docker compose down -v && docker compose up -d

health: ## Check service health
	@echo "MCP Server:   $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/health || echo 'DOWN')"
	@echo "Orchestrator: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/health || echo 'DOWN')"
	@echo "Postgres:     $$(docker compose exec postgres pg_isready -U governance_admin -q && echo 'UP' || echo 'DOWN')"
	@echo "Neo4j:        $$(docker compose exec neo4j cypher-shell -u neo4j -p secure_password_change_me 'RETURN 1' >/dev/null 2>&1 && echo 'UP' || echo 'DOWN')"
