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
