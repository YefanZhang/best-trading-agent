import asyncio
from typing import Annotated

import typer

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.llm.providers import DeterministicResearchProvider
from best_trading_agent.research.service import ResearchService
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main(
    ctx: typer.Context,
    database_url: Annotated[
        str,
        typer.Option("--database-url", help="SQLAlchemy database URL."),
    ] = "sqlite+pysqlite:///best-trading-agent.db",
) -> None:
    ctx.obj = {"database_url": database_url}


@app.command()
def research(ctx: typer.Context, ticker: str) -> None:
    session_factory = create_session_factory(ctx.obj["database_url"])
    create_schema(session_factory)
    repository = ResearchRepository(session_factory)
    service = ResearchService(
        repository,
        FixtureResearchDataAdapter(),
        DeterministicResearchProvider(),
    )
    result = asyncio.run(service.run_research(ticker))
    typer.echo(f"{result.run.ticker} {result.run.status.value} {result.run.id}")
    for section in result.report.sections:
        typer.echo(f"- {section.title}: {section.body}")
    for idea in result.report.trade_ideas:
        typer.echo(f"Trade idea: {idea.structure} - {idea.thesis}")


@app.command("runs-list")
def runs_list(ctx: typer.Context) -> None:
    session_factory = create_session_factory(ctx.obj["database_url"])
    create_schema(session_factory)
    repository = ResearchRepository(session_factory)
    for run in repository.list_runs():
        typer.echo(f"{run.id} {run.ticker} {run.status.value}")
