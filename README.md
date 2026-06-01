# best-trading-agent

Local-first research assistant for US equities and listed options.

## Development

```bash
uv sync --extra dev
npm install
uv run pytest
```

The backend will expose a FastAPI API and Typer CLI. The frontend will be a TypeScript workbench.
Task 6 should add the CLI console script and backend dev server target when those modules exist.
