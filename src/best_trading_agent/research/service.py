import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from best_trading_agent.data.adapters import ResearchDataAdapter
from best_trading_agent.domain.models import Report, ResearchRun, RunStatus
from best_trading_agent.llm.providers import ResearchLLMProvider
from best_trading_agent.storage.repositories import ResearchRepository


@dataclass(frozen=True)
class ResearchResult:
    run: ResearchRun
    report: Report


class ResearchService:
    def __init__(
        self,
        repository: ResearchRepository,
        data_adapter: ResearchDataAdapter,
        llm_provider: ResearchLLMProvider,
    ) -> None:
        self._repository = repository
        self._data_adapter = data_adapter
        self._llm_provider = llm_provider

    async def run_research(self, ticker: str) -> ResearchResult:
        normalized_ticker = ticker.upper().strip()
        run = ResearchRun(
            id=f"run-{uuid4().hex}",
            ticker=normalized_ticker,
            created_at=datetime.now(UTC),
        )
        self._repository.save_run(run)
        self._repository.update_run_status(run.id, RunStatus.RUNNING)

        try:
            collected = await self._data_adapter.collect(normalized_ticker, run.id)
            for source in collected.sources:
                self._repository.save_source(source)
            if collected.options_snapshot is not None:
                self._repository.save_options_snapshot(collected.options_snapshot)
            self._repository.add_watchlist_entry(normalized_ticker)
            report = await self._llm_provider.generate_report(
                run.id,
                normalized_ticker,
                collected.sources,
                collected.options_snapshot,
                collected.warnings,
            )
            self._repository.save_report(report)
            final_status = (
                RunStatus.COMPLETED_WITH_WARNINGS if collected.warnings else RunStatus.COMPLETED
            )
            self._repository.update_run_status(run.id, final_status, collected.warnings)
            stored_run = self._repository.get_run(run.id)
            if stored_run is None:
                raise RuntimeError(f"Run disappeared after save: {run.id}")
            return ResearchResult(run=stored_run, report=report)
        except asyncio.CancelledError:
            self._repository.update_run_status(run.id, RunStatus.FAILED)
            raise
        except Exception:
            self._repository.update_run_status(run.id, RunStatus.FAILED)
            raise
