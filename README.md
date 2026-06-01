# best-trading-agent

Local-first research assistant for US equities and listed options.

## Development

```bash
uv sync --extra dev
npm --prefix frontend ci
uv run pytest
```

The backend exposes a FastAPI API and Typer CLI. The frontend is a TypeScript workbench.
