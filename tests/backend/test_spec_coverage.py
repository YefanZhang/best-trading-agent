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
