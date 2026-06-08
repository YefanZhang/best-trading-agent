from datetime import UTC, datetime, timedelta

from best_trading_agent.agents.research_agent import DeterministicTradingResearchAgent
from best_trading_agent.agents.signal_agent import DeterministicSignalAgent
from best_trading_agent.domain.trading import (
    Direction,
    MarketEvent,
    MarketEventType,
    OrderIntentType,
    PortfolioState,
    RiskDecision,
    RiskDecisionStatus,
    RiskRuleResult,
    Strategy,
    TradeSide,
)
from best_trading_agent.execution.simulator import SimulatedExecutionService
from best_trading_agent.risk.engine import RiskConfig, RiskEngine


def _market_event(
    *,
    occurred_at: datetime = datetime(2026, 6, 7, 15, 59, tzinfo=UTC),
    price: float = 125.50,
) -> MarketEvent:
    return MarketEvent(
        id="event-1",
        event_type=MarketEventType.BAR_CLOSED,
        symbol="NVDA",
        occurred_at=occurred_at,
        price=price,
        bid=price - 0.05,
        ask=price + 0.05,
        volume=42_000_000,
        source="fixture",
    )


def test_research_agent_returns_structured_summary_with_sources_and_uncertainty() -> None:
    agent = DeterministicTradingResearchAgent()
    event = _market_event()

    summary = agent.summarize(event)

    assert summary.symbol == "NVDA"
    assert summary.source_event_id == event.id
    assert summary.source_refs == [event.id]
    assert summary.uncertainties == ["Fixture market data is not live."]
    assert 0 <= summary.confidence <= 1


def test_signal_agent_emits_small_long_stock_intent_from_constructive_summary() -> None:
    summary = DeterministicTradingResearchAgent().summarize(_market_event())
    state = PortfolioState(cash_usd=10_000)

    intent = DeterministicSignalAgent().create_intent(summary, state)

    assert intent.intent_type is OrderIntentType.OPEN_POSITION
    assert intent.symbol == "NVDA"
    assert intent.strategy is Strategy.LONG_STOCK
    assert intent.direction is Direction.BULLISH
    assert intent.quantity == 1
    assert intent.idempotency_key == "NVDA-event-1-LONG_STOCK"


def test_risk_engine_approves_safe_candidate_with_machine_readable_rules() -> None:
    checked_at = datetime(2026, 6, 7, 16, 0, tzinfo=UTC)
    event = _market_event()
    summary = DeterministicTradingResearchAgent().summarize(event)
    intent = DeterministicSignalAgent().create_intent(summary, PortfolioState(cash_usd=10_000))
    engine = RiskEngine(
        RiskConfig(
            max_single_trade_usd=1_000,
            approval_required_trade_usd=750,
            stale_quote_seconds=120,
        )
    )

    decision = engine.evaluate(
        intent=intent,
        portfolio_state=PortfolioState(cash_usd=10_000),
        market_event=event,
        checked_at=checked_at,
    )

    assert decision.decision is RiskDecisionStatus.APPROVED
    assert {result.rule_id for result in decision.rule_results} >= {
        "SUPPORTED_STRATEGY",
        "MAX_SINGLE_TRADE",
        "STALE_MARKET_DATA",
        "DUPLICATE_ORDER",
        "KILL_SWITCH",
    }


def test_risk_engine_rejects_stale_duplicate_or_kill_switch_candidates() -> None:
    checked_at = datetime(2026, 6, 7, 16, 0, tzinfo=UTC)
    event = _market_event(occurred_at=checked_at - timedelta(minutes=5))
    summary = DeterministicTradingResearchAgent().summarize(event)
    intent = DeterministicSignalAgent().create_intent(summary, PortfolioState(cash_usd=10_000))
    state = PortfolioState(
        cash_usd=10_000,
        kill_switch_active=True,
        open_intent_keys=[intent.idempotency_key],
    )

    decision = RiskEngine(RiskConfig(stale_quote_seconds=60)).evaluate(
        intent=intent,
        portfolio_state=state,
        market_event=event,
        checked_at=checked_at,
    )

    assert decision.decision is RiskDecisionStatus.REJECTED
    rejected_rule_ids = {
        result.rule_id
        for result in decision.rule_results
        if result.decision is RiskDecisionStatus.REJECTED
    }

    assert rejected_rule_ids >= {
        "STALE_MARKET_DATA",
        "DUPLICATE_ORDER",
        "KILL_SWITCH",
    }


def test_risk_engine_requires_approval_for_low_confidence_candidate() -> None:
    checked_at = datetime(2026, 6, 7, 16, 0, tzinfo=UTC)
    event = _market_event()
    summary = DeterministicTradingResearchAgent().summarize(event)
    intent = DeterministicSignalAgent().create_intent(summary, PortfolioState(cash_usd=10_000))
    low_confidence_intent = intent.model_copy(update={"confidence": 0.40})

    decision = RiskEngine(RiskConfig(min_confidence=0.55)).evaluate(
        intent=low_confidence_intent,
        portfolio_state=PortfolioState(cash_usd=10_000),
        market_event=event,
        checked_at=checked_at,
    )

    assert decision.decision is RiskDecisionStatus.APPROVAL_REQUIRED
    assert any(result.rule_id == "LOW_CONFIDENCE" for result in decision.rule_results)


def test_simulator_executes_approved_intent_and_leaves_rejected_intent_unfilled() -> None:
    filled_at = datetime(2026, 6, 7, 16, 0, tzinfo=UTC)
    event = _market_event(price=125.50)
    summary = DeterministicTradingResearchAgent().summarize(event)
    intent = DeterministicSignalAgent().create_intent(summary, PortfolioState(cash_usd=10_000))
    approved = RiskDecision(
        decision=RiskDecisionStatus.APPROVED,
        rule_results=[
            RiskRuleResult(
                rule_id="MAX_SINGLE_TRADE",
                decision=RiskDecisionStatus.APPROVED,
                reason="Trade notional is within limit.",
                values={"notional_usd": 125.50},
                checked_at=filled_at,
            )
        ],
        checked_at=filled_at,
    )
    rejected = approved.model_copy(update={"decision": RiskDecisionStatus.REJECTED})
    simulator = SimulatedExecutionService()

    approved_result = simulator.execute(
        intent=intent,
        risk_decision=approved,
        market_event=event,
        portfolio_state=PortfolioState(cash_usd=10_000),
        filled_at=filled_at,
    )
    rejected_result = simulator.execute(
        intent=intent,
        risk_decision=rejected,
        market_event=event,
        portfolio_state=PortfolioState(cash_usd=10_000),
        filled_at=filled_at,
    )

    assert approved_result.order is not None
    assert approved_result.order.side is TradeSide.BUY
    assert approved_result.final_state.cash_usd == 9_874.50
    assert approved_result.final_state.positions[0].quantity == 1
    assert approved_result.final_state.open_intent_keys == [intent.idempotency_key]
    assert rejected_result.order is None
    assert rejected_result.final_state.cash_usd == 10_000
