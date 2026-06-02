import os

from fastapi import FastAPI

from best_trading_agent.api.routes import router
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.schema import create_schema


def create_app(
    database_url: str = "sqlite+pysqlite:///best-trading-agent.db",
    data_adapter_mode: str | None = None,
) -> FastAPI:
    session_factory = create_session_factory(database_url)
    create_schema(session_factory)
    app = FastAPI(title="best-trading-agent")
    app.state.session_factory = session_factory
    app.state.data_adapter_mode = data_adapter_mode or os.getenv(
        "BEST_TRADING_AGENT_DATA_MODE",
        "fixture",
    )
    app.include_router(router, prefix="/api")
    return app
