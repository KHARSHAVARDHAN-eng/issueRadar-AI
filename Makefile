.PHONY: dev dev-docker test lint format build docker release help

help:
	@echo "IssueRadar AI Production Automation Targets:"
	@echo "  make dev          - Run development servers (Frontend & Backend)"
	@echo "  make dev-docker   - Start development containers via Docker Compose"
	@echo "  make test         - Run full backend pytest suite"
	@echo "  make lint         - Run ESLint & Ruff code quality checks"
	@echo "  make format       - Format codebase with Prettier & Ruff"
	@echo "  make build        - Compile TypeScript and build web production bundle"
	@echo "  make docker       - Build production Docker Compose stack"
	@echo "  make release      - Run complete release verification pipeline"

dev:
	npm run dev

dev-docker:
	docker compose -f docker-compose.dev.yml up --build

test:
	npm run test:api

lint:
	npm run lint

format:
	npm run format

build:
	npm --prefix apps/web run typecheck
	npm --prefix apps/web run build

docker:
	docker compose -f docker-compose.prod.yml build

release: format lint test build
	@echo "========================================="
	@echo "IssueRadar AI v1.0.0 Release Verification Complete!"
	@echo "========================================="
