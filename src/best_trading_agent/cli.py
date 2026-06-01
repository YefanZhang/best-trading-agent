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
runs_app = typer.Typer(no_args_is_help=True)
sources_app = typer.Typer(no_args_is_help=True)
app.add_typer(runs_app, name="runs")
app.add_typer(sources_app, name="sources")


def _repository(database_url: str) -> ResearchRepository:
    session_factory = create_session_factory(database_url)
    create_schema(session_factory)
    return ResearchRepository(session_factory)


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
    repository = _repository(ctx.obj["database_url"])
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


@runs_app.command("list")
def nested_runs_list(ctx: typer.Context) -> None:
    for run in _repository(ctx.obj["database_url"]).list_runs():
        typer.echo(f"{run.id} {run.ticker} {run.status.value}")


@runs_app.command("show")
def runs_show(ctx: typer.Context, run_id: str) -> None:
    repository = _repository(ctx.obj["database_url"])
    run = repository.get_run(run_id)
    report = repository.get_report_for_run(run_id)
    if run is None or report is None:
        raise typer.BadParameter(f"Run not found: {run_id}")
    typer.echo(f"{run.id} {run.ticker} {run.status.value}")
    for section in report.sections:
        typer.echo(f"- {section.title}: {section.body}")
    for idea in report.trade_ideas:
        typer.echo(f"Trade idea: {idea.structure} - {idea.thesis}")


@sources_app.command("show")
def sources_show(ctx: typer.Context, source_id: str) -> None:
    source = _repository(ctx.obj["database_url"]).get_source(source_id)
    if source is None:
        raise typer.BadParameter(f"Source not found: {source_id}")
    typer.echo(f"{source.id} {source.source_type.value} {source.title}")
    typer.echo(source.payload)


@app.command("runs-list")
def runs_list(ctx: typer.Context) -> None:
    nested_runs_list(ctx)
