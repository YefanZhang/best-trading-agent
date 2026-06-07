from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from best_trading_agent.domain.trading import (
    MarketEvent,
    OrderIntent,
    OrderIntentType,
    PortfolioState,
    RiskDecision,
    RiskDecisionStatus,
    RiskRuleResult,
    Strategy,
)


@dataclass(frozen=True)
class RiskConfig:
    max_single_trade_usd: float = 1_000.0
    approval_required_trade_usd: float = 750.0
    stale_quote_seconds: int = 120
    min_confidence: float = 0.55
    allowed_strategies: tuple[Strategy, ...] = field(
        default_factory=lambda: (Strategy.LONG_STOCK, Strategy.CASH_SECURED_HOLD)
    )


class RiskEngine:
    def __init__(self, config: RiskConfig | None = None) -> None:
        self._config = config or RiskConfig()

    def evaluate(
        self,
        intent: OrderIntent,
        portfolio_state: PortfolioState,
        market_event: MarketEvent,
        checked_at: datetime,
    ) -> RiskDecision:
        results = [
            self._supported_strategy(intent, checked_at),
            self._single_trade_limit(intent, market_event, checked_at),
            self._cash_available(intent, portfolio_state, market_event, checked_at),
            self._stale_market_data(market_event, checked_at),
            self._duplicate_order(intent, portfolio_state, checked_at),
            self._kill_switch(portfolio_state, checked_at),
            self._low_confidence(intent, checked_at),
        ]
        return RiskDecision(
            decision=_roll_up(results),
            rule_results=results,
            checked_at=checked_at,
        )

    def _supported_strategy(
        self, intent: OrderIntent, checked_at: datetime
    ) -> RiskRuleResult:
        if intent.strategy not in self._config.allowed_strategies:
            return _result(
                "SUPPORTED_STRATEGY",
                RiskDecisionStatus.REJECTED,
                "Strategy is not allowed in the current phase.",
                {"strategy": intent.strategy.value},
                checked_at,
            )
        return _result(
            "SUPPORTED_STRATEGY",
            RiskDecisionStatus.APPROVED,
            "Strategy is allowed.",
            {"strategy": intent.strategy.value},
            checked_at,
        )

    def _single_trade_limit(
        self,
        intent: OrderIntent,
        market_event: MarketEvent,
        checked_at: datetime,
    ) -> RiskRuleResult:
        notional_usd = _notional(intent, market_event)
        values = {
            "notional_usd": notional_usd,
            "max_single_trade_usd": self._config.max_single_trade_usd,
            "approval_required_trade_usd": self._config.approval_required_trade_usd,
        }
        if notional_usd > self._config.max_single_trade_usd:
            return _result(
                "MAX_SINGLE_TRADE",
                RiskDecisionStatus.REJECTED,
                "Trade notional exceeds max single-trade limit.",
                values,
                checked_at,
            )
        if notional_usd >= self._config.approval_required_trade_usd:
            return _result(
                "MAX_SINGLE_TRADE",
                RiskDecisionStatus.APPROVAL_REQUIRED,
                "Trade notional requires human approval.",
                values,
                checked_at,
            )
        return _result(
            "MAX_SINGLE_TRADE",
            RiskDecisionStatus.APPROVED,
            "Trade notional is within limit.",
            values,
            checked_at,
        )

    def _cash_available(
        self,
        intent: OrderIntent,
        portfolio_state: PortfolioState,
        market_event: MarketEvent,
        checked_at: datetime,
    ) -> RiskRuleResult:
        notional_usd = _notional(intent, market_event)
        if intent.intent_type is OrderIntentType.HOLD or notional_usd <= portfolio_state.cash_usd:
            return _result(
                "CASH_AVAILABLE",
                RiskDecisionStatus.APPROVED,
                "Cash is sufficient for the candidate.",
                {"cash_usd": portfolio_state.cash_usd, "notional_usd": notional_usd},
                checked_at,
            )
        return _result(
            "CASH_AVAILABLE",
            RiskDecisionStatus.REJECTED,
            "Cash is insufficient for the candidate.",
            {"cash_usd": portfolio_state.cash_usd, "notional_usd": notional_usd},
            checked_at,
        )

    def _stale_market_data(
        self, market_event: MarketEvent, checked_at: datetime
    ) -> RiskRuleResult:
        age_seconds = (checked_at - market_event.occurred_at).total_seconds()
        values = {
            "quote_age_seconds": age_seconds,
            "max_allowed_age_seconds": self._config.stale_quote_seconds,
        }
        if age_seconds > self._config.stale_quote_seconds:
            return _result(
                "STALE_MARKET_DATA",
                RiskDecisionStatus.REJECTED,
                "Market data age exceeded configured threshold.",
                values,
                checked_at,
            )
        return _result(
            "STALE_MARKET_DATA",
            RiskDecisionStatus.APPROVED,
            "Market data is fresh enough for the candidate.",
            values,
            checked_at,
        )

    def _duplicate_order(
        self, intent: OrderIntent, portfolio_state: PortfolioState, checked_at: datetime
    ) -> RiskRuleResult:
        if intent.idempotency_key in portfolio_state.open_intent_keys:
            return _result(
                "DUPLICATE_ORDER",
                RiskDecisionStatus.REJECTED,
                "Idempotency key has already been used.",
                {"idempotency_key": intent.idempotency_key},
                checked_at,
            )
        return _result(
            "DUPLICATE_ORDER",
            RiskDecisionStatus.APPROVED,
            "Idempotency key has not been used.",
            {"idempotency_key": intent.idempotency_key},
            checked_at,
        )

    def _kill_switch(
        self, portfolio_state: PortfolioState, checked_at: datetime
    ) -> RiskRuleResult:
        if portfolio_state.kill_switch_active:
            return _result(
                "KILL_SWITCH",
                RiskDecisionStatus.REJECTED,
                "Kill switch is active.",
                {"kill_switch_active": True},
                checked_at,
            )
        return _result(
            "KILL_SWITCH",
            RiskDecisionStatus.APPROVED,
            "Kill switch is inactive.",
            {"kill_switch_active": False},
            checked_at,
        )

    def _low_confidence(self, intent: OrderIntent, checked_at: datetime) -> RiskRuleResult:
        values = {"confidence": intent.confidence, "min_confidence": self._config.min_confidence}
        if intent.confidence < self._config.min_confidence:
            return _result(
                "LOW_CONFIDENCE",
                RiskDecisionStatus.APPROVAL_REQUIRED,
                "Candidate confidence is below automatic-approval threshold.",
                values,
                checked_at,
            )
        return _result(
            "LOW_CONFIDENCE",
            RiskDecisionStatus.APPROVED,
            "Candidate confidence is above automatic-approval threshold.",
            values,
            checked_at,
        )


def _notional(intent: OrderIntent, market_event: MarketEvent) -> float:
    return round(intent.quantity * market_event.price, 2)


def _roll_up(results: list[RiskRuleResult]) -> RiskDecisionStatus:
    if any(result.decision is RiskDecisionStatus.REJECTED for result in results):
        return RiskDecisionStatus.REJECTED
    if any(result.decision is RiskDecisionStatus.APPROVAL_REQUIRED for result in results):
        return RiskDecisionStatus.APPROVAL_REQUIRED
    return RiskDecisionStatus.APPROVED


def _result(
    rule_id: str,
    decision: RiskDecisionStatus,
    reason: str,
    values: dict[str, Any],
    checked_at: datetime,
) -> RiskRuleResult:
    return RiskRuleResult(
        rule_id=rule_id,
        decision=decision,
        reason=reason,
        values=values,
        checked_at=checked_at,
    )
