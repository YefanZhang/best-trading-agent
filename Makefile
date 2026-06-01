.PHONY: install test lint typecheck backend frontend

install:
	uv sync --extra dev
	@if [ -f frontend/package.json ]; then \
		npm --prefix frontend ci; \
	fi

test:
	uv run pytest
	@if [ -f frontend/package.json ]; then \
		npm --prefix frontend test -- --run; \
	else \
		echo "frontend/package.json not found; skipping frontend test"; \
	fi

lint:
	uv run ruff check .

typecheck:
	uv run mypy src
	@if [ -f frontend/package.json ]; then \
		npm --prefix frontend run typecheck; \
	else \
		echo "frontend/package.json not found; skipping frontend typecheck"; \
	fi

backend:
	@echo "Backend available after API scaffolding in Task 6"

frontend:
	@if [ -f frontend/package.json ]; then \
		npm --prefix frontend run dev; \
	else \
		echo "frontend/package.json not found; skipping frontend dev"; \
	fi
