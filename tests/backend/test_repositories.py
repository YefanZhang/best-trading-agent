from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

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
    repo.update_run_status(
        run.id, RunStatus.COMPLETED_WITH_WARNINGS, [DataWarning("news", "RSS unavailable")]
    )
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


def test_repository_preserves_utc_datetimes_after_round_trip() -> None:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_schema(session_factory)
    repo = ResearchRepository(session_factory)

    run = ResearchRun(id="run-1", ticker="NVDA", created_at=datetime(2026, 5, 31, tzinfo=UTC))
    source = SourceDocument(
        id="src-1",
        run_id=run.id,
        source_type=SourceType.NEWS,
        title="News",
        url="https://example.com",
        retrieved_at=datetime(2026, 6, 1, tzinfo=UTC),
        payload={"headline": "Example"},
    )

    repo.save_run(run)
    repo.save_source(source)

    stored_run = repo.get_run(run.id)
    stored_source = repo.list_sources(run.id)[0]

    assert stored_run is not None
    assert stored_run.created_at.tzinfo is UTC
    assert stored_source.retrieved_at.tzinfo is UTC


def test_repository_rejects_source_for_missing_run() -> None:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_schema(session_factory)
    repo = ResearchRepository(session_factory)

    source = SourceDocument(
        id="src-1",
        run_id="missing-run",
        source_type=SourceType.NEWS,
        title="News",
        url="https://example.com",
        retrieved_at=datetime(2026, 6, 1, tzinfo=UTC),
        payload={"headline": "Example"},
    )

    with pytest.raises(IntegrityError):
        repo.save_source(source)


def test_repository_rejects_report_for_missing_run() -> None:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_schema(session_factory)
    repo = ResearchRepository(session_factory)

    report = Report(
        id="report-1",
        run_id="missing-run",
        sections=[ReportSection("Summary", "Body", [])],
        trade_ideas=[],
    )

    with pytest.raises(IntegrityError):
        repo.save_report(report)
