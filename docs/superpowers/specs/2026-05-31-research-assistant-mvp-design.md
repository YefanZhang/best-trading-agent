# Research Assistant MVP Design

Date: 2026-05-31
Project: best-trading-agent

## Goal

Build `best-trading-agent` from scratch as a local-first research assistant for US equities and listed options. The first version helps a user generate evidence-first research memos and clearly separated options trade ideas using free/public data sources only.

The web UI is the primary long-term interaction surface. The CLI is a secondary interface for repeatable runs and scripting.

## Architecture

The MVP uses a mixed stack:

- Python backend for data ingestion, options/equity analysis, SQLite persistence, agent orchestration, report generation, API, and CLI.
- TypeScript frontend for the primary research workspace.
- FastAPI for the local API service.
- REST endpoints for stable resources such as tickers, runs, reports, sources, and settings.
- Server-sent events for long-running research progress.
- SQLite for local persistence.
- A provider-neutral LLM interface so OpenAI, local models, or other providers can be added without changing core research flow.

The CLI and web API call the same backend application services. That keeps the behavior consistent across both surfaces.

## Data Sources

The MVP uses only free/public data sources:

- US equity market data from public Python libraries or APIs where available.
- Listed options chain data from public/free sources where available.
- SEC filings from public SEC endpoints.
- News and catalyst data from RSS feeds or other public sources.

Each data adapter returns structured data with:

- Source name.
- Retrieval timestamp.
- Raw or normalized payload reference.
- Warnings for missing, stale, or partial data.

Research runs should continue when a non-critical source fails. The final report must show visible missing-data notes rather than hiding gaps.

## Persistence

SQLite persists:

- Tickers and watchlist entries.
- Research runs and run status.
- Source documents and retrieval metadata.
- Options snapshots.
- Generated report sections.
- Trade idea sections.
- Warnings and audit metadata.

Reports are generated from stored source snapshots so the user can inspect what evidence was available at generation time.

## Web Workflow

The primary web experience is a research workbench:

1. Pick or enter a ticker.
2. Choose the initial research mode: equity plus options research.
3. Start a research run.
4. Watch progress while data sources are fetched, normalized, summarized, and assembled.
5. Read a generated memo with evidence-first sections.
6. Review a separate trade ideas section.
7. Open source drilldowns for filings, news items, quote data, and options-chain evidence.
8. Revisit saved runs from ticker history.

The workbench layout includes:

- Watchlist/sidebar area.
- Ticker research command/search area.
- Market snapshot panel.
- Catalyst/source feed panel.
- Generated memo area.
- Source drawer for evidence inspection.
- Settings area for provider configuration.

## CLI Workflow

The CLI mirrors the backend workflow and stores results in the same SQLite database. Initial commands:

- `best-trading-agent research TICKER`
- `best-trading-agent runs list`
- `best-trading-agent runs show RUN_ID`
- `best-trading-agent sources show SOURCE_ID`

The CLI is not a separate implementation path. It calls the same application services used by the FastAPI routes.

## Report Shape

Generated reports are evidence-first and include:

- Market snapshot.
- Fundamentals and filing highlights.
- Catalyst and news summary.
- Options context, including expiries, chains, implied volatility, skew, and notable volume where available.
- Bull, base, and bear framing.
- Key risks and missing-data warnings.
- Source citations and audit metadata.
- A clearly separated trade ideas section.

Trade ideas can propose possible options structures with assumptions and risk notes. The product does not execute trades and does not present ideas as financial advice.

## MVP Scope

In scope:

- US equities and listed options research.
- Free/public data only.
- Local SQLite persistence.
- Provider-neutral LLM adapter.
- One concrete development provider stub for deterministic testing.
- Configuration slot for real model providers.
- TypeScript web workbench as the primary UI.
- CLI as a secondary interface.
- Evidence-first reports plus separated trade ideas.
- Source citation and audit trail where possible.

Out of scope:

- Broker integration or order execution.
- Live streaming quotes.
- Portfolio management.
- Paid data vendor integration.
- Multi-user authentication.
- Cloud deployment.
- Backtesting.
- Automated trading.
- Financial-advice claims.

## Error Handling

Data-source failures are represented as structured warnings on the run and report. A research run can finish with `completed`, `completed_with_warnings`, or `failed` status.

The UI and CLI both expose:

- Which source failed.
- Whether the report omitted a section because of missing data.
- Retrieval timestamps.
- Any adapter warnings used during report generation.

LLM/provider failures should fail only the report-generation step when raw source collection succeeded. Stored source snapshots remain available for retry.

## Testing Strategy

Backend tests cover:

- Data adapter contracts.
- SQLite repositories.
- Research-run orchestration.
- Report assembly from stored source snapshots.
- Provider-neutral LLM interface behavior.
- Partial failure handling.

Frontend tests cover:

- Empty ticker state.
- Run configuration state.
- Running/progress state.
- Completed report state.
- Completed-with-warnings state.
- Failed run state.
- Report history and source drawer behavior.

End-to-end tests cover:

- One mocked research run from the web UI.
- One mocked research run from the CLI.

Tests should use deterministic provider stubs and fixture data so the core workflow does not depend on live public data availability.

## Implementation Notes

Implementation should be split into independent tasks suitable for subagent dispatch:

- Repository scaffold and developer tooling.
- Backend domain model, SQLite schema, and repositories.
- Data adapter interfaces and initial free/public adapters.
- Research orchestration and report assembly.
- Provider-neutral LLM interface and deterministic stub provider.
- FastAPI routes and SSE progress stream.
- CLI commands.
- TypeScript frontend scaffold and research workbench.
- Integration tests and end-to-end smoke tests.

