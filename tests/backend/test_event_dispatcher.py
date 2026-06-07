from datetime import UTC, datetime

from best_trading_agent.domain.trading import (
    MarketEvent,
    MarketEventType,
    PortfolioState,
    RiskDecisionStatus,
)
from best_trading_agent.events.dispatcher import TradingEventDispatcher
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema
from best_trading_agent.trading.service import TradingLoopResult, TradingLoopService


def test_dispatcher_routes_bar_closed_event_into_trading_loop() -> None:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_schema(session_factory)
    repository = ResearchRepository(session_factory)
    service = TradingLoopService(repository)
    checked_at = datetime(2026, 6, 7, 16, 0, tzinfo=UTC)
    event = MarketEvent(
        id="event-1",
        event_type=MarketEventType.BAR_CLOSED,
        symbol="NVDA",
        occurred_at=datetime(2026, 6, 7, 15, 59, tzinfo=UTC),
        price=125.50,
        bid=125.45,
        ask=125.55,
        volume=42_000_000,
        source="fixture",
    )
    dispatcher = TradingEventDispatcher()
    dispatcher.subscribe(
        MarketEventType.BAR_CLOSED,
        lambda published_event: service.run_event(
            published_event,
            PortfolioState(cash_usd=10_000),
            checked_at=checked_at,
        ),
    )

    results = dispatcher.publish(event)
    audits = repository.list_trading_audit_records()

    assert len(results) == 1
    assert isinstance(results[0], TradingLoopResult)
    assert results[0].risk_decision.decision is RiskDecisionStatus.APPROVED
    assert len(audits) == 1
    assert audits[0].market_event.id == event.id


def test_dispatcher_returns_empty_results_when_no_handler_is_registered() -> None:
    event = MarketEvent(
        id="event-1",
        event_type=MarketEventType.QUOTE_UPDATED,
        symbol="NVDA",
        occurred_at=datetime(2026, 6, 7, 15, 59, tzinfo=UTC),
        price=125.50,
        bid=125.45,
        ask=125.55,
        volume=42_000_000,
        source="fixture",
    )

    results = TradingEventDispatcher().publish(event)

    assert results == []
