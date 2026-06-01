from pathlib import Path

from fastapi.testclient import TestClient

from best_trading_agent.api.main import create_app

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_api_contract_contains_report_warnings_and_trade_ideas(tmp_path: Path) -> None:
    client = TestClient(create_app(f"sqlite+pysqlite:///{tmp_path / 'contract.db'}"))

    result = client.post("/api/runs", json={"ticker": "NVDA"}).json()

    assert set(result) == {"run", "report"}
    assert {"id", "ticker", "created_at", "status", "warnings"} <= set(result["run"])
    assert {"id", "run_id", "sections", "trade_ideas", "warnings"} <= set(result["report"])
    assert result["report"]["sections"][0]["source_ids"]
    assert result["report"]["trade_ideas"][0]["risk_notes"]
    assert result["report"]["warnings"][0]["message"]


def test_readme_documents_mvp_setup_and_usage() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text()

    assert "## What works in the MVP" in readme
    assert "npm --prefix frontend ci" in readme
    assert "uv run best-trading-agent research NVDA" in readme
    assert "uv run best-trading-agent runs-list" in readme
    assert "does not place trades" in readme
