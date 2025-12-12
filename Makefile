.PHONY: help up down build restart logs clean test shell dev prod status health install-deps

# Default target
help:
	@echo "CodeDoc - Available Commands:"
	@echo ""
	@echo "  make up              - Start all services in production mode"
	@echo "  make down            - Stop all services"
	@echo "  make build           - Build Docker images"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - View logs (follow mode)"
	@echo "  make clean           - Stop services and remove volumes"
	@echo ""
	@echo "  make dev             - Start services in development mode"
	@echo "  make prod            - Start services in production mode"
	@echo "  make status          - Show running containers"
	@echo "  make health          - Check backend health"
	@echo ""
	@echo "  make shell           - Open bash shell in backend container"
	@echo "  make test            - Run backend tests"
	@echo "  make install-deps    - Install backend dependencies"
	@echo ""
	@echo "  make compile-ext     - Compile VS Code extension"
	@echo "  make package-ext     - Package VS Code extension (.vsix)"
	@echo ""

# Production commands
up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

restart: down up

logs:
	docker compose logs -f

clean:
	docker compose down -v
	@echo "Cleaned up containers and volumes"

# Development commands
dev:
	docker compose -f docker-compose.dev.yml up

prod:
	docker compose up -d

status:
	docker compose ps

# Backend commands
shell:
	docker compose exec backend bash

test:
	docker compose exec backend python -m pytest tests/ -v

install-deps:
	docker compose exec backend pip install -r requirements.txt

# Health check
health:
	@echo "Checking backend health..."
	@curl -s http://localhost:5001/api/config || echo "Backend not responding"

# Extension commands
compile-ext:
	cd vscode-extension && npm run compile

package-ext:
	cd vscode-extension && npm run package
