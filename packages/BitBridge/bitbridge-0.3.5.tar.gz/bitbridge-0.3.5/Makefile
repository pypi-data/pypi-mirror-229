.PHONY: help test lint format up down

.DEFAULT: help
help:
	@echo "make test"
	@echo "       run tests"
	@echo "make lint"
	@echo "       run linter"
	@echo "make format"
	@echo "       run formatter"
	@echo "make up"
	@echo "       run docker-compose up --build -d"
	@echo "make down"
	@echo "       run docker-compose down"

test:
	@bash ./scripts/test.sh

lint:
	@bash ./scripts/lint.sh

format:
	@bash ./scripts/format.sh


up:
	@docker compose up --build -d

down:
	@docker compose down
