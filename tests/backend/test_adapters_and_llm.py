import pytest

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.llm.providers import DeterministicResearchProvider


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
