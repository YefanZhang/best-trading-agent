# best-trading-agent

Local-first research assistant for US equities and listed options.

## What works in the MVP

- Deterministic fixture-backed equity and options research run.
- Optional live free/public data mode for Yahoo Finance market/options/news and SEC company submissions.
- SQLite persistence for runs, sources, reports, trade ideas, and warnings.
- FastAPI endpoint for starting research runs.
- Typer CLI for starting research runs and listing saved runs.
- React/TypeScript research workbench that calls the API.
- Deterministic simulated trading loop demo with risk checks, simulated fills, state updates,
  and audit records.

The default data adapter is a deterministic development fixture so tests and demos stay fast. Live mode is available behind the same adapter interface when you want current public data.

## Setup

```bash
uv sync --extra dev
npm ci
npm --prefix frontend ci
npx playwright install chromium
```

## Test

```bash
uv run pytest
npm --prefix frontend test -- --run
npm run e2e
```

GitHub Actions runs backend linting, backend typechecking, backend tests, frontend
typechecking, frontend tests, frontend build, and Playwright e2e tests on pull
requests, pushes to `main`, and manual workflow dispatch.

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
uv run best-trading-agent trading-demo NVDA --scenario approved
uv run best-trading-agent trading-demo NVDA --scenario approval-required
uv run best-trading-agent trading-demo NVDA --scenario rejected
```

## Live Data Mode

The default data mode is `fixture`, which returns deterministic local data for fast tests.
To fetch live free/public Yahoo Finance market/options/news data plus SEC company submissions, start the backend with:

```bash
BEST_TRADING_AGENT_DATA_MODE=live \
BEST_TRADING_AGENT_SEC_USER_AGENT="best-trading-agent/0.1 your-email@example.com" \
uv run uvicorn best_trading_agent.api.main:create_app --factory --reload
```

Or run the CLI with:

```bash
BEST_TRADING_AGENT_SEC_USER_AGENT="best-trading-agent/0.1 your-email@example.com" \
uv run best-trading-agent --data-mode live research NVDA
```

Set `BEST_TRADING_AGENT_SEC_USER_AGENT` to an identifying value with a contact email for SEC public data requests. Without an email-style user-agent, `data.sec.gov` may return `403 Forbidden`.

## Scope boundaries

This project does not place trades, integrate with brokers, stream live quotes, or provide financial advice.
