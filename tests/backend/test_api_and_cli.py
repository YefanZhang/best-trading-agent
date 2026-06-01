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
