from typing import Any

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.domain.models import DataWarning, Report, ResearchRun
from best_trading_agent.llm.providers import DeterministicResearchProvider
from best_trading_agent.research.service import ResearchService
from best_trading_agent.storage.repositories import ResearchRepository

router = APIRouter()


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


@router.post("/runs", status_code=status.HTTP_201_CREATED)
async def create_run(payload: RunRequest, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    service = ResearchService(
        repository,
        FixtureResearchDataAdapter(),
        DeterministicResearchProvider(),
    )
    result = await service.run_research(payload.ticker)
    return {"run": _run_to_dict(result.run), "report": _report_to_dict(result.report)}


@router.get("/runs")
async def list_runs(request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    return {"runs": [_run_to_dict(run) for run in repository.list_runs()]}
