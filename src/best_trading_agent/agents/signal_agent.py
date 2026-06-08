from best_trading_agent.domain.trading import (
    AssetClass,
    Direction,
    OrderIntent,
    OrderIntentType,
    PortfolioState,
    ResearchSummary,
    Strategy,
)


class DeterministicSignalAgent:
    def create_intent(
        self, summary: ResearchSummary, portfolio_state: PortfolioState
    ) -> OrderIntent:
        if summary.confidence < 0.5 or portfolio_state.cash_usd <= 0:
            return OrderIntent(
                intent_type=OrderIntentType.HOLD,
                symbol=summary.symbol,
                asset_class=AssetClass.EQUITY,
                strategy=Strategy.CASH_SECURED_HOLD,
                direction=Direction.NEUTRAL,
                quantity=0,
                confidence=summary.confidence,
                max_loss_usd=0,
                rationale_summary="Insufficient confidence or cash for an executable candidate.",
                idempotency_key=f"{summary.symbol}-{summary.source_event_id}-HOLD",
            )

        return OrderIntent(
            intent_type=OrderIntentType.OPEN_POSITION,
            symbol=summary.symbol,
            asset_class=AssetClass.EQUITY,
            strategy=Strategy.LONG_STOCK,
            direction=Direction.BULLISH,
            quantity=1,
            confidence=summary.confidence,
            max_loss_usd=125.50,
            rationale_summary="Constructive research supports one-share simulated exposure.",
            idempotency_key=f"{summary.symbol}-{summary.source_event_id}-LONG_STOCK",
        )
