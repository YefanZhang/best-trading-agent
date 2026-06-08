from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import uuid4

from best_trading_agent.agents.research_agent import DeterministicTradingResearchAgent
from best_trading_agent.agents.signal_agent import DeterministicSignalAgent
from best_trading_agent.domain.trading import (
    MarketEvent,
    MarketEventType,
    OrderIntent,
    PortfolioState,
    ResearchSummary,
    RiskDecision,
    SimulatedOrder,
    TradingAuditRecord,
)
from best_trading_agent.execution.simulator import SimulatedExecutionService
from best_trading_agent.risk.engine import RiskEngine
from best_trading_agent.storage.repositories import ResearchRepository


class TradingScenario(StrEnum):
    APPROVED = "approved"
    APPROVAL_REQUIRED = "approval-required"
    REJECTED = "rejected"


@dataclass(frozen=True)
class TradingLoopResult:
    run_id: str
    market_event: MarketEvent
    research_summary: ResearchSummary
    signal_intent: OrderIntent
    risk_decision: RiskDecision
    simulated_order: SimulatedOrder | None
    final_state: PortfolioState
    audit_record: TradingAuditRecord


class TradingLoopService:
    def __init__(
        self,
        repository: ResearchRepository,
        research_agent: DeterministicTradingResearchAgent | None = None,
        signal_agent: DeterministicSignalAgent | None = None,
        risk_engine: RiskEngine | None = None,
        execution_service: SimulatedExecutionService | None = None,
    ) -> None:
        self._repository = repository
        self._research_agent = research_agent or DeterministicTradingResearchAgent()
        self._signal_agent = signal_agent or DeterministicSignalAgent()
        self._risk_engine = risk_engine or RiskEngine()
        self._execution_service = execution_service or SimulatedExecutionService()

    def run_demo(
        self,
        ticker: str,
        scenario: TradingScenario = TradingScenario.APPROVED,
        now: datetime | None = None,
    ) -> TradingLoopResult:
        resolved_now = now or datetime.now(UTC)
        symbol = ticker.upper().strip()
        market_event = _demo_market_event(symbol, scenario, resolved_now)
        portfolio_state = PortfolioState(cash_usd=10_000)
        return self.run_event(
            market_event=market_event,
            portfolio_state=portfolio_state,
            checked_at=resolved_now,
        )

    def run_event(
        self,
        market_event: MarketEvent,
        portfolio_state: PortfolioState,
        checked_at: datetime | None = None,
        run_id: str | None = None,
    ) -> TradingLoopResult:
        resolved_run_id = run_id or f"trading-run-{uuid4().hex}"
        resolved_checked_at = checked_at or datetime.now(UTC)
        research_summary = self._research_agent.summarize(market_event)
        signal_intent = self._signal_agent.create_intent(research_summary, portfolio_state)
        risk_decision = self._risk_engine.evaluate(
            intent=signal_intent,
            portfolio_state=portfolio_state,
            market_event=market_event,
            checked_at=resolved_checked_at,
        )
        execution_result = self._execution_service.execute(
            intent=signal_intent,
            risk_decision=risk_decision,
            market_event=market_event,
            portfolio_state=portfolio_state,
            filled_at=resolved_checked_at,
        )
        audit_record = TradingAuditRecord(
            id=f"audit-{uuid4().hex}",
            run_id=resolved_run_id,
            created_at=resolved_checked_at,
            market_event=market_event,
            research_summary=research_summary,
            signal_intent=signal_intent,
            risk_decision=risk_decision,
            simulated_order=execution_result.order,
            final_state=execution_result.final_state,
        )
        self._repository.save_trading_audit_record(audit_record)
        return TradingLoopResult(
            run_id=resolved_run_id,
            market_event=market_event,
            research_summary=research_summary,
            signal_intent=signal_intent,
            risk_decision=risk_decision,
            simulated_order=execution_result.order,
            final_state=execution_result.final_state,
            audit_record=audit_record,
        )


def _demo_market_event(symbol: str, scenario: TradingScenario, now: datetime) -> MarketEvent:
    price_by_scenario = {
        TradingScenario.APPROVED: 125.50,
        TradingScenario.APPROVAL_REQUIRED: 800.00,
        TradingScenario.REJECTED: 1_500.00,
    }
    price = price_by_scenario[scenario]
    return MarketEvent(
        id=f"event-{scenario.value}-{symbol}",
        event_type=MarketEventType.BAR_CLOSED,
        symbol=symbol,
        occurred_at=now - timedelta(seconds=30),
        price=price,
        bid=price - 0.05,
        ask=price + 0.05,
        volume=42_000_000,
        source="fixture",
    )
