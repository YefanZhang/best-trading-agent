from collections import defaultdict
from collections.abc import Callable

from best_trading_agent.domain.trading import MarketEvent, MarketEventType

TradingEventHandler = Callable[[MarketEvent], object]


class TradingEventDispatcher:
    def __init__(self) -> None:
        self._handlers: dict[MarketEventType, list[TradingEventHandler]] = defaultdict(list)

    def subscribe(
        self,
        event_type: MarketEventType,
        handler: TradingEventHandler,
    ) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: MarketEvent) -> list[object]:
        return [handler(event) for handler in self._handlers[event.event_type]]
