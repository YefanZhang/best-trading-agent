from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)


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
