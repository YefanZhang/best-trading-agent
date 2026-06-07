from best_trading_agent.domain.trading import MarketEvent, ResearchSummary


class DeterministicTradingResearchAgent:
    def summarize(self, event: MarketEvent) -> ResearchSummary:
        return ResearchSummary(
            symbol=event.symbol,
            source_event_id=event.id,
            market_regime="RISK_ON",
            summary=(
                f"{event.symbol} closed at {event.price:.2f}. "
                "Fixture-backed context is constructive enough for a small test."
            ),
            bullish_factors=[
                "Latest bar closed with valid price data.",
                "Ticker is inside the large-cap/liquid universe for the MVP.",
            ],
            bearish_factors=["Fixture data is not live."],
            uncertainties=["Fixture market data is not live."],
            source_refs=[event.id],
            confidence=0.62,
        )
