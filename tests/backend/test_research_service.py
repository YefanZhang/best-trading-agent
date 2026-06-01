import pytest

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.domain.models import RunStatus
from best_trading_agent.llm.providers import DeterministicResearchProvider
from best_trading_agent.research.service import ResearchService
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema


@pytest.mark.asyncio
async def test_research_service_persists_completed_run_with_warnings() -> None:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_schema(session_factory)
    repo = ResearchRepository(session_factory)
    service = ResearchService(repo, FixtureResearchDataAdapter(), DeterministicResearchProvider())

    result = await service.run_research("nvda")

    stored_run = repo.get_run(result.run.id)
    stored_report = repo.get_report_for_run(result.run.id)
    sources = repo.list_sources(result.run.id)

    assert stored_run is not None
    assert stored_run.ticker == "NVDA"
    assert stored_run.status is RunStatus.COMPLETED_WITH_WARNINGS
    assert len(sources) == 4
    assert stored_report is not None
    assert stored_report.trade_ideas[0].structure == "Defined-risk call spread"
