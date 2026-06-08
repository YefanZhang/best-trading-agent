from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from best_trading_agent.domain.trading import (
    MarketEvent,
    OrderIntent,
    OrderIntentType,
    PortfolioState,
    Position,
    RiskDecision,
    RiskDecisionStatus,
    SimulatedOrder,
    SimulatedOrderStatus,
    TradeSide,
)


@dataclass(frozen=True)
class ExecutionResult:
    order: SimulatedOrder | None
    final_state: PortfolioState


class SimulatedExecutionService:
    def execute(
        self,
        intent: OrderIntent,
        risk_decision: RiskDecision,
        market_event: MarketEvent,
        portfolio_state: PortfolioState,
        filled_at: datetime,
    ) -> ExecutionResult:
        if (
            risk_decision.decision is not RiskDecisionStatus.APPROVED
            or intent.intent_type is OrderIntentType.HOLD
        ):
            return ExecutionResult(order=None, final_state=portfolio_state)

        side = (
            TradeSide.BUY
            if intent.intent_type is OrderIntentType.OPEN_POSITION
            else TradeSide.SELL
        )
        order = SimulatedOrder(
            id=f"order-{uuid4().hex}",
            intent_idempotency_key=intent.idempotency_key,
            symbol=intent.symbol,
            side=side,
            quantity=intent.quantity,
            fill_price=market_event.price,
            status=SimulatedOrderStatus.FILLED,
            filled_at=filled_at,
        )
        return ExecutionResult(
            order=order,
            final_state=_apply_fill(order, portfolio_state),
        )


def _apply_fill(order: SimulatedOrder, state: PortfolioState) -> PortfolioState:
    if order.side is TradeSide.BUY:
        return _apply_buy(order, state)
    if order.side is TradeSide.SELL:
        return _apply_sell(order, state)
    return state


def _apply_buy(order: SimulatedOrder, state: PortfolioState) -> PortfolioState:
    existing = next(
        (position for position in state.positions if position.symbol == order.symbol),
        None,
    )
    new_cash = round(state.cash_usd - order.quantity * order.fill_price, 2)
    positions = [position for position in state.positions if position.symbol != order.symbol]
    if existing is None:
        positions.append(
            Position(
                symbol=order.symbol,
                quantity=order.quantity,
                average_price=order.fill_price,
            )
        )
    else:
        total_quantity = existing.quantity + order.quantity
        weighted_cost = (
            existing.quantity * existing.average_price + order.quantity * order.fill_price
        )
        positions.append(
            Position(
                symbol=order.symbol,
                quantity=total_quantity,
                average_price=round(weighted_cost / total_quantity, 2),
            )
        )
    return PortfolioState(
        cash_usd=new_cash,
        positions=sorted(positions, key=lambda position: position.symbol),
        realized_pnl_usd=state.realized_pnl_usd,
        kill_switch_active=state.kill_switch_active,
        open_intent_keys=[*state.open_intent_keys, order.intent_idempotency_key],
    )


def _apply_sell(order: SimulatedOrder, state: PortfolioState) -> PortfolioState:
    existing = next(
        (position for position in state.positions if position.symbol == order.symbol),
        None,
    )
    if existing is None:
        return state

    remaining_quantity = max(existing.quantity - order.quantity, 0)
    positions = [position for position in state.positions if position.symbol != order.symbol]
    if remaining_quantity:
        positions.append(
            Position(
                symbol=order.symbol,
                quantity=remaining_quantity,
                average_price=existing.average_price,
            )
        )
    realized_pnl = round(
        state.realized_pnl_usd
        + (order.fill_price - existing.average_price) * min(order.quantity, existing.quantity),
        2,
    )
    return PortfolioState(
        cash_usd=round(state.cash_usd + order.quantity * order.fill_price, 2),
        positions=sorted(positions, key=lambda position: position.symbol),
        realized_pnl_usd=realized_pnl,
        kill_switch_active=state.kill_switch_active,
        open_intent_keys=[*state.open_intent_keys, order.intent_idempotency_key],
    )
