# best-trading-agent

Local-first research assistant for US equities and listed options.

## What works in the MVP

- Deterministic fixture-backed equity and options research run.
- SQLite persistence for runs, sources, reports, trade ideas, and warnings.
- FastAPI endpoint for starting research runs.
- Typer CLI for starting research runs and listing saved runs.
- React/TypeScript research workbench that calls the API.

The current data adapter is a deterministic development fixture. Live free/public adapters can be added behind the same adapter interface.

## Setup

```bash
uv sync --extra dev
npm --prefix frontend ci
```

## Test

```bash
uv run pytest
npm --prefix frontend test -- --run
```

## Run backend

```bash
uv run uvicorn best_trading_agent.api.main:create_app --factory --reload
```

## Run frontend

```bash
npm --prefix frontend run dev
```

## Run CLI

```bash
uv run best-trading-agent research NVDA
uv run best-trading-agent runs-list
```

## Live data mode

The default data mode is `fixture`, which returns deterministic local data for fast tests.
To fetch live free/public Yahoo Finance market, options, and news data, start the backend with:

```bash
BEST_TRADING_AGENT_DATA_MODE=live uv run uvicorn best_trading_agent.api.main:create_app --factory --reload
```

Or run the CLI with:

```bash
uv run best-trading-agent --data-mode live research NVDA
```

## Scope boundaries

This project does not place trades, integrate with brokers, stream live quotes, or provide financial advice.
