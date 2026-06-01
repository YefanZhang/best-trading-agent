# Research Assistant MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working `best-trading-agent` MVP: a local-first US equities/options research assistant with a Python backend, TypeScript web workbench, CLI, SQLite persistence, provider-neutral LLM interface, free/public data adapter seams, and deterministic mocked research workflow.

**Architecture:** The backend owns domain models, persistence, data adapters, research orchestration, report assembly, FastAPI routes, SSE progress, and CLI commands. The frontend is a React/TypeScript workbench that calls the API and renders run progress, report sections, trade ideas, warnings, and source drilldowns. All live data and real LLM providers sit behind interfaces so tests use deterministic fixtures and stubs.

**Tech Stack:** Python 3.11+, FastAPI, Typer, SQLAlchemy 2.x, Pydantic 2.x, pytest, Ruff, mypy, uv; React, TypeScript, Vite, Vitest, Testing Library, Playwright, npm.

---

## File Structure

- `pyproject.toml`: Python package metadata, dependencies, CLI entry point, and tool configuration.
- `package.json`, `frontend/package.json`: JavaScript workspace scripts and frontend dependencies.
- `Makefile`: common setup/test/dev commands.
- `README.md`: local development and MVP usage.
- `src/best_trading_agent/domain/models.py`: domain dataclasses/enums for tickers, sources, runs, reports, options snapshots, warnings, and trade ideas.
- `src/best_trading_agent/storage/database.py`: SQLite engine/session setup.
- `src/best_trading_agent/storage/schema.py`: SQLAlchemy tables.
- `src/best_trading_agent/storage/repositories.py`: repository methods for runs, sources, reports, snapshots, warnings, and watchlist entries.
- `src/best_trading_agent/data/adapters.py`: data adapter protocols and deterministic fixture adapters.
- `src/best_trading_agent/llm/providers.py`: provider-neutral LLM protocol and deterministic development provider.
- `src/best_trading_agent/research/service.py`: orchestration for data collection, report generation, status transitions, warnings, and source audit trail.
- `src/best_trading_agent/api/main.py`: FastAPI app factory and route registration.
- `src/best_trading_agent/api/routes.py`: REST and SSE routes.
- `src/best_trading_agent/cli.py`: Typer CLI that calls backend services.
- `frontend/src/api/client.ts`: typed API client.
- `frontend/src/App.tsx`: workbench shell and state orchestration.
- `frontend/src/components/*.tsx`: focused UI components for watchlist, run form, progress, report, trade ideas, warnings, and source drawer.
- `tests/backend/*`: backend unit and integration tests.
- `frontend/src/**/*.test.tsx`: frontend component and API-client tests.
- `tests/e2e/*`: CLI and web smoke tests with mocked backend data.

---

## Task 1: Repository Scaffold And Tooling

**Files:**
- Create: `/Users/yefanzhang/workplace/best-trading-agent/pyproject.toml`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/package.json`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/Makefile`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/README.md`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/__init__.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_scaffold.py`

- [ ] **Step 1: Write the failing scaffold test**

Create `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_scaffold.py`:

```python
from importlib.metadata import version

import best_trading_agent


def test_package_imports() -> None:
    assert best_trading_agent.__all__ == ["__version__"]
    assert best_trading_agent.__version__ == version("best-trading-agent")
```

- [ ] **Step 2: Add Python project metadata and package init**

Create `/Users/yefanzhang/workplace/best-trading-agent/pyproject.toml`:

```toml
[project]
name = "best-trading-agent"
version = "0.1.0"
description = "Local-first equities and options research assistant."
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",
  "pydantic>=2.8.0",
  "sqlalchemy>=2.0.32",
  "typer>=0.12.5",
  "uvicorn>=0.30.6",
]

[project.optional-dependencies]
dev = [
  "httpx>=0.27.0",
  "mypy>=1.11.0",
  "pytest>=8.3.0",
  "pytest-asyncio>=0.23.8",
  "ruff>=0.6.2",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests/backend"]
pythonpath = ["src"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
packages = ["best_trading_agent"]
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/__init__.py`:

```python
from importlib.metadata import version

__version__ = version("best-trading-agent")
__all__ = ["__version__"]
```

- [ ] **Step 3: Add JavaScript workspace and common commands**

Create `/Users/yefanzhang/workplace/best-trading-agent/package.json`:

```json
{
  "name": "best-trading-agent-workspace",
  "private": true,
  "scripts": {
    "test": "if [ -f frontend/package.json ]; then npm --prefix frontend test; else echo \"frontend/package.json not found; skipping frontend test\"; fi",
    "dev": "if [ -f frontend/package.json ]; then npm --prefix frontend run dev; else echo \"frontend/package.json not found; skipping frontend dev\"; fi",
    "build": "if [ -f frontend/package.json ]; then npm --prefix frontend run build; else echo \"frontend/package.json not found; skipping frontend build\"; fi",
    "typecheck": "if [ -f frontend/package.json ]; then npm --prefix frontend run typecheck; else echo \"frontend/package.json not found; skipping frontend typecheck\"; fi"
  }
}
```

Create `/Users/yefanzhang/workplace/best-trading-agent/Makefile`:

```make
.PHONY: install test lint typecheck backend frontend

install:
	uv sync --extra dev
	@if [ -f frontend/package.json ]; then \
		npm --prefix frontend ci; \
	fi

test:
	uv run pytest
	@if [ -f frontend/package.json ]; then \
		npm --prefix frontend test -- --run; \
	else \
		echo "frontend/package.json not found; skipping frontend test"; \
	fi

lint:
	uv run ruff check .

typecheck:
	uv run mypy src
	@if [ -f frontend/package.json ]; then \
		npm --prefix frontend run typecheck; \
	else \
		echo "frontend/package.json not found; skipping frontend typecheck"; \
	fi

backend:
	@echo "Backend available after API scaffolding in Task 6"

frontend:
	@if [ -f frontend/package.json ]; then \
		npm --prefix frontend run dev; \
	else \
		echo "frontend/package.json not found; skipping frontend dev"; \
	fi
```

Create `/Users/yefanzhang/workplace/best-trading-agent/README.md`:

```markdown
# best-trading-agent

Local-first research assistant for US equities and listed options.

## Development

```bash
uv sync --extra dev
npm --prefix frontend ci
uv run pytest
```

The backend will expose a FastAPI API and Typer CLI. The frontend will be a TypeScript workbench.
```

- [ ] **Step 4: Run scaffold test**

Run:

```bash
uv run pytest /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_scaffold.py -v
```

Expected: `1 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/pyproject.toml /Users/yefanzhang/workplace/best-trading-agent/package.json /Users/yefanzhang/workplace/best-trading-agent/Makefile /Users/yefanzhang/workplace/best-trading-agent/README.md /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/__init__.py /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_scaffold.py
git commit -m "chore: scaffold project tooling"
```

---

## Task 2: Domain Models

**Files:**
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/domain/__init__.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/domain/models.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_domain_models.py`

- [ ] **Step 1: Write model behavior tests**

Create `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_domain_models.py`:

```python
from datetime import UTC, datetime

from best_trading_agent.domain.models import (
    DataWarning,
    Report,
    ReportSection,
    ResearchRun,
    RunStatus,
    SourceDocument,
    SourceType,
    TradeIdea,
)


def test_research_run_defaults_to_pending() -> None:
    run = ResearchRun(id="run-1", ticker="NVDA", created_at=datetime(2026, 5, 31, tzinfo=UTC))

    assert run.status is RunStatus.PENDING
    assert run.ticker == "NVDA"
    assert run.warnings == []


def test_report_keeps_evidence_and_trade_ideas_separate() -> None:
    source = SourceDocument(
        id="src-1",
        run_id="run-1",
        source_type=SourceType.NEWS,
        title="Catalyst",
        url="https://example.com/news",
        retrieved_at=datetime(2026, 5, 31, tzinfo=UTC),
        payload={"headline": "Example"},
    )
    report = Report(
        id="report-1",
        run_id="run-1",
        sections=[
            ReportSection(
                title="Catalysts",
                body="Example catalyst summary",
                source_ids=[source.id],
            )
        ],
        trade_ideas=[
            TradeIdea(
                structure="Call spread",
                thesis="Upside with defined risk",
                risk_notes=["Can expire worthless"],
                source_ids=[source.id],
            )
        ],
        warnings=[DataWarning(source="news", message="One RSS feed unavailable")],
    )

    assert report.sections[0].title == "Catalysts"
    assert report.trade_ideas[0].structure == "Call spread"
    assert report.warnings[0].message == "One RSS feed unavailable"
```

- [ ] **Step 2: Implement domain models**

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/domain/__init__.py`:

```python
from best_trading_agent.domain.models import (
    DataWarning,
    OptionContract,
    OptionsSnapshot,
    Report,
    ReportSection,
    ResearchRun,
    RunStatus,
    SourceDocument,
    SourceType,
    TradeIdea,
)

__all__ = [
    "DataWarning",
    "OptionContract",
    "OptionsSnapshot",
    "Report",
    "ReportSection",
    "ResearchRun",
    "RunStatus",
    "SourceDocument",
    "SourceType",
    "TradeIdea",
]
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/domain/models.py`:

```python
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
```

- [ ] **Step 3: Run model tests**

Run:

```bash
uv run pytest /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_domain_models.py -v
```

Expected: `2 passed`.

- [ ] **Step 4: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/domain /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_domain_models.py
git commit -m "feat: add research domain models"
```

---

## Task 3: SQLite Persistence

**Files:**
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/__init__.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/database.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/schema.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/repositories.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_repositories.py`

- [ ] **Step 1: Write repository tests**

Create `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_repositories.py`:

```python
from datetime import UTC, datetime

from best_trading_agent.domain.models import (
    DataWarning,
    Report,
    ReportSection,
    ResearchRun,
    RunStatus,
    SourceDocument,
    SourceType,
    TradeIdea,
)
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema


def test_repository_persists_run_sources_and_report() -> None:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_schema(session_factory)
    repo = ResearchRepository(session_factory)

    run = ResearchRun(id="run-1", ticker="NVDA", created_at=datetime(2026, 5, 31, tzinfo=UTC))
    repo.save_run(run)
    repo.update_run_status(run.id, RunStatus.COMPLETED_WITH_WARNINGS, [DataWarning("news", "RSS unavailable")])
    repo.save_source(
        SourceDocument(
            id="src-1",
            run_id=run.id,
            source_type=SourceType.NEWS,
            title="News",
            url="https://example.com",
            retrieved_at=datetime(2026, 5, 31, tzinfo=UTC),
            payload={"headline": "Example"},
        )
    )
    repo.save_report(
        Report(
            id="report-1",
            run_id=run.id,
            sections=[ReportSection("Summary", "Body", ["src-1"])],
            trade_ideas=[TradeIdea("Call spread", "Defined risk upside", ["Risk"], ["src-1"])],
            warnings=[DataWarning("news", "RSS unavailable")],
        )
    )

    stored_run = repo.get_run(run.id)
    stored_report = repo.get_report_for_run(run.id)

    assert stored_run is not None
    assert stored_run.status is RunStatus.COMPLETED_WITH_WARNINGS
    assert stored_run.warnings[0].source == "news"
    assert repo.list_sources(run.id)[0].payload["headline"] == "Example"
    assert stored_report is not None
    assert stored_report.trade_ideas[0].structure == "Call spread"
```

- [ ] **Step 2: Implement database setup and schema**

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/__init__.py`:

```python
from best_trading_agent.storage.database import SessionFactory, create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema

__all__ = ["ResearchRepository", "SessionFactory", "create_schema", "create_session_factory"]
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/database.py`:

```python
from collections.abc import Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

SessionFactory = Callable[[], Session]


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    engine = create_engine(database_url, future=True)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/schema.py`:

```python
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class RunRecord(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    ticker: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String)
    warnings: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)

    sources: Mapped[list["SourceRecord"]] = relationship(back_populates="run")
    report: Mapped["ReportRecord | None"] = relationship(back_populates="run")


class SourceRecord(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    source_type: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    retrieved_at: Mapped[Any] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)

    run: Mapped[RunRecord] = relationship(back_populates="sources")


class ReportRecord(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), unique=True, index=True)
    sections: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    trade_ideas: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    warnings: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)

    run: Mapped[RunRecord] = relationship(back_populates="report")


def create_schema(session_factory: sessionmaker[Session]) -> None:
    bind = session_factory.kw["bind"]
    Base.metadata.create_all(bind)
```

- [ ] **Step 3: Implement repository mapping**

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/repositories.py`:

```python
from sqlalchemy.orm import Session, sessionmaker

from best_trading_agent.domain.models import (
    DataWarning,
    Report,
    ReportSection,
    ResearchRun,
    RunStatus,
    SourceDocument,
    SourceType,
    TradeIdea,
)
from best_trading_agent.storage.schema import ReportRecord, RunRecord, SourceRecord


class ResearchRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_run(self, run: ResearchRun) -> None:
        with self._session_factory() as session:
            session.add(
                RunRecord(
                    id=run.id,
                    ticker=run.ticker,
                    created_at=run.created_at,
                    status=run.status.value,
                    warnings=[warning.__dict__ for warning in run.warnings],
                )
            )
            session.commit()

    def update_run_status(
        self, run_id: str, status: RunStatus, warnings: list[DataWarning] | None = None
    ) -> None:
        with self._session_factory() as session:
            record = session.get(RunRecord, run_id)
            if record is None:
                raise KeyError(f"Run not found: {run_id}")
            record.status = status.value
            if warnings is not None:
                record.warnings = [warning.__dict__ for warning in warnings]
            session.commit()

    def get_run(self, run_id: str) -> ResearchRun | None:
        with self._session_factory() as session:
            record = session.get(RunRecord, run_id)
            if record is None:
                return None
            return ResearchRun(
                id=record.id,
                ticker=record.ticker,
                created_at=record.created_at,
                status=RunStatus(record.status),
                warnings=[DataWarning(**warning) for warning in record.warnings],
            )

    def list_runs(self) -> list[ResearchRun]:
        with self._session_factory() as session:
            records = session.query(RunRecord).order_by(RunRecord.created_at.desc()).all()
            return [
                ResearchRun(
                    id=record.id,
                    ticker=record.ticker,
                    created_at=record.created_at,
                    status=RunStatus(record.status),
                    warnings=[DataWarning(**warning) for warning in record.warnings],
                )
                for record in records
            ]

    def save_source(self, source: SourceDocument) -> None:
        with self._session_factory() as session:
            session.add(
                SourceRecord(
                    id=source.id,
                    run_id=source.run_id,
                    source_type=source.source_type.value,
                    title=source.title,
                    url=source.url,
                    retrieved_at=source.retrieved_at,
                    payload=source.payload,
                )
            )
            session.commit()

    def list_sources(self, run_id: str) -> list[SourceDocument]:
        with self._session_factory() as session:
            records = session.query(SourceRecord).filter_by(run_id=run_id).all()
            return [
                SourceDocument(
                    id=record.id,
                    run_id=record.run_id,
                    source_type=SourceType(record.source_type),
                    title=record.title,
                    url=record.url,
                    retrieved_at=record.retrieved_at,
                    payload=record.payload,
                )
                for record in records
            ]

    def save_report(self, report: Report) -> None:
        with self._session_factory() as session:
            session.add(
                ReportRecord(
                    id=report.id,
                    run_id=report.run_id,
                    sections=[section.__dict__ for section in report.sections],
                    trade_ideas=[idea.__dict__ for idea in report.trade_ideas],
                    warnings=[warning.__dict__ for warning in report.warnings],
                )
            )
            session.commit()

    def get_report_for_run(self, run_id: str) -> Report | None:
        with self._session_factory() as session:
            record = session.query(ReportRecord).filter_by(run_id=run_id).one_or_none()
            if record is None:
                return None
            return Report(
                id=record.id,
                run_id=record.run_id,
                sections=[ReportSection(**section) for section in record.sections],
                trade_ideas=[TradeIdea(**idea) for idea in record.trade_ideas],
                warnings=[DataWarning(**warning) for warning in record.warnings],
            )
```

- [ ] **Step 4: Run repository tests**

Run:

```bash
uv run pytest /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_repositories.py -v
```

Expected: `1 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_repositories.py
git commit -m "feat: add sqlite research repository"
```

---

## Task 4: Adapter And LLM Interfaces

**Files:**
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/data/__init__.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/data/adapters.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/llm/__init__.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/llm/providers.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_adapters_and_llm.py`

- [ ] **Step 1: Write adapter/provider tests**

Create `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_adapters_and_llm.py`:

```python
import pytest

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.llm.providers import DeterministicResearchProvider


@pytest.mark.asyncio
async def test_fixture_adapter_returns_sources_options_and_warning() -> None:
    adapter = FixtureResearchDataAdapter()

    result = await adapter.collect("NVDA", run_id="run-1")

    assert {source.source_type.value for source in result.sources} == {"market", "options", "sec", "news"}
    assert result.options_snapshot is not None
    assert result.options_snapshot.contracts[0].symbol.startswith("NVDA")
    assert result.warnings[0].source == "news"


@pytest.mark.asyncio
async def test_deterministic_provider_generates_evidence_and_trade_idea() -> None:
    adapter = FixtureResearchDataAdapter()
    provider = DeterministicResearchProvider()
    data = await adapter.collect("NVDA", run_id="run-1")

    report = await provider.generate_report("run-1", "NVDA", data.sources, data.options_snapshot, data.warnings)

    assert report.run_id == "run-1"
    assert report.sections[0].title == "Market Snapshot"
    assert report.trade_ideas[0].structure == "Defined-risk call spread"
    assert report.warnings == data.warnings
```

- [ ] **Step 2: Implement data adapter interface and fixture adapter**

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/data/__init__.py`:

```python
from best_trading_agent.data.adapters import CollectedResearchData, FixtureResearchDataAdapter, ResearchDataAdapter

__all__ = ["CollectedResearchData", "FixtureResearchDataAdapter", "ResearchDataAdapter"]
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/data/adapters.py`:

```python
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from best_trading_agent.domain.models import (
    DataWarning,
    OptionContract,
    OptionsSnapshot,
    SourceDocument,
    SourceType,
)


@dataclass(frozen=True)
class CollectedResearchData:
    sources: list[SourceDocument]
    options_snapshot: OptionsSnapshot | None
    warnings: list[DataWarning]


class ResearchDataAdapter(Protocol):
    async def collect(self, ticker: str, run_id: str) -> CollectedResearchData:
        raise NotImplementedError


class FixtureResearchDataAdapter:
    async def collect(self, ticker: str, run_id: str) -> CollectedResearchData:
        retrieved_at = datetime(2026, 5, 31, tzinfo=UTC)
        upper_ticker = ticker.upper()
        sources = [
            SourceDocument(
                id=f"{run_id}-market",
                run_id=run_id,
                source_type=SourceType.MARKET,
                title=f"{upper_ticker} market snapshot",
                url=None,
                retrieved_at=retrieved_at,
                payload={"price": 125.0, "volume": 42000000},
            ),
            SourceDocument(
                id=f"{run_id}-options",
                run_id=run_id,
                source_type=SourceType.OPTIONS,
                title=f"{upper_ticker} options chain snapshot",
                url=None,
                retrieved_at=retrieved_at,
                payload={"front_expiry": "2026-06-19", "iv_rank": 0.58},
            ),
            SourceDocument(
                id=f"{run_id}-sec",
                run_id=run_id,
                source_type=SourceType.SEC,
                title=f"{upper_ticker} latest filing excerpt",
                url="https://www.sec.gov/",
                retrieved_at=retrieved_at,
                payload={"filing": "10-Q", "summary": "Revenue growth remains positive."},
            ),
            SourceDocument(
                id=f"{run_id}-news",
                run_id=run_id,
                source_type=SourceType.NEWS,
                title=f"{upper_ticker} catalyst feed",
                url="https://example.com/rss",
                retrieved_at=retrieved_at,
                payload={"headline": "Analysts discuss AI demand outlook."},
            ),
        ]
        snapshot = OptionsSnapshot(
            id=f"{run_id}-options-snapshot",
            run_id=run_id,
            ticker=upper_ticker,
            retrieved_at=retrieved_at,
            contracts=[
                OptionContract(
                    symbol=f"{upper_ticker}260619C00130000",
                    expiration="2026-06-19",
                    strike=130.0,
                    option_type="call",
                    bid=4.2,
                    ask=4.5,
                    implied_volatility=0.52,
                    volume=1200,
                    open_interest=8800,
                )
            ],
        )
        warnings = [DataWarning(source="news", message="Fixture RSS feed represents partial news coverage")]
        return CollectedResearchData(sources=sources, options_snapshot=snapshot, warnings=warnings)
```

- [ ] **Step 3: Implement provider-neutral LLM interface and deterministic provider**

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/llm/__init__.py`:

```python
from best_trading_agent.llm.providers import DeterministicResearchProvider, ResearchLLMProvider

__all__ = ["DeterministicResearchProvider", "ResearchLLMProvider"]
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/llm/providers.py`:

```python
from typing import Protocol

from best_trading_agent.domain.models import (
    DataWarning,
    OptionsSnapshot,
    Report,
    ReportSection,
    SourceDocument,
    TradeIdea,
)


class ResearchLLMProvider(Protocol):
    async def generate_report(
        self,
        run_id: str,
        ticker: str,
        sources: list[SourceDocument],
        options_snapshot: OptionsSnapshot | None,
        warnings: list[DataWarning],
    ) -> Report:
        raise NotImplementedError


class DeterministicResearchProvider:
    async def generate_report(
        self,
        run_id: str,
        ticker: str,
        sources: list[SourceDocument],
        options_snapshot: OptionsSnapshot | None,
        warnings: list[DataWarning],
    ) -> Report:
        source_ids = [source.id for source in sources]
        sections = [
            ReportSection(
                title="Market Snapshot",
                body=f"{ticker.upper()} fixture snapshot includes price, volume, filings, catalysts, and options context.",
                source_ids=source_ids,
            ),
            ReportSection(
                title="Options Context",
                body=(
                    "Front-expiry implied volatility and contract activity are available."
                    if options_snapshot is not None
                    else "Options data was unavailable for this run."
                ),
                source_ids=[source.id for source in sources if source.source_type.value == "options"],
            ),
            ReportSection(
                title="Bull Base Bear",
                body="Bull: catalysts continue. Base: current trend persists. Bear: demand or valuation disappoints.",
                source_ids=source_ids,
            ),
        ]
        trade_ideas = [
            TradeIdea(
                structure="Defined-risk call spread",
                thesis="Potential upside participation while limiting premium at risk.",
                risk_notes=[
                    "Can expire worthless.",
                    "Spread caps upside.",
                    "Fixture data is not live market data.",
                ],
                source_ids=source_ids,
            )
        ]
        return Report(
            id=f"{run_id}-report",
            run_id=run_id,
            sections=sections,
            trade_ideas=trade_ideas,
            warnings=warnings,
        )
```

- [ ] **Step 4: Run adapter/provider tests**

Run:

```bash
uv run pytest /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_adapters_and_llm.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/data /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/llm /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_adapters_and_llm.py
git commit -m "feat: add research adapter and llm provider seams"
```

---

## Task 5: Research Orchestration Service

**Files:**
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/research/__init__.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/research/service.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_research_service.py`

- [ ] **Step 1: Write orchestration tests**

Create `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_research_service.py`:

```python
import pytest

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.domain.models import RunStatus
from best_trading_agent.llm.providers import DeterministicResearchProvider
from best_trading_agent.research.service import ResearchService
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema


@pytest.mark.asyncio
async def test_research_service_persists_completed_run_with_warnings() -> None:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_schema(session_factory)
    repo = ResearchRepository(session_factory)
    service = ResearchService(repo, FixtureResearchDataAdapter(), DeterministicResearchProvider())

    result = await service.run_research("nvda")

    stored_run = repo.get_run(result.run.id)
    stored_report = repo.get_report_for_run(result.run.id)
    sources = repo.list_sources(result.run.id)

    assert stored_run is not None
    assert stored_run.ticker == "NVDA"
    assert stored_run.status is RunStatus.COMPLETED_WITH_WARNINGS
    assert len(sources) == 4
    assert stored_report is not None
    assert stored_report.trade_ideas[0].structure == "Defined-risk call spread"
```

- [ ] **Step 2: Implement orchestration service**

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/research/__init__.py`:

```python
from best_trading_agent.research.service import ResearchResult, ResearchService

__all__ = ["ResearchResult", "ResearchService"]
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/research/service.py`:

```python
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from best_trading_agent.data.adapters import ResearchDataAdapter
from best_trading_agent.domain.models import Report, ResearchRun, RunStatus
from best_trading_agent.llm.providers import ResearchLLMProvider
from best_trading_agent.storage.repositories import ResearchRepository


@dataclass(frozen=True)
class ResearchResult:
    run: ResearchRun
    report: Report


class ResearchService:
    def __init__(
        self,
        repository: ResearchRepository,
        data_adapter: ResearchDataAdapter,
        llm_provider: ResearchLLMProvider,
    ) -> None:
        self._repository = repository
        self._data_adapter = data_adapter
        self._llm_provider = llm_provider

    async def run_research(self, ticker: str) -> ResearchResult:
        normalized_ticker = ticker.upper().strip()
        run = ResearchRun(id=f"run-{uuid4().hex}", ticker=normalized_ticker, created_at=datetime.now(UTC))
        self._repository.save_run(run)
        self._repository.update_run_status(run.id, RunStatus.RUNNING)

        try:
            collected = await self._data_adapter.collect(normalized_ticker, run.id)
            for source in collected.sources:
                self._repository.save_source(source)
            report = await self._llm_provider.generate_report(
                run.id,
                normalized_ticker,
                collected.sources,
                collected.options_snapshot,
                collected.warnings,
            )
            self._repository.save_report(report)
            final_status = (
                RunStatus.COMPLETED_WITH_WARNINGS if collected.warnings else RunStatus.COMPLETED
            )
            self._repository.update_run_status(run.id, final_status, collected.warnings)
            stored_run = self._repository.get_run(run.id)
            if stored_run is None:
                raise RuntimeError(f"Run disappeared after save: {run.id}")
            return ResearchResult(run=stored_run, report=report)
        except Exception:
            self._repository.update_run_status(run.id, RunStatus.FAILED)
            raise
```

- [ ] **Step 3: Run service tests**

Run:

```bash
uv run pytest /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_research_service.py -v
```

Expected: `1 passed`.

- [ ] **Step 4: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/research /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_research_service.py
git commit -m "feat: orchestrate research runs"
```

---

## Task 6: FastAPI And CLI

**Files:**
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/pyproject.toml`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api/__init__.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api/main.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api/routes.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/cli.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_api_and_cli.py`

- [ ] **Step 1: Write API and CLI tests**

Create `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_api_and_cli.py`:

```python
from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from best_trading_agent.api.main import create_app
from best_trading_agent.cli import app as cli_app


def test_api_runs_research_and_returns_report(tmp_path: Path) -> None:
    client = TestClient(create_app(f"sqlite+pysqlite:///{tmp_path / 'api.db'}"))

    response = client.post("/api/runs", json={"ticker": "nvda"})

    assert response.status_code == 201
    body = response.json()
    assert body["run"]["ticker"] == "NVDA"
    assert body["run"]["status"] == "completed_with_warnings"
    assert body["report"]["trade_ideas"][0]["structure"] == "Defined-risk call spread"


def test_cli_research_command_outputs_run_summary(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        ["--database-url", f"sqlite+pysqlite:///{tmp_path / 'cli.db'}", "research", "nvda"],
    )

    assert result.exit_code == 0
    assert "NVDA" in result.output
    assert "completed_with_warnings" in result.output
    assert "Defined-risk call spread" in result.output
```

- [ ] **Step 2: Implement FastAPI routes**

Add the CLI entry point to `/Users/yefanzhang/workplace/best-trading-agent/pyproject.toml` immediately before `[build-system]`:

```toml
[project.scripts]
best-trading-agent = "best_trading_agent.cli:app"
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api/__init__.py`:

```python
from best_trading_agent.api.main import create_app

__all__ = ["create_app"]
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api/main.py`:

```python
from fastapi import FastAPI

from best_trading_agent.api.routes import router
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.schema import create_schema


def create_app(database_url: str = "sqlite+pysqlite:///best-trading-agent.db") -> FastAPI:
    session_factory = create_session_factory(database_url)
    create_schema(session_factory)
    app = FastAPI(title="best-trading-agent")
    app.state.session_factory = session_factory
    app.include_router(router, prefix="/api")
    return app
```

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api/routes.py`:

```python
from typing import Any

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.domain.models import Report, ResearchRun
from best_trading_agent.llm.providers import DeterministicResearchProvider
from best_trading_agent.research.service import ResearchService
from best_trading_agent.storage.repositories import ResearchRepository

router = APIRouter()


class RunRequest(BaseModel):
    ticker: str


def _run_to_dict(run: ResearchRun) -> dict[str, Any]:
    return {
        "id": run.id,
        "ticker": run.ticker,
        "created_at": run.created_at.isoformat(),
        "status": run.status.value,
        "warnings": [warning.__dict__ for warning in run.warnings],
    }


def _report_to_dict(report: Report) -> dict[str, Any]:
    return {
        "id": report.id,
        "run_id": report.run_id,
        "sections": [section.__dict__ for section in report.sections],
        "trade_ideas": [idea.__dict__ for idea in report.trade_ideas],
        "warnings": [warning.__dict__ for warning in report.warnings],
    }


@router.post("/runs", status_code=status.HTTP_201_CREATED)
async def create_run(payload: RunRequest, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    service = ResearchService(repository, FixtureResearchDataAdapter(), DeterministicResearchProvider())
    result = await service.run_research(payload.ticker)
    return {"run": _run_to_dict(result.run), "report": _report_to_dict(result.report)}


@router.get("/runs")
async def list_runs(request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    return {"runs": [_run_to_dict(run) for run in repository.list_runs()]}
```

- [ ] **Step 3: Implement CLI**

Create `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/cli.py`:

```python
import asyncio
from typing import Annotated

import typer

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.llm.providers import DeterministicResearchProvider
from best_trading_agent.research.service import ResearchService
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main(
    ctx: typer.Context,
    database_url: Annotated[
        str,
        typer.Option("--database-url", help="SQLAlchemy database URL."),
    ] = "sqlite+pysqlite:///best-trading-agent.db",
) -> None:
    ctx.obj = {"database_url": database_url}


@app.command()
def research(ctx: typer.Context, ticker: str) -> None:
    session_factory = create_session_factory(ctx.obj["database_url"])
    create_schema(session_factory)
    repository = ResearchRepository(session_factory)
    service = ResearchService(repository, FixtureResearchDataAdapter(), DeterministicResearchProvider())
    result = asyncio.run(service.run_research(ticker))
    typer.echo(f"{result.run.ticker} {result.run.status.value} {result.run.id}")
    for section in result.report.sections:
        typer.echo(f"- {section.title}: {section.body}")
    for idea in result.report.trade_ideas:
        typer.echo(f"Trade idea: {idea.structure} - {idea.thesis}")


@app.command("runs-list")
def runs_list(ctx: typer.Context) -> None:
    session_factory = create_session_factory(ctx.obj["database_url"])
    create_schema(session_factory)
    repository = ResearchRepository(session_factory)
    for run in repository.list_runs():
        typer.echo(f"{run.id} {run.ticker} {run.status.value}")
```

- [ ] **Step 4: Run API and CLI tests**

Run:

```bash
uv run pytest /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_api_and_cli.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/cli.py /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_api_and_cli.py
git commit -m "feat: expose research through api and cli"
```

---

## Task 7: TypeScript Frontend Scaffold

**Files:**
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/package.json`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/index.html`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/tsconfig.json`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/vite.config.ts`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/main.tsx`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.tsx`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.test.tsx`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/styles.css`

- [ ] **Step 1: Add frontend dependencies and Vite config**

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/package.json`:

```json
{
  "name": "best-trading-agent-frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "typecheck": "tsc -b",
    "test": "vitest"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.2",
    "typescript": "^5.5.4",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.468.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.4.8",
    "@testing-library/react": "^16.0.1",
    "@testing-library/user-event": "^14.5.2",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "jsdom": "^24.1.1",
    "vitest": "^2.0.5"
  }
}
```

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/vite.config.ts`:

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/testSetup.ts",
  },
});
```

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src", "vite.config.ts"]
}
```

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>best-trading-agent</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 2: Write initial frontend test**

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/testSetup.ts`:

```ts
import "@testing-library/jest-dom/vitest";
```

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the research workbench shell", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Research Workbench" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start research" })).toBeInTheDocument();
  });
});
```

- [ ] **Step 3: Implement workbench shell**

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/main.tsx`:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";

import { App } from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.tsx`:

```tsx
import { Play } from "lucide-react";

export function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">best-trading-agent</div>
        <nav>
          <a href="#research">Research</a>
          <a href="#watchlist">Watchlist</a>
          <a href="#sources">Sources</a>
          <a href="#settings">Settings</a>
        </nav>
      </aside>
      <section className="workspace" id="research">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">US equities and options</p>
            <h1>Research Workbench</h1>
          </div>
          <button className="primary-button" type="button">
            <Play size={18} aria-hidden="true" />
            Start research
          </button>
        </header>
        <section className="panel-grid" aria-label="Research panels">
          <div className="panel">Ticker command</div>
          <div className="panel">Market snapshot</div>
          <div className="panel">Catalysts</div>
          <div className="panel wide">Generated memo</div>
        </section>
      </section>
    </main>
  );
}
```

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/styles.css`:

```css
:root {
  color: #1f2933;
  background: #f4f6f8;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

body {
  margin: 0;
}

a {
  color: inherit;
  text-decoration: none;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px 1fr;
}

.sidebar {
  background: #17202a;
  color: #f8fafc;
  padding: 24px;
}

.brand {
  font-weight: 700;
  margin-bottom: 32px;
}

.sidebar nav {
  display: grid;
  gap: 14px;
  color: #d7dde5;
}

.workspace {
  padding: 32px;
}

.workspace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #667085;
  font-size: 0.82rem;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: 2rem;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 0;
  border-radius: 6px;
  padding: 10px 14px;
  color: #ffffff;
  background: #0f766e;
  font-weight: 700;
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.panel {
  min-height: 140px;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  background: #ffffff;
  padding: 18px;
  font-weight: 700;
}

.wide {
  grid-column: 1 / -1;
}

@media (max-width: 800px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    padding: 16px;
  }

  .workspace {
    padding: 20px;
  }

  .workspace-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .panel-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 4: Run frontend scaffold test**

Run:

```bash
npm --prefix /Users/yefanzhang/workplace/best-trading-agent/frontend test -- --run /Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.test.tsx
```

Expected: one passing test file.

- [ ] **Step 5: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/frontend
git commit -m "feat: scaffold research workbench frontend"
```

---

## Task 8: Frontend API Client And Workbench States

**Files:**
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/api/client.ts`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/RunForm.tsx`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/ReportView.tsx`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.tsx`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/api/client.test.ts`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.test.tsx`

- [ ] **Step 1: Write API client test**

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/api/client.test.ts`:

```ts
import { describe, expect, it, vi } from "vitest";

import { createResearchRun } from "./client";

describe("createResearchRun", () => {
  it("posts ticker and returns run result", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        run: { id: "run-1", ticker: "NVDA", status: "completed_with_warnings", warnings: [] },
        report: { id: "report-1", run_id: "run-1", sections: [], trade_ideas: [], warnings: [] },
      }),
    });

    const result = await createResearchRun("nvda", fetchMock);

    expect(fetchMock).toHaveBeenCalledWith("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker: "nvda" }),
    });
    expect(result.run.ticker).toBe("NVDA");
  });
});
```

- [ ] **Step 2: Implement typed API client**

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/api/client.ts`:

```ts
export type RunStatus = "pending" | "running" | "completed" | "completed_with_warnings" | "failed";

export type DataWarning = {
  source: string;
  message: string;
};

export type ResearchRun = {
  id: string;
  ticker: string;
  status: RunStatus;
  warnings: DataWarning[];
};

export type ReportSection = {
  title: string;
  body: string;
  source_ids: string[];
};

export type TradeIdea = {
  structure: string;
  thesis: string;
  risk_notes: string[];
  source_ids: string[];
};

export type Report = {
  id: string;
  run_id: string;
  sections: ReportSection[];
  trade_ideas: TradeIdea[];
  warnings: DataWarning[];
};

export type ResearchResult = {
  run: ResearchRun;
  report: Report;
};

export async function createResearchRun(
  ticker: string,
  fetcher: typeof fetch = fetch,
): Promise<ResearchResult> {
  const response = await fetcher("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker }),
  });
  if (!response.ok) {
    throw new Error(`Research request failed: ${response.status}`);
  }
  return response.json() as Promise<ResearchResult>;
}
```

- [ ] **Step 3: Write workbench state test**

Replace `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.test.tsx` with:

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("runs research and renders report with separated trade ideas", async () => {
    const user = userEvent.setup();
    const createRun = vi.fn().mockResolvedValue({
      run: {
        id: "run-1",
        ticker: "NVDA",
        status: "completed_with_warnings",
        warnings: [{ source: "news", message: "Partial coverage" }],
      },
      report: {
        id: "report-1",
        run_id: "run-1",
        sections: [{ title: "Market Snapshot", body: "Fixture body", source_ids: ["src-1"] }],
        trade_ideas: [
          {
            structure: "Defined-risk call spread",
            thesis: "Upside with limited premium risk",
            risk_notes: ["Can expire worthless"],
            source_ids: ["src-1"],
          },
        ],
        warnings: [{ source: "news", message: "Partial coverage" }],
      },
    });

    render(<App createRun={createRun} />);
    await user.clear(screen.getByLabelText("Ticker"));
    await user.type(screen.getByLabelText("Ticker"), "nvda");
    await user.click(screen.getByRole("button", { name: "Start research" }));

    expect(await screen.findByText("Market Snapshot")).toBeInTheDocument();
    expect(screen.getByText("Defined-risk call spread")).toBeInTheDocument();
    expect(screen.getByText("Partial coverage")).toBeInTheDocument();
  });
});
```

- [ ] **Step 4: Implement form and report components**

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/RunForm.tsx`:

```tsx
import { Play } from "lucide-react";
import { FormEvent, useState } from "react";

type RunFormProps = {
  disabled: boolean;
  onSubmit: (ticker: string) => void;
};

export function RunForm({ disabled, onSubmit }: RunFormProps) {
  const [ticker, setTicker] = useState("NVDA");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(ticker);
  }

  return (
    <form className="run-form" onSubmit={handleSubmit}>
      <label>
        Ticker
        <input value={ticker} onChange={(event) => setTicker(event.target.value)} />
      </label>
      <button className="primary-button" disabled={disabled} type="submit">
        <Play size={18} aria-hidden="true" />
        Start research
      </button>
    </form>
  );
}
```

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/ReportView.tsx`:

```tsx
import type { Report, ResearchRun } from "../api/client";

type ReportViewProps = {
  run: ResearchRun;
  report: Report;
};

export function ReportView({ run, report }: ReportViewProps) {
  return (
    <section className="report-view" aria-label="Research report">
      <div className="status-line">
        <strong>{run.ticker}</strong>
        <span>{run.status}</span>
      </div>
      {report.warnings.length > 0 ? (
        <section className="warning-list" aria-label="Warnings">
          {report.warnings.map((warning) => (
            <p key={`${warning.source}-${warning.message}`}>
              <strong>{warning.source}:</strong> {warning.message}
            </p>
          ))}
        </section>
      ) : null}
      <section>
        <h2>Evidence memo</h2>
        {report.sections.map((section) => (
          <article className="report-card" key={section.title}>
            <h3>{section.title}</h3>
            <p>{section.body}</p>
          </article>
        ))}
      </section>
      <section>
        <h2>Trade ideas</h2>
        {report.trade_ideas.map((idea) => (
          <article className="report-card" key={idea.structure}>
            <h3>{idea.structure}</h3>
            <p>{idea.thesis}</p>
            <ul>
              {idea.risk_notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          </article>
        ))}
      </section>
    </section>
  );
}
```

- [ ] **Step 5: Wire App to API client**

Replace `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.tsx` with:

```tsx
import { useState } from "react";

import { createResearchRun, type ResearchResult } from "./api/client";
import { ReportView } from "./components/ReportView";
import { RunForm } from "./components/RunForm";

type AppProps = {
  createRun?: (ticker: string) => Promise<ResearchResult>;
};

export function App({ createRun = createResearchRun }: AppProps) {
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun(ticker: string) {
    setIsRunning(true);
    setError(null);
    try {
      setResult(await createRun(ticker));
    } catch (error) {
      setError(error instanceof Error ? error.message : "Research request failed");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">best-trading-agent</div>
        <nav>
          <a href="#research">Research</a>
          <a href="#watchlist">Watchlist</a>
          <a href="#sources">Sources</a>
          <a href="#settings">Settings</a>
        </nav>
      </aside>
      <section className="workspace" id="research">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">US equities and options</p>
            <h1>Research Workbench</h1>
          </div>
          <RunForm disabled={isRunning} onSubmit={handleRun} />
        </header>
        {isRunning ? <p className="status-line">Running research...</p> : null}
        {error ? <p role="alert">{error}</p> : null}
        {result ? (
          <ReportView report={result.report} run={result.run} />
        ) : (
          <section className="panel-grid" aria-label="Research panels">
            <div className="panel">Ticker command</div>
            <div className="panel">Market snapshot</div>
            <div className="panel">Catalysts</div>
            <div className="panel wide">Generated memo</div>
          </section>
        )}
      </section>
    </main>
  );
}
```

Append to `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/styles.css`:

```css
.run-form {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.run-form label {
  display: grid;
  gap: 6px;
  font-weight: 700;
}

.run-form input {
  min-width: 140px;
  border: 1px solid #bcccdc;
  border-radius: 6px;
  padding: 10px 12px;
}

.primary-button:disabled {
  opacity: 0.6;
}

.status-line {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.report-view {
  display: grid;
  gap: 20px;
}

.warning-list {
  border: 1px solid #f5c2c7;
  border-radius: 8px;
  background: #fff5f5;
  padding: 12px 16px;
}

.report-card {
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
  margin-bottom: 12px;
}
```

- [ ] **Step 6: Run frontend tests**

Run:

```bash
npm --prefix /Users/yefanzhang/workplace/best-trading-agent/frontend test -- --run
```

Expected: all frontend tests pass.

- [ ] **Step 7: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/frontend/src
git commit -m "feat: connect workbench to research api"
```

---

## Task 9: Integration Verification And Documentation

**Files:**
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/README.md`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_contracts.py`

- [ ] **Step 1: Write contract test covering backend vertical slice**

Create `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_contracts.py`:

```python
from pathlib import Path

from fastapi.testclient import TestClient

from best_trading_agent.api.main import create_app


def test_api_contract_contains_report_warnings_and_trade_ideas(tmp_path: Path) -> None:
    client = TestClient(create_app(f"sqlite+pysqlite:///{tmp_path / 'contract.db'}"))

    result = client.post("/api/runs", json={"ticker": "NVDA"}).json()

    assert set(result) == {"run", "report"}
    assert {"id", "ticker", "created_at", "status", "warnings"} <= set(result["run"])
    assert {"id", "run_id", "sections", "trade_ideas", "warnings"} <= set(result["report"])
    assert result["report"]["sections"][0]["source_ids"]
    assert result["report"]["trade_ideas"][0]["risk_notes"]
    assert result["report"]["warnings"][0]["message"]
```

- [ ] **Step 2: Update README with exact usage**

Replace `/Users/yefanzhang/workplace/best-trading-agent/README.md` with:

```markdown
# best-trading-agent

Local-first research assistant for US equities and listed options.

## What works in the MVP

- Deterministic fixture-backed equity and options research run.
- SQLite persistence for runs, sources, reports, trade ideas, and warnings.
- FastAPI endpoint for starting research runs.
- Typer CLI for starting research runs and listing saved runs.
- React/TypeScript research workbench that calls the API.

The current data adapter is a deterministic development fixture. Live free/public adapters can be added behind the same adapter interface.

## Setup

```bash
uv sync --extra dev
npm --prefix frontend ci
```

## Test

```bash
uv run pytest
npm --prefix frontend test -- --run
```

## Run backend

```bash
uv run uvicorn best_trading_agent.api.main:create_app --factory --reload
```

## Run frontend

```bash
npm --prefix frontend run dev
```

## Run CLI

```bash
uv run best-trading-agent research NVDA
uv run best-trading-agent runs-list
```

## Scope boundaries

This project does not place trades, integrate with brokers, stream live quotes, or provide financial advice.
```

- [ ] **Step 3: Run full backend and frontend verification**

Run:

```bash
uv run pytest
npm --prefix /Users/yefanzhang/workplace/best-trading-agent/frontend test -- --run
npm --prefix /Users/yefanzhang/workplace/best-trading-agent/frontend run build
uv run ruff check .
uv run mypy /Users/yefanzhang/workplace/best-trading-agent/src
```

Expected:

- Backend tests pass.
- Frontend tests pass.
- Frontend build succeeds.
- Ruff succeeds.
- Mypy succeeds.

- [ ] **Step 4: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/README.md /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_contracts.py
git commit -m "test: verify mvp research contract"
```

---

## Task 10: Spec Coverage Hardening

**Files:**
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/domain/models.py`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/schema.py`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/repositories.py`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/research/service.py`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api/routes.py`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/cli.py`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.tsx`
- Modify: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/ReportView.tsx`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_spec_coverage.py`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/SourceDrawer.tsx`
- Create: `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/RunHistory.tsx`

- [ ] **Step 1: Write backend spec coverage tests**

Create `/Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_spec_coverage.py`:

```python
from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from best_trading_agent.api.main import create_app
from best_trading_agent.cli import app as cli_app


def test_api_exposes_history_sources_and_sse(tmp_path: Path) -> None:
    client = TestClient(create_app(f"sqlite+pysqlite:///{tmp_path / 'coverage.db'}"))
    created = client.post("/api/runs", json={"ticker": "NVDA"}).json()
    run_id = created["run"]["id"]

    assert client.get(f"/api/runs/{run_id}").json()["run"]["id"] == run_id
    sources = client.get(f"/api/runs/{run_id}/sources").json()["sources"]
    assert sources[0]["id"].startswith(run_id)

    events = client.get(f"/api/runs/{run_id}/events")
    assert events.status_code == 200
    assert "text/event-stream" in events.headers["content-type"]
    assert "event: status" in events.text
    assert "completed_with_warnings" in events.text


def test_cli_exposes_nested_run_and_source_commands(tmp_path: Path) -> None:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'cli-coverage.db'}"
    runner = CliRunner()
    research = runner.invoke(cli_app, ["--database-url", database_url, "research", "NVDA"])
    run_id = research.output.splitlines()[0].split()[-1]

    runs_list = runner.invoke(cli_app, ["--database-url", database_url, "runs", "list"])
    runs_show = runner.invoke(cli_app, ["--database-url", database_url, "runs", "show", run_id])
    sources_show = runner.invoke(
        cli_app,
        ["--database-url", database_url, "sources", "show", f"{run_id}-market"],
    )

    assert runs_list.exit_code == 0
    assert run_id in runs_list.output
    assert runs_show.exit_code == 0
    assert "completed_with_warnings" in runs_show.output
    assert sources_show.exit_code == 0
    assert "market snapshot" in sources_show.output
```

- [ ] **Step 2: Add watchlist and options snapshot domain models**

Append these dataclasses to `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/domain/models.py`:

```python
@dataclass(frozen=True)
class WatchlistEntry:
    ticker: str
    created_at: datetime
```

Update `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/domain/__init__.py` so it imports and exports `WatchlistEntry`.

- [ ] **Step 3: Add storage records for options snapshots and watchlist entries**

Append these records to `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/schema.py`:

```python
class OptionsSnapshotRecord(Base):
    __tablename__ = "options_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    ticker: Mapped[str] = mapped_column(String, index=True)
    retrieved_at: Mapped[Any] = mapped_column(DateTime(timezone=True))
    contracts: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    warnings: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)


class WatchlistRecord(Base):
    __tablename__ = "watchlist"

    ticker: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True))
```

- [ ] **Step 4: Add repository methods for snapshots, watchlist, and source lookup**

Extend `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/storage/repositories.py` with these imports:

```python
from datetime import UTC, datetime

from best_trading_agent.domain.models import OptionContract, OptionsSnapshot, WatchlistEntry
from best_trading_agent.storage.schema import OptionsSnapshotRecord, WatchlistRecord
```

Add these methods to `ResearchRepository`:

```python
    def save_options_snapshot(self, snapshot: OptionsSnapshot) -> None:
        with self._session_factory() as session:
            session.add(
                OptionsSnapshotRecord(
                    id=snapshot.id,
                    run_id=snapshot.run_id,
                    ticker=snapshot.ticker,
                    retrieved_at=snapshot.retrieved_at,
                    contracts=[contract.__dict__ for contract in snapshot.contracts],
                    warnings=[warning.__dict__ for warning in snapshot.warnings],
                )
            )
            session.commit()

    def get_options_snapshot(self, run_id: str) -> OptionsSnapshot | None:
        with self._session_factory() as session:
            record = session.query(OptionsSnapshotRecord).filter_by(run_id=run_id).one_or_none()
            if record is None:
                return None
            return OptionsSnapshot(
                id=record.id,
                run_id=record.run_id,
                ticker=record.ticker,
                retrieved_at=record.retrieved_at,
                contracts=[OptionContract(**contract) for contract in record.contracts],
                warnings=[DataWarning(**warning) for warning in record.warnings],
            )

    def get_source(self, source_id: str) -> SourceDocument | None:
        with self._session_factory() as session:
            record = session.get(SourceRecord, source_id)
            if record is None:
                return None
            return SourceDocument(
                id=record.id,
                run_id=record.run_id,
                source_type=SourceType(record.source_type),
                title=record.title,
                url=record.url,
                retrieved_at=record.retrieved_at,
                payload=record.payload,
            )

    def add_watchlist_entry(self, ticker: str) -> WatchlistEntry:
        entry = WatchlistEntry(ticker=ticker.upper(), created_at=datetime.now(UTC))
        with self._session_factory() as session:
            session.merge(WatchlistRecord(ticker=entry.ticker, created_at=entry.created_at))
            session.commit()
        return entry

    def list_watchlist_entries(self) -> list[WatchlistEntry]:
        with self._session_factory() as session:
            records = session.query(WatchlistRecord).order_by(WatchlistRecord.ticker.asc()).all()
            return [WatchlistEntry(ticker=record.ticker, created_at=record.created_at) for record in records]
```

- [ ] **Step 5: Persist options snapshot during research**

In `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/research/service.py`, after saving sources and before generating the report, add:

```python
            if collected.options_snapshot is not None:
                self._repository.save_options_snapshot(collected.options_snapshot)
            self._repository.add_watchlist_entry(normalized_ticker)
```

- [ ] **Step 6: Add API routes for run history, sources, and SSE status**

Extend `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/api/routes.py` with:

```python
from fastapi import HTTPException
from fastapi.responses import StreamingResponse


def _source_to_dict(source: SourceDocument) -> dict[str, Any]:
    return {
        "id": source.id,
        "run_id": source.run_id,
        "source_type": source.source_type.value,
        "title": source.title,
        "url": source.url,
        "retrieved_at": source.retrieved_at.isoformat(),
        "payload": source.payload,
    }


@router.get("/runs/{run_id}")
async def get_run(run_id: str, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    run = repository.get_run(run_id)
    report = repository.get_report_for_run(run_id)
    if run is None or report is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"run": _run_to_dict(run), "report": _report_to_dict(report)}


@router.get("/runs/{run_id}/sources")
async def list_run_sources(run_id: str, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    return {"sources": [_source_to_dict(source) for source in repository.list_sources(run_id)]}


@router.get("/sources/{source_id}")
async def get_source(source_id: str, request: Request) -> dict[str, Any]:
    repository = ResearchRepository(request.app.state.session_factory)
    source = repository.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"source": _source_to_dict(source)}


@router.get("/runs/{run_id}/events")
async def run_events(run_id: str, request: Request) -> StreamingResponse:
    repository = ResearchRepository(request.app.state.session_factory)
    run = repository.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    async def stream() -> AsyncIterator[str]:
        yield f"event: status\ndata: {run.status.value}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
```

Also add this import near the top of the same file:

```python
from collections.abc import AsyncIterator

from best_trading_agent.domain.models import SourceDocument
```

- [ ] **Step 7: Replace flat CLI history command with nested commands**

Replace `/Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent/cli.py` with:

```python
import asyncio
from typing import Annotated

import typer

from best_trading_agent.data.adapters import FixtureResearchDataAdapter
from best_trading_agent.llm.providers import DeterministicResearchProvider
from best_trading_agent.research.service import ResearchService
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema

app = typer.Typer(no_args_is_help=True)
runs_app = typer.Typer(no_args_is_help=True)
sources_app = typer.Typer(no_args_is_help=True)
app.add_typer(runs_app, name="runs")
app.add_typer(sources_app, name="sources")


def _repository(database_url: str) -> ResearchRepository:
    session_factory = create_session_factory(database_url)
    create_schema(session_factory)
    return ResearchRepository(session_factory)


@app.callback()
def main(
    ctx: typer.Context,
    database_url: Annotated[
        str,
        typer.Option("--database-url", help="SQLAlchemy database URL."),
    ] = "sqlite+pysqlite:///best-trading-agent.db",
) -> None:
    ctx.obj = {"database_url": database_url}


@app.command()
def research(ctx: typer.Context, ticker: str) -> None:
    repository = _repository(ctx.obj["database_url"])
    service = ResearchService(repository, FixtureResearchDataAdapter(), DeterministicResearchProvider())
    result = asyncio.run(service.run_research(ticker))
    typer.echo(f"{result.run.ticker} {result.run.status.value} {result.run.id}")
    for section in result.report.sections:
        typer.echo(f"- {section.title}: {section.body}")
    for idea in result.report.trade_ideas:
        typer.echo(f"Trade idea: {idea.structure} - {idea.thesis}")


@runs_app.command("list")
def runs_list(ctx: typer.Context) -> None:
    for run in _repository(ctx.obj["database_url"]).list_runs():
        typer.echo(f"{run.id} {run.ticker} {run.status.value}")


@runs_app.command("show")
def runs_show(ctx: typer.Context, run_id: str) -> None:
    repository = _repository(ctx.obj["database_url"])
    run = repository.get_run(run_id)
    report = repository.get_report_for_run(run_id)
    if run is None or report is None:
        raise typer.BadParameter(f"Run not found: {run_id}")
    typer.echo(f"{run.id} {run.ticker} {run.status.value}")
    for section in report.sections:
        typer.echo(f"- {section.title}: {section.body}")
    for idea in report.trade_ideas:
        typer.echo(f"Trade idea: {idea.structure} - {idea.thesis}")


@sources_app.command("show")
def sources_show(ctx: typer.Context, source_id: str) -> None:
    source = _repository(ctx.obj["database_url"]).get_source(source_id)
    if source is None:
        raise typer.BadParameter(f"Source not found: {source_id}")
    typer.echo(f"{source.id} {source.source_type.value} {source.title}")
    typer.echo(source.payload)
```

- [ ] **Step 8: Add source drawer and run history UI**

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/SourceDrawer.tsx`:

```tsx
import type { ReportSection } from "../api/client";

type SourceDrawerProps = {
  sections: ReportSection[];
};

export function SourceDrawer({ sections }: SourceDrawerProps) {
  const sourceIds = Array.from(new Set(sections.flatMap((section) => section.source_ids)));

  return (
    <aside className="source-drawer" aria-label="Source drawer">
      <h2>Sources</h2>
      {sourceIds.map((sourceId) => (
        <button className="source-chip" key={sourceId} type="button">
          {sourceId}
        </button>
      ))}
    </aside>
  );
}
```

Create `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/RunHistory.tsx`:

```tsx
import type { ResearchRun } from "../api/client";

type RunHistoryProps = {
  runs: ResearchRun[];
};

export function RunHistory({ runs }: RunHistoryProps) {
  return (
    <section className="run-history" aria-label="Run history">
      <h2>Run history</h2>
      {runs.length === 0 ? <p>No saved runs yet.</p> : null}
      {runs.map((run) => (
        <article key={run.id}>
          <strong>{run.ticker}</strong>
          <span>{run.status}</span>
        </article>
      ))}
    </section>
  );
}
```

Update `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/components/ReportView.tsx` to import `SourceDrawer` and render it after the trade ideas section:

```tsx
import { SourceDrawer } from "./SourceDrawer";
```

```tsx
      <SourceDrawer sections={report.sections} />
```

Update `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.tsx` to keep a run history:

```tsx
import { RunHistory } from "./components/RunHistory";
```

```tsx
  const [runs, setRuns] = useState<ResearchResult["run"][]>([]);
```

Inside `handleRun`, replace `setResult(await createRun(ticker));` with:

```tsx
      const nextResult = await createRun(ticker);
      setResult(nextResult);
      setRuns((existingRuns) => [nextResult.run, ...existingRuns]);
```

Render history after the report or empty panels:

```tsx
        <RunHistory runs={runs} />
```

- [ ] **Step 9: Update frontend tests for source drawer and history**

Extend `/Users/yefanzhang/workplace/best-trading-agent/frontend/src/App.test.tsx` with these assertions after the existing report assertions:

```tsx
    expect(screen.getByLabelText("Source drawer")).toBeInTheDocument();
    expect(screen.getByText("src-1")).toBeInTheDocument();
    expect(screen.getByLabelText("Run history")).toBeInTheDocument();
```

- [ ] **Step 10: Run spec coverage verification**

Run:

```bash
uv run pytest /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_spec_coverage.py -v
npm --prefix /Users/yefanzhang/workplace/best-trading-agent/frontend test -- --run
uv run pytest
```

Expected:

- Backend spec coverage tests pass.
- Frontend tests pass.
- Full backend suite passes.

- [ ] **Step 11: Commit**

Run:

```bash
git add /Users/yefanzhang/workplace/best-trading-agent/src/best_trading_agent /Users/yefanzhang/workplace/best-trading-agent/tests/backend/test_spec_coverage.py /Users/yefanzhang/workplace/best-trading-agent/frontend/src
git commit -m "feat: complete mvp spec coverage"
```
