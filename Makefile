.PHONY: install test lint typecheck backend frontend

install:
	uv sync --extra dev
	npm install

test:
	uv run pytest
	npm --prefix frontend test -- --run

lint:
	uv run ruff check .

typecheck:
	uv run mypy src
	npm --prefix frontend run typecheck

backend:
	uv run uvicorn best_trading_agent.api.main:create_app --factory --reload

frontend:
	npm --prefix frontend run dev
