# Makefile for Docker operations

.PHONY: help build up down restart logs clean dev prod test

help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start containers (production)"
	@echo "  make down        - Stop containers"
	@echo "  make restart     - Restart containers"
	@echo "  make logs        - View logs"
	@echo "  make clean       - Remove containers, volumes, and images"
	@echo "  make dev         - Start development environment"
	@echo "  make prod        - Start production environment"
	@echo "  make test        - Run tests in container"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all
	rm -rf exports/* logs/*

dev:
	docker-compose -f docker-compose.dev.yml up

prod:
	docker-compose up -d

test:
	docker-compose exec backend python -m pytest tests/ -v

shell:
	docker-compose exec backend /bin/bash

ps:
	docker-compose ps
