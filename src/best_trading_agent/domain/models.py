from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"


class SourceType(StrEnum):
    MARKET = "market"
    OPTIONS = "options"
    SEC = "sec"
    NEWS = "news"
    LLM = "llm"


@dataclass(frozen=True)
class DataWarning:
    source: str
    message: str


@dataclass(frozen=True)
class ResearchRun:
    id: str
    ticker: str
    created_at: datetime
    status: RunStatus = RunStatus.PENDING
    warnings: list[DataWarning] = field(default_factory=list)


@dataclass(frozen=True)
class SourceDocument:
    id: str
    run_id: str
    source_type: SourceType
    title: str
    url: str | None
    retrieved_at: datetime
    payload: dict[str, Any]


@dataclass(frozen=True)
class OptionContract:
    symbol: str
    expiration: str
    strike: float
    option_type: str
    bid: float | None
    ask: float | None
    implied_volatility: float | None
    volume: int | None
    open_interest: int | None


@dataclass(frozen=True)
class OptionsSnapshot:
    id: str
    run_id: str
    ticker: str
    retrieved_at: datetime
    contracts: list[OptionContract]
    warnings: list[DataWarning] = field(default_factory=list)


@dataclass(frozen=True)
class ReportSection:
    title: str
    body: str
    source_ids: list[str]


@dataclass(frozen=True)
class TradeIdea:
    structure: str
    thesis: str
    risk_notes: list[str]
    source_ids: list[str]


@dataclass(frozen=True)
class Report:
    id: str
    run_id: str
    sections: list[ReportSection]
    trade_ideas: list[TradeIdea]
    warnings: list[DataWarning] = field(default_factory=list)
