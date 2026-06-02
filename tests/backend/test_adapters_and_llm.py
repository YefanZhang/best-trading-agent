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


def fake_sec_json(url: str, user_agent: str) -> dict[str, object]:
    assert "best-trading-agent" in user_agent
    if url == "https://www.sec.gov/files/company_tickers.json":
        return {
            "0": {"cik_str": 1045810, "ticker": "NVDA", "title": "NVIDIA CORP"},
            "1": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
        }
    if url == "https://data.sec.gov/submissions/CIK0001045810.json":
        return {
            "cik": "0001045810",
            "name": "NVIDIA CORP",
            "filings": {
                "recent": {
                    "form": ["10-Q", "8-K", "4"],
                    "filingDate": ["2026-05-28", "2026-05-21", "2026-05-20"],
                    "accessionNumber": [
                        "0001045810-26-000123",
                        "0001045810-26-000111",
                        "0001045810-26-000100",
                    ],
                    "primaryDocument": ["nvda-20260528.htm", "nvda-8k.htm", "xslF345X05/doc4.xml"],
                }
            },
        }
    raise AssertionError(f"Unexpected SEC URL: {url}")


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
    adapter = YFinanceResearchDataAdapter(
        sec_fetch_json=fake_sec_json,
        sec_user_agent="best-trading-agent/0.1 tests@example.com",
        ticker_factory=FakeYFinanceTicker,
    )

    result = await adapter.collect("nvda", run_id="run-live")

    sources_by_type = {source.source_type.value: source for source in result.sources}
    assert sources_by_type["market"].payload["price"] == 501.25
    assert sources_by_type["market"].payload["company_name"] == "NVIDIA Corporation"
    assert sources_by_type["news"].payload["items"][0]["title"] == (
        "Nvidia shares move after analyst note"
    )
    assert sources_by_type["sec"].payload["provider"] == "sec"
    assert sources_by_type["sec"].payload["latest_filings"][0]["form"] == "10-Q"
    assert result.options_snapshot is not None
    assert [contract.option_type for contract in result.options_snapshot.contracts] == [
        "call",
        "put",
    ]
    assert result.options_snapshot.contracts[0].symbol == "NVDA260619C00130000"
    assert result.warnings == []


@pytest.mark.asyncio
async def test_yfinance_adapter_skips_sec_without_configured_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BEST_TRADING_AGENT_SEC_USER_AGENT", raising=False)

    def fail_sec_fetch(url: str, user_agent: str) -> dict[str, object]:
        raise AssertionError(f"SEC fetch should be skipped, got {url} with {user_agent}")

    adapter = YFinanceResearchDataAdapter(
        sec_fetch_json=fail_sec_fetch,
        ticker_factory=FakeYFinanceTicker,
    )

    result = await adapter.collect("nvda", run_id="run-live")

    assert "sec" not in {source.source_type.value for source in result.sources}
    assert result.warnings[-1].source == "sec"
    assert "BEST_TRADING_AGENT_SEC_USER_AGENT" in result.warnings[-1].message
    assert "contact email" in result.warnings[-1].message


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
    report_text = "\n".join(section.body for section in report.sections)
    assert "Latest SEC filing: 10-Q" in report_text
    assert "Analysts discuss AI demand outlook." in report_text
    assert "SEC source returned company metadata" not in report_text
    assert "News source returned no items" not in report_text


@pytest.mark.asyncio
async def test_deterministic_provider_does_not_label_live_sources_as_fixture() -> None:
    adapter = YFinanceResearchDataAdapter(
        sec_fetch_json=fake_sec_json,
        sec_user_agent="best-trading-agent/0.1 tests@example.com",
        ticker_factory=FakeYFinanceTicker,
    )
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
    assert "501.25" in report_text
    assert "NVIDIA Corporation" in report_text
    assert "Nvidia shares move after analyst note" in report_text
    assert "10-Q" in report_text
    assert "Yahoo Finance" in report.sections[0].body
