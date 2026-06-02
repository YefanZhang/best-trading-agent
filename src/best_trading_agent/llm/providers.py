from typing import Protocol

from best_trading_agent.domain.models import (
    DataWarning,
    OptionsSnapshot,
    Report,
    ReportSection,
    SourceDocument,
    TradeIdea,
)


class ResearchLLMProvider(Protocol):
    async def generate_report(
        self,
        run_id: str,
        ticker: str,
        sources: list[SourceDocument],
        options_snapshot: OptionsSnapshot | None,
        warnings: list[DataWarning],
    ) -> Report:
        raise NotImplementedError


class DeterministicResearchProvider:
    async def generate_report(
        self,
        run_id: str,
        ticker: str,
        sources: list[SourceDocument],
        options_snapshot: OptionsSnapshot | None,
        warnings: list[DataWarning],
    ) -> Report:
        source_ids = [source.id for source in sources]
        has_yahoo_sources = any(
            source.payload.get("provider") == "yfinance" or "Yahoo Finance" in source.title
            for source in sources
        )
        source_label = "Yahoo Finance" if has_yahoo_sources else "fixture"
        data_risk_note = (
            "Yahoo Finance data may be delayed, incomplete, or unavailable."
            if has_yahoo_sources
            else "Fixture data is not live market data."
        )
        sections = [
            ReportSection(
                title="Market Snapshot",
                body=(
                    f"{ticker.upper()} {source_label} snapshot includes price, volume, filings, "
                    "catalysts, and options context."
                ),
                source_ids=source_ids,
            ),
            ReportSection(
                title="Options Context",
                body=(
                    "Front-expiry implied volatility and contract activity are available."
                    if options_snapshot is not None
                    else "Options data was unavailable for this run."
                ),
                source_ids=[
                    source.id for source in sources if source.source_type.value == "options"
                ],
            ),
            ReportSection(
                title="Bull Base Bear",
                body=(
                    "Bull: catalysts continue. Base: current trend persists. "
                    "Bear: demand or valuation disappoints."
                ),
                source_ids=source_ids,
            ),
        ]
        trade_ideas = [
            TradeIdea(
                structure="Defined-risk call spread",
                thesis="Potential upside participation while limiting premium at risk.",
                risk_notes=[
                    "Can expire worthless.",
                    "Spread caps upside.",
                    data_risk_note,
                ],
                source_ids=source_ids,
            )
        ]
        return Report(
            id=f"{run_id}-report",
            run_id=run_id,
            sections=sections,
            trade_ideas=trade_ideas,
            warnings=warnings,
        )
