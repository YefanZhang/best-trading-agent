from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from best_trading_agent.domain.trading import (
    AssetClass,
    Direction,
    MarketEvent,
    MarketEventType,
    OrderIntent,
    OrderIntentType,
    PortfolioState,
    Position,
    ResearchSummary,
    RiskDecision,
    RiskDecisionStatus,
    RiskRuleResult,
    SimulatedOrder,
    SimulatedOrderStatus,
    Strategy,
    TradeSide,
    TradingAuditRecord,
)


def test_market_event_validates_price_and_serializes_to_json() -> None:
    event = MarketEvent(
        id="event-1",
        event_type=MarketEventType.BAR_CLOSED,
        symbol="nvda",
        occurred_at=datetime(2026, 6, 7, 15, 59, tzinfo=UTC),
        price=125.50,
        bid=125.45,
        ask=125.55,
        volume=42_000_000,
        source="fixture",
    )

    payload = event.model_dump(mode="json")

    assert event.symbol == "NVDA"
    assert payload["event_type"] == "BAR_CLOSED"
    assert payload["occurred_at"] == "2026-06-07T15:59:00Z"

    with pytest.raises(ValidationError):
        MarketEvent(
            id="event-2",
            event_type=MarketEventType.BAR_CLOSED,
            symbol="NVDA",
            occurred_at=datetime(2026, 6, 7, 15, 59, tzinfo=UTC),
            price=0,
            bid=125.45,
            ask=125.55,
            volume=42_000_000,
            source="fixture",
        )


def test_order_intent_rejects_invalid_confidence_and_unsupported_quantity() -> None:
    intent = OrderIntent(
        intent_type=OrderIntentType.OPEN_POSITION,
        symbol="aapl",
        asset_class=AssetClass.EQUITY,
        strategy=Strategy.LONG_STOCK,
        direction=Direction.BULLISH,
        quantity=1,
        confidence=0.62,
        max_loss_usd=100.0,
        rationale_summary="Constructive context supports a small test.",
        idempotency_key="AAPL-2026-06-07-BAR-CLOSED-001",
    )

    assert intent.symbol == "AAPL"
    assert intent.model_dump(mode="json")["strategy"] == "LONG_STOCK"

    with pytest.raises(ValidationError):
        OrderIntent(
            intent_type=OrderIntentType.OPEN_POSITION,
            symbol="AAPL",
            asset_class=AssetClass.EQUITY,
            strategy=Strategy.LONG_STOCK,
            direction=Direction.BULLISH,
            quantity=0,
            confidence=1.5,
            max_loss_usd=100.0,
            rationale_summary="Invalid confidence.",
            idempotency_key="bad",
        )


def test_portfolio_state_and_audit_record_round_trip() -> None:
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
    summary = ResearchSummary(
        symbol="NVDA",
        source_event_id=event.id,
        market_regime="RISK_ON",
        summary="Momentum is constructive but data is fixture-backed.",
        bullish_factors=["Price closed above reference level"],
        bearish_factors=["Fixture data is not live"],
        uncertainties=["No intraday confirmation"],
        source_refs=[event.id],
        confidence=0.61,
    )
    intent = OrderIntent(
        intent_type=OrderIntentType.OPEN_POSITION,
        symbol="NVDA",
        asset_class=AssetClass.EQUITY,
        strategy=Strategy.LONG_STOCK,
        direction=Direction.BULLISH,
        quantity=1,
        confidence=0.61,
        max_loss_usd=125.50,
        rationale_summary="Constructive research supports one share.",
        idempotency_key="NVDA-event-1-LONG_STOCK",
    )
    decision = RiskDecision(
        decision=RiskDecisionStatus.APPROVED,
        rule_results=[
            RiskRuleResult(
                rule_id="MAX_SINGLE_TRADE",
                decision=RiskDecisionStatus.APPROVED,
                reason="Trade notional is within limit.",
                values={"notional_usd": 125.50},
                checked_at=datetime(2026, 6, 7, 16, 0, tzinfo=UTC),
            )
        ],
        checked_at=datetime(2026, 6, 7, 16, 0, tzinfo=UTC),
    )
    order = SimulatedOrder(
        id="order-1",
        intent_idempotency_key=intent.idempotency_key,
        symbol="NVDA",
        side=TradeSide.BUY,
        quantity=1,
        fill_price=125.50,
        status=SimulatedOrderStatus.FILLED,
        filled_at=datetime(2026, 6, 7, 16, 0, tzinfo=UTC),
    )
    final_state = PortfolioState(
        cash_usd=9_874.50,
        positions=[Position(symbol="NVDA", quantity=1, average_price=125.50)],
        open_intent_keys=[intent.idempotency_key],
    )

    audit = TradingAuditRecord(
        id="audit-1",
        run_id="run-1",
        created_at=datetime(2026, 6, 7, 16, 0, tzinfo=UTC),
        market_event=event,
        research_summary=summary,
        signal_intent=intent,
        risk_decision=decision,
        simulated_order=order,
        final_state=final_state,
    )

    restored = TradingAuditRecord.model_validate(audit.model_dump(mode="json"))

    assert restored.final_state.positions[0].symbol == "NVDA"
    assert restored.simulated_order is not None
    assert restored.simulated_order.status is SimulatedOrderStatus.FILLED
