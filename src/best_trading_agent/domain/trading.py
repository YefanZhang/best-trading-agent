from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class MarketEventType(StrEnum):
    BAR_CLOSED = "BAR_CLOSED"
    QUOTE_UPDATED = "QUOTE_UPDATED"


class OrderIntentType(StrEnum):
    OPEN_POSITION = "OPEN_POSITION"
    CLOSE_POSITION = "CLOSE_POSITION"
    HOLD = "HOLD"


class AssetClass(StrEnum):
    EQUITY = "EQUITY"


class Strategy(StrEnum):
    LONG_STOCK = "LONG_STOCK"
    CASH_SECURED_HOLD = "CASH_SECURED_HOLD"


class Direction(StrEnum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class RiskDecisionStatus(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class TradeSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    NONE = "NONE"


class SimulatedOrderStatus(StrEnum):
    FILLED = "FILLED"


class TradingModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class MarketEvent(TradingModel):
    id: str = Field(min_length=1)
    event_type: MarketEventType
    symbol: str = Field(min_length=1)
    occurred_at: datetime
    price: float = Field(gt=0)
    bid: float | None = Field(default=None, gt=0)
    ask: float | None = Field(default=None, gt=0)
    volume: int | None = Field(default=None, ge=0)
    source: str = Field(min_length=1)

    @field_validator("symbol")
    @classmethod
    def _uppercase_symbol(cls, value: str) -> str:
        return value.upper().strip()


class Position(TradingModel):
    symbol: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    average_price: float = Field(gt=0)

    @field_validator("symbol")
    @classmethod
    def _uppercase_symbol(cls, value: str) -> str:
        return value.upper().strip()


class PortfolioState(TradingModel):
    cash_usd: float = Field(ge=0)
    positions: list[Position] = Field(default_factory=list)
    realized_pnl_usd: float = 0.0
    kill_switch_active: bool = False
    open_intent_keys: list[str] = Field(default_factory=list)


class ResearchSummary(TradingModel):
    symbol: str = Field(min_length=1)
    source_event_id: str = Field(min_length=1)
    market_regime: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    bullish_factors: list[str] = Field(min_length=1)
    bearish_factors: list[str] = Field(min_length=1)
    uncertainties: list[str] = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)

    @field_validator("symbol")
    @classmethod
    def _uppercase_symbol(cls, value: str) -> str:
        return value.upper().strip()


class OrderIntent(TradingModel):
    intent_type: OrderIntentType
    symbol: str = Field(min_length=1)
    asset_class: AssetClass
    strategy: Strategy
    direction: Direction
    quantity: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    max_loss_usd: float = Field(ge=0)
    rationale_summary: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)

    @field_validator("symbol")
    @classmethod
    def _uppercase_symbol(cls, value: str) -> str:
        return value.upper().strip()

    @model_validator(mode="after")
    def _validate_quantity_for_intent_type(self) -> "OrderIntent":
        if self.intent_type is OrderIntentType.HOLD:
            if self.quantity != 0:
                raise ValueError("HOLD intents must use quantity 0.")
        elif self.quantity <= 0:
            raise ValueError("Executable intents must use quantity greater than 0.")
        return self


class RiskRuleResult(TradingModel):
    rule_id: str = Field(min_length=1)
    decision: RiskDecisionStatus
    reason: str = Field(min_length=1)
    values: dict[str, Any] = Field(default_factory=dict)
    checked_at: datetime


class RiskDecision(TradingModel):
    decision: RiskDecisionStatus
    rule_results: list[RiskRuleResult] = Field(min_length=1)
    checked_at: datetime


class SimulatedOrder(TradingModel):
    id: str = Field(min_length=1)
    intent_idempotency_key: str = Field(min_length=1)
    symbol: str = Field(min_length=1)
    side: TradeSide
    quantity: int = Field(gt=0)
    fill_price: float = Field(gt=0)
    status: SimulatedOrderStatus
    filled_at: datetime

    @field_validator("symbol")
    @classmethod
    def _uppercase_symbol(cls, value: str) -> str:
        return value.upper().strip()


class TradingAuditRecord(TradingModel):
    id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    created_at: datetime
    market_event: MarketEvent
    research_summary: ResearchSummary
    signal_intent: OrderIntent
    risk_decision: RiskDecision
    simulated_order: SimulatedOrder | None = None
    final_state: PortfolioState
