from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from best_trading_agent.domain.models import (
    DataWarning,
    OptionContract,
    OptionsSnapshot,
    SourceDocument,
    SourceType,
)


@dataclass(frozen=True)
class CollectedResearchData:
    sources: list[SourceDocument]
    options_snapshot: OptionsSnapshot | None
    warnings: list[DataWarning]


class ResearchDataAdapter(Protocol):
    async def collect(self, ticker: str, run_id: str) -> CollectedResearchData:
        raise NotImplementedError


class FixtureResearchDataAdapter:
    async def collect(self, ticker: str, run_id: str) -> CollectedResearchData:
        retrieved_at = datetime(2026, 5, 31, tzinfo=UTC)
        upper_ticker = ticker.upper()
        sources = [
            SourceDocument(
                id=f"{run_id}-market",
                run_id=run_id,
                source_type=SourceType.MARKET,
                title=f"{upper_ticker} market snapshot",
                url=None,
                retrieved_at=retrieved_at,
                payload={"price": 125.0, "volume": 42000000},
            ),
            SourceDocument(
                id=f"{run_id}-options",
                run_id=run_id,
                source_type=SourceType.OPTIONS,
                title=f"{upper_ticker} options chain snapshot",
                url=None,
                retrieved_at=retrieved_at,
                payload={"front_expiry": "2026-06-19", "iv_rank": 0.58},
            ),
            SourceDocument(
                id=f"{run_id}-sec",
                run_id=run_id,
                source_type=SourceType.SEC,
                title=f"{upper_ticker} latest filing excerpt",
                url="https://www.sec.gov/",
                retrieved_at=retrieved_at,
                payload={"filing": "10-Q", "summary": "Revenue growth remains positive."},
            ),
            SourceDocument(
                id=f"{run_id}-news",
                run_id=run_id,
                source_type=SourceType.NEWS,
                title=f"{upper_ticker} catalyst feed",
                url="https://example.com/rss",
                retrieved_at=retrieved_at,
                payload={"headline": "Analysts discuss AI demand outlook."},
            ),
        ]
        snapshot = OptionsSnapshot(
            id=f"{run_id}-options-snapshot",
            run_id=run_id,
            ticker=upper_ticker,
            retrieved_at=retrieved_at,
            contracts=[
                OptionContract(
                    symbol=f"{upper_ticker}260619C00130000",
                    expiration="2026-06-19",
                    strike=130.0,
                    option_type="call",
                    bid=4.2,
                    ask=4.5,
                    implied_volatility=0.52,
                    volume=1200,
                    open_interest=8800,
                )
            ],
        )
        warnings = [
            DataWarning(source="news", message="Fixture RSS feed represents partial news coverage")
        ]
        return CollectedResearchData(sources=sources, options_snapshot=snapshot, warnings=warnings)
