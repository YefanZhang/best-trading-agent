from dataclasses import dataclass

import pytest

from best_trading_agent.data.adapters import (
    FixtureResearchDataAdapter,
    YFinanceResearchDataAdapter,
    build_research_data_adapter,
)
from best_trading_agent.llm.providers import DeterministicResearchProvider


class FakeFrame:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self._records = records

    def to_dict(self, orient: str) -> list[dict[str, object]]:
        assert orient == "records"
        return self._records


@dataclass(frozen=True)
class FakeOptionChain:
    calls: FakeFrame
    puts: FakeFrame


class FakeYFinanceTicker:
    fast_info = {
        "last_price": 501.25,
        "currency": "USD",
        "day_volume": 12_345_678,
        "market_cap": 1_000_000_000,
    }
    info = {
        "shortName": "NVIDIA Corporation",
        "sector": "Technology",
        "trailingPE": 42.5,
    }
    options = ["2026-06-19"]
    news = [
        {
            "title": "Nvidia shares move after analyst note",
            "link": "https://finance.yahoo.com/news/example",
            "publisher": "Yahoo Finance",
        }
    ]

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker

    def option_chain(self, expiration: str) -> FakeOptionChain:
        return FakeOptionChain(
            calls=FakeFrame(
                [
                    {
                        "contractSymbol": f"{self.ticker}260619C00130000",
                        "strike": 130.0,
                        "bid": 4.2,
                        "ask": 4.5,
                        "impliedVolatility": 0.52,
                        "volume": 1200,
                        "openInterest": 8800,
                    }
                ]
            ),
            puts=FakeFrame(
                [
                    {
                        "contractSymbol": f"{self.ticker}260619P00110000",
                        "strike": 110.0,
                        "bid": 3.1,
                        "ask": 3.4,
                        "impliedVolatility": 0.61,
                        "volume": 700,
                        "openInterest": 5100,
                    }
                ]
            ),
        )


@pytest.mark.asyncio
async def test_fixture_adapter_returns_sources_options_and_warning() -> None:
    adapter = FixtureResearchDataAdapter()

    result = await adapter.collect("NVDA", run_id="run-1")

    assert {source.source_type.value for source in result.sources} == {
        "market",
        "options",
        "sec",
        "news",
    }
    assert result.options_snapshot is not None
    assert result.options_snapshot.contracts[0].symbol.startswith("NVDA")
    assert result.warnings[0].source == "news"


@pytest.mark.asyncio
async def test_yfinance_adapter_maps_market_options_and_news_sources() -> None:
    adapter = YFinanceResearchDataAdapter(ticker_factory=FakeYFinanceTicker)

    result = await adapter.collect("nvda", run_id="run-live")

    sources_by_type = {source.source_type.value: source for source in result.sources}
    assert sources_by_type["market"].payload["price"] == 501.25
    assert sources_by_type["market"].payload["company_name"] == "NVIDIA Corporation"
    assert sources_by_type["news"].payload["items"][0]["title"] == (
        "Nvidia shares move after analyst note"
    )
    assert result.options_snapshot is not None
    assert [contract.option_type for contract in result.options_snapshot.contracts] == [
        "call",
        "put",
    ]
    assert result.options_snapshot.contracts[0].symbol == "NVDA260619C00130000"
    assert result.warnings == []


def test_build_research_data_adapter_selects_fixture_and_live_modes() -> None:
    assert isinstance(build_research_data_adapter("fixture"), FixtureResearchDataAdapter)
    assert isinstance(build_research_data_adapter("live"), YFinanceResearchDataAdapter)

    with pytest.raises(ValueError, match="Unknown data adapter mode"):
        build_research_data_adapter("unknown")


@pytest.mark.asyncio
async def test_deterministic_provider_generates_evidence_and_trade_idea() -> None:
    adapter = FixtureResearchDataAdapter()
    provider = DeterministicResearchProvider()
    data = await adapter.collect("NVDA", run_id="run-1")

    report = await provider.generate_report(
        "run-1",
        "NVDA",
        data.sources,
        data.options_snapshot,
        data.warnings,
    )

    assert report.run_id == "run-1"
    assert report.sections[0].title == "Market Snapshot"
    assert report.trade_ideas[0].structure == "Defined-risk call spread"
    assert report.warnings == data.warnings


@pytest.mark.asyncio
async def test_deterministic_provider_does_not_label_live_sources_as_fixture() -> None:
    adapter = YFinanceResearchDataAdapter(ticker_factory=FakeYFinanceTicker)
    provider = DeterministicResearchProvider()
    data = await adapter.collect("NVDA", run_id="run-live")

    report = await provider.generate_report(
        "run-live",
        "NVDA",
        data.sources,
        data.options_snapshot,
        data.warnings,
    )

    report_text = "\n".join(
        [
            *(section.body for section in report.sections),
            *(note for idea in report.trade_ideas for note in idea.risk_notes),
        ]
    )
    assert "fixture" not in report_text.lower()
    assert "Yahoo Finance" in report.sections[0].body
