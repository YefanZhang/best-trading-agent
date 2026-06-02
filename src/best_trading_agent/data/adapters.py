from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

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


class YFinanceResearchDataAdapter:
    def __init__(self, ticker_factory: Any | None = None) -> None:
        if ticker_factory is None:
            import yfinance as yf  # type: ignore[import-untyped]

            ticker_factory = yf.Ticker
        self._ticker_factory = ticker_factory

    async def collect(self, ticker: str, run_id: str) -> CollectedResearchData:
        upper_ticker = ticker.upper().strip()
        retrieved_at = datetime.now(UTC)
        yf_ticker = self._ticker_factory(upper_ticker)
        warnings: list[DataWarning] = []
        sources: list[SourceDocument] = []

        market_payload = self._market_payload(yf_ticker)
        sources.append(
            SourceDocument(
                id=f"{run_id}-market",
                run_id=run_id,
                source_type=SourceType.MARKET,
                title=f"{upper_ticker} Yahoo Finance market snapshot",
                url=f"https://finance.yahoo.com/quote/{upper_ticker}",
                retrieved_at=retrieved_at,
                payload=market_payload,
            )
        )

        options_snapshot = self._options_snapshot(
            yf_ticker,
            upper_ticker,
            run_id,
            retrieved_at,
            warnings,
        )
        if options_snapshot is not None:
            sources.append(
                SourceDocument(
                    id=f"{run_id}-options",
                    run_id=run_id,
                    source_type=SourceType.OPTIONS,
                    title=f"{upper_ticker} Yahoo Finance options snapshot",
                    url=f"https://finance.yahoo.com/quote/{upper_ticker}/options",
                    retrieved_at=retrieved_at,
                    payload={
                        "expirations": [
                            contract.expiration for contract in options_snapshot.contracts
                        ],
                        "contract_count": len(options_snapshot.contracts),
                    },
                )
            )

        news_items = self._news_items(yf_ticker)
        if news_items:
            sources.append(
                SourceDocument(
                    id=f"{run_id}-news",
                    run_id=run_id,
                    source_type=SourceType.NEWS,
                    title=f"{upper_ticker} Yahoo Finance news",
                    url=f"https://finance.yahoo.com/quote/{upper_ticker}/news",
                    retrieved_at=retrieved_at,
                    payload={"items": news_items},
                )
            )
        else:
            warnings.append(
                DataWarning(source="news", message="Yahoo Finance returned no news items")
            )

        return CollectedResearchData(
            sources=sources,
            options_snapshot=options_snapshot,
            warnings=warnings,
        )

    def _market_payload(self, yf_ticker: Any) -> dict[str, Any]:
        fast_info = _as_mapping(getattr(yf_ticker, "fast_info", {}))
        info = _as_mapping(getattr(yf_ticker, "info", {}))
        return {
            "provider": "yfinance",
            "price": _first_present(fast_info, "last_price", "lastPrice"),
            "previous_close": _first_present(fast_info, "previous_close", "previousClose"),
            "currency": _first_present(fast_info, "currency"),
            "volume": _first_present(fast_info, "day_volume", "lastVolume"),
            "market_cap": _first_present(fast_info, "market_cap", "marketCap")
            or _first_present(info, "marketCap"),
            "company_name": _first_present(info, "shortName", "longName"),
            "sector": _first_present(info, "sector"),
            "trailing_pe": _first_present(info, "trailingPE"),
        }

    def _options_snapshot(
        self,
        yf_ticker: Any,
        ticker: str,
        run_id: str,
        retrieved_at: datetime,
        warnings: list[DataWarning],
    ) -> OptionsSnapshot | None:
        expirations = list(getattr(yf_ticker, "options", []) or [])
        if not expirations:
            warnings.append(
                DataWarning(
                    source="options",
                    message="Yahoo Finance returned no option expirations",
                )
            )
            return None

        expiration = str(expirations[0])
        try:
            chain = yf_ticker.option_chain(expiration)
        except Exception as error:
            warnings.append(
                DataWarning(
                    source="options",
                    message=f"Yahoo Finance options fetch failed: {error}",
                )
            )
            return None

        contracts = [
            *self._option_contracts(_records(getattr(chain, "calls", [])), expiration, "call"),
            *self._option_contracts(_records(getattr(chain, "puts", [])), expiration, "put"),
        ]
        if not contracts:
            warnings.append(
                DataWarning(source="options", message="Yahoo Finance returned no option contracts")
            )
            return None
        return OptionsSnapshot(
            id=f"{run_id}-options-snapshot",
            run_id=run_id,
            ticker=ticker,
            retrieved_at=retrieved_at,
            contracts=contracts,
        )

    def _option_contracts(
        self,
        records: list[dict[str, Any]],
        expiration: str,
        option_type: str,
    ) -> list[OptionContract]:
        contracts: list[OptionContract] = []
        for record in records:
            symbol = str(record.get("contractSymbol") or record.get("symbol") or "")
            if not symbol:
                continue
            contracts.append(
                OptionContract(
                    symbol=symbol,
                    expiration=expiration,
                    strike=_float_or_none(record.get("strike")) or 0.0,
                    option_type=option_type,
                    bid=_float_or_none(record.get("bid")),
                    ask=_float_or_none(record.get("ask")),
                    implied_volatility=_float_or_none(record.get("impliedVolatility")),
                    volume=_int_or_none(record.get("volume")),
                    open_interest=_int_or_none(record.get("openInterest")),
                )
            )
        return contracts

    def _news_items(self, yf_ticker: Any) -> list[dict[str, Any]]:
        raw_news = getattr(yf_ticker, "news", []) or []
        items: list[dict[str, Any]] = []
        for item in raw_news[:10]:
            item_mapping = _as_mapping(item)
            content = _as_mapping(item_mapping.get("content", {}))
            title = item_mapping.get("title") or content.get("title")
            link = (
                item_mapping.get("link")
                or content.get("canonicalUrl")
                or content.get("clickThroughUrl")
            )
            publisher = item_mapping.get("publisher") or _as_mapping(
                content.get("provider", {})
            ).get(
                "displayName",
            )
            if title:
                items.append({"title": title, "url": link, "publisher": publisher})
        return items


def build_research_data_adapter(mode: str) -> ResearchDataAdapter:
    normalized_mode = mode.strip().lower()
    if normalized_mode == "fixture":
        return FixtureResearchDataAdapter()
    if normalized_mode == "live":
        return YFinanceResearchDataAdapter()
    raise ValueError(f"Unknown data adapter mode: {mode}")


def _as_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    try:
        return dict(value)
    except (TypeError, ValueError):
        return {}


def _records(value: Any) -> list[dict[str, Any]]:
    if hasattr(value, "to_dict"):
        return list(value.to_dict("records"))
    if isinstance(value, list):
        return [_as_mapping(item) for item in value]
    return []


def _first_present(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
