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
