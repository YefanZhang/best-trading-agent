from datetime import UTC, datetime

from sqlalchemy.orm import Session, sessionmaker

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
    WatchlistEntry,
)
from best_trading_agent.domain.trading import TradingAuditRecord
from best_trading_agent.storage.schema import (
    OptionsSnapshotRecord,
    ReportRecord,
    RunRecord,
    SourceRecord,
    TradingAuditRecordRecord,
    WatchlistRecord,
)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class ResearchRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_run(self, run: ResearchRun) -> None:
        with self._session_factory() as session:
            session.add(
                RunRecord(
                    id=run.id,
                    ticker=run.ticker,
                    created_at=_as_utc(run.created_at),
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
                created_at=_as_utc(record.created_at),
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
                    created_at=_as_utc(record.created_at),
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
                    retrieved_at=_as_utc(source.retrieved_at),
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
                    retrieved_at=_as_utc(record.retrieved_at),
                    payload=record.payload,
                )
                for record in records
            ]

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
                retrieved_at=_as_utc(record.retrieved_at),
                payload=record.payload,
            )

    def save_options_snapshot(self, snapshot: OptionsSnapshot) -> None:
        with self._session_factory() as session:
            session.add(
                OptionsSnapshotRecord(
                    id=snapshot.id,
                    run_id=snapshot.run_id,
                    ticker=snapshot.ticker,
                    retrieved_at=_as_utc(snapshot.retrieved_at),
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
                retrieved_at=_as_utc(record.retrieved_at),
                contracts=[OptionContract(**contract) for contract in record.contracts],
                warnings=[DataWarning(**warning) for warning in record.warnings],
            )

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

    def add_watchlist_entry(self, ticker: str) -> WatchlistEntry:
        entry = WatchlistEntry(ticker=ticker.upper(), created_at=datetime.now(UTC))
        with self._session_factory() as session:
            session.merge(WatchlistRecord(ticker=entry.ticker, created_at=entry.created_at))
            session.commit()
        return entry

    def list_watchlist_entries(self) -> list[WatchlistEntry]:
        with self._session_factory() as session:
            records = session.query(WatchlistRecord).order_by(WatchlistRecord.ticker.asc()).all()
            return [
                WatchlistEntry(ticker=record.ticker, created_at=_as_utc(record.created_at))
                for record in records
            ]

    def save_trading_audit_record(self, audit_record: TradingAuditRecord) -> None:
        with self._session_factory() as session:
            session.add(
                TradingAuditRecordRecord(
                    id=audit_record.id,
                    run_id=audit_record.run_id,
                    created_at=_as_utc(audit_record.created_at),
                    payload=audit_record.model_dump(mode="json"),
                )
            )
            session.commit()

    def get_trading_audit_record(self, audit_id: str) -> TradingAuditRecord | None:
        with self._session_factory() as session:
            record = session.get(TradingAuditRecordRecord, audit_id)
            if record is None:
                return None
            return TradingAuditRecord.model_validate(record.payload)

    def list_trading_audit_records(self) -> list[TradingAuditRecord]:
        with self._session_factory() as session:
            records = (
                session.query(TradingAuditRecordRecord)
                .order_by(TradingAuditRecordRecord.created_at.asc())
                .all()
            )
            return [TradingAuditRecord.model_validate(record.payload) for record in records]
