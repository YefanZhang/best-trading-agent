from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

from best_trading_agent.cli import app as cli_app
from best_trading_agent.domain.trading import RiskDecisionStatus
from best_trading_agent.storage.database import create_session_factory
from best_trading_agent.storage.repositories import ResearchRepository
from best_trading_agent.storage.schema import create_schema
from best_trading_agent.trading.service import TradingLoopService, TradingScenario


def _repo() -> ResearchRepository:
    session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
    create_schema(session_factory)
    return ResearchRepository(session_factory)


def test_trading_loop_approved_demo_persists_replayable_audit_record() -> None:
    repo = _repo()
    now = datetime(2026, 6, 7, 16, 0, tzinfo=UTC)

    result = TradingLoopService(repo).run_demo("nvda", TradingScenario.APPROVED, now=now)
    audits = repo.list_trading_audit_records()

    assert result.risk_decision.decision is RiskDecisionStatus.APPROVED
    assert result.simulated_order is not None
    assert result.final_state.positions[0].symbol == "NVDA"
    assert len(audits) == 1
    assert audits[0].id == result.audit_record.id
    assert audits[0].market_event.id == result.market_event.id
    assert audits[0].simulated_order is not None
    assert audits[0].final_state.positions[0].quantity == 1


def test_trading_loop_non_approved_demo_persists_audit_without_execution() -> None:
    repo = _repo()
    now = datetime(2026, 6, 7, 16, 0, tzinfo=UTC)

    approval_required = TradingLoopService(repo).run_demo(
        "nvda",
        TradingScenario.APPROVAL_REQUIRED,
        now=now,
    )
    rejected = TradingLoopService(repo).run_demo("aapl", TradingScenario.REJECTED, now=now)
    audits = repo.list_trading_audit_records()

    assert approval_required.risk_decision.decision is RiskDecisionStatus.APPROVAL_REQUIRED
    assert approval_required.simulated_order is None
    assert rejected.risk_decision.decision is RiskDecisionStatus.REJECTED
    assert rejected.simulated_order is None
    assert len(audits) == 2


def test_cli_trading_demo_outputs_trace_and_audit_id(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_app,
        [
            "--database-url",
            f"sqlite+pysqlite:///{tmp_path / 'trading-demo.db'}",
            "trading-demo",
            "NVDA",
            "--scenario",
            "approved",
        ],
    )

    assert result.exit_code == 0
    assert "NVDA approved" in result.output
    assert "Signal: OPEN_POSITION LONG_STOCK qty=1" in result.output
    assert "Risk: APPROVED" in result.output
    assert "Order: FILLED BUY 1 NVDA" in result.output
    assert "Audit: audit-" in result.output
