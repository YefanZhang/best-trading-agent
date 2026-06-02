import asyncio
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from best_trading_agent.data.adapters import build_research_data_adapter
from best_trading_agent.domain.models import (
    DataWarning,
    Report,
    ResearchRun,
    RunStatus,
    SourceDocument,
)
from best_trading_agent.llm.providers import DeterministicResearchProvider
from best_trading_agent.research.service import ResearchService
from best_trading_agent.storage.repositories import ResearchRepository

router = APIRouter()
_EVENT_POLL_INTERVAL_SECONDS = 0.01
_TERMINAL_STATUSES = {
    RunStatus.COMPLETED,
    RunStatus.COMPLETED_WITH_WARNINGS,
    RunStatus.FAILED,
}


class RunRequest(BaseModel):
    ticker: str


def _warning_to_dict(warning: DataWarning) -> dict[str, str]:
    return {
        "source": warning.source,
        "message": warning.message,
    }


def _run_to_dict(run: ResearchRun) -> dict[str, Any]:
    return {
        "id": run.id,
        "ticker": run.ticker,
        "created_at": run.created_at.isoformat(),
        "status": run.status.value,
        "warnings": [_warning_to_dict(warning) for warning in run.warnings],
    }


def _report_to_dict(report: Report) -> dict[str, Any]:
    return {
        "id": report.id,
        "run_id": report.run_id,
        "sections": [
            {
                "title": section.title,
                "body": section.body,
                "source_ids": section.source_ids,
            }
            for section in report.sections
        ],
        "trade_ideas": [
            {
                "structure": idea.structure,
                "thesis": idea.thesis,
                "risk_notes": idea.risk_notes,
                "source_ids": idea.source_ids,
            }
            for idea in report.trade_ideas
        ],
        "warnings": [_warning_to_dict(warning) for warning in report.warnings],
    }


def _source_to_dict(source: SourceDocument) -> dict[str, Any]:
    return {
        "id": source.id,
        "run_id": source.run_id,
        "source_type": source.source_type.value,
        "title": source.title,
        "url": source.url,
        "retrieved_at": source.retrieved_at.isoformat(),
        "payload": source.payload,
    }


@router.post("/runs", status_code=status.HTTP_201_CREATED)
async def create_run(payload: RunRequest, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    service = ResearchService(
        repository,
        build_research_data_adapter(request.app.state.data_adapter_mode),
        DeterministicResearchProvider(),
    )
    result = await service.run_research(payload.ticker)
    return {"run": _run_to_dict(result.run), "report": _report_to_dict(result.report)}


@router.get("/runs")
async def list_runs(request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    return {"runs": [_run_to_dict(run) for run in repository.list_runs()]}


@router.get("/runs/{run_id}")
async def get_run(run_id: str, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    run = repository.get_run(run_id)
    report = repository.get_report_for_run(run_id)
    if run is None or report is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"run": _run_to_dict(run), "report": _report_to_dict(report)}


@router.get("/runs/{run_id}/sources")
async def list_run_sources(run_id: str, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    return {"sources": [_source_to_dict(source) for source in repository.list_sources(run_id)]}


@router.get("/sources/{source_id}")
async def get_source(source_id: str, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    source = repository.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"source": _source_to_dict(source)}


@router.get("/runs/{run_id}/events")
async def run_events(run_id: str, request: Request) -> StreamingResponse:
    repository = ResearchRepository(request.app.state.session_factory)
    run = repository.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    async def stream() -> AsyncIterator[str]:
        last_status: RunStatus | None = None
        while True:
            if await request.is_disconnected():
                break

            current_run = repository.get_run(run_id)
            if current_run is None:
                break

            if current_run.status != last_status:
                last_status = current_run.status
                yield f"event: status\ndata: {current_run.status.value}\n\n"

            if current_run.status in _TERMINAL_STATUSES:
                break

            await asyncio.sleep(_EVENT_POLL_INTERVAL_SECONDS)

    return StreamingResponse(stream(), media_type="text/event-stream")
