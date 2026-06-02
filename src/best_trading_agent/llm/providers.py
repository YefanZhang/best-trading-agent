from typing import Protocol

from best_trading_agent.domain.models import (
    DataWarning,
    OptionsSnapshot,
    Report,
    ReportSection,
    SourceDocument,
    SourceType,
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
        market_source = _first_source(sources, SourceType.MARKET)
        news_source = _first_source(sources, SourceType.NEWS)
        sec_source = _first_source(sources, SourceType.SEC)
        has_yahoo_sources = any(
            source.payload.get("provider") == "yfinance" or "Yahoo Finance" in source.title
            for source in sources
        )
        source_label = "Yahoo Finance" if has_yahoo_sources else "fixture"
        market_context = (
            "price, volume, news, and options context"
            if has_yahoo_sources
            else "price, volume, filings, catalysts, and options context"
        )
        data_risk_note = (
            "Yahoo Finance data may be delayed, incomplete, or unavailable."
            if has_yahoo_sources
            else "Fixture data is not live market data."
        )
        sections = [
            ReportSection(
                title="Market Snapshot",
                body=_market_body(ticker, source_label, market_context, market_source),
                source_ids=source_ids,
            ),
            ReportSection(
                title="Options Context",
                body=_options_body(options_snapshot),
                source_ids=[
                    source.id for source in sources if source.source_type.value == "options"
                ],
            ),
            ReportSection(
                title="Filings and News",
                body=_filings_and_news_body(sec_source, news_source),
                source_ids=[
                    source.id
                    for source in sources
                    if source.source_type in {SourceType.SEC, SourceType.NEWS}
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


def _first_source(sources: list[SourceDocument], source_type: SourceType) -> SourceDocument | None:
    return next((source for source in sources if source.source_type is source_type), None)


def _market_body(
    ticker: str,
    source_label: str,
    market_context: str,
    market_source: SourceDocument | None,
) -> str:
    if market_source is None:
        return f"{ticker.upper()} {source_label} snapshot includes {market_context}."

    payload = market_source.payload
    company_name = payload.get("company_name") or ticker.upper()
    price = payload.get("price")
    currency = payload.get("currency")
    volume = payload.get("volume")
    sector = payload.get("sector")
    details = []
    if price is not None:
        details.append(f"price {price}{f' {currency}' if currency else ''}")
    if volume is not None:
        details.append(f"volume {volume}")
    if sector:
        details.append(f"sector {sector}")
    if not details:
        return f"{ticker.upper()} {source_label} snapshot includes {market_context}."
    return f"{company_name} ({ticker.upper()}) {source_label} snapshot: {', '.join(details)}."


def _options_body(options_snapshot: OptionsSnapshot | None) -> str:
    if options_snapshot is None:
        return "Options data was unavailable for this run."

    first_contract = options_snapshot.contracts[0] if options_snapshot.contracts else None
    if first_contract is None:
        return "Options data was available, but no contracts were returned."
    return (
        f"Front expiry {first_contract.expiration}; "
        f"{len(options_snapshot.contracts)} sampled contracts; "
        f"{first_contract.symbol} has implied volatility {first_contract.implied_volatility} "
        f"and volume {first_contract.volume}."
    )


def _filings_and_news_body(
    sec_source: SourceDocument | None,
    news_source: SourceDocument | None,
) -> str:
    parts: list[str] = []
    if sec_source is not None:
        filing_summary = _filing_summary(sec_source.payload)
        if filing_summary:
            parts.append(filing_summary)
        else:
            parts.append("SEC source returned company metadata but no recent 10-K, 10-Q, or 8-K.")
    else:
        parts.append("SEC filing data was unavailable for this run.")

    if news_source is not None:
        news_summary = _news_summary(news_source.payload)
        if news_summary:
            parts.append(news_summary)
        else:
            parts.append("News source returned no items.")
    else:
        parts.append("News data was unavailable for this run.")
    return " ".join(parts)


def _filing_summary(payload: dict[str, object]) -> str | None:
    latest_filings = payload.get("latest_filings")
    if isinstance(latest_filings, list) and latest_filings:
        filing = latest_filings[0]
        if isinstance(filing, dict):
            form = filing.get("form")
            filing_date = filing.get("filing_date")
            if form and filing_date:
                return f"Latest SEC filing: {form} filed {filing_date}."
            if form:
                return f"Latest SEC filing: {form}."

    filing = payload.get("filing")
    if isinstance(filing, str) and filing:
        return f"Latest SEC filing: {filing}."
    return None


def _news_summary(payload: dict[str, object]) -> str | None:
    items = payload.get("items")
    if isinstance(items, list) and items:
        first_item = items[0]
        if isinstance(first_item, dict):
            title = first_item.get("title")
            if isinstance(title, str) and title:
                return f"Top news item: {title}."

    headline = payload.get("headline")
    if isinstance(headline, str) and headline:
        return f"Top news item: {headline}."
    return None
