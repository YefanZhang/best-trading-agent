from pathlib import Path

from fastapi.testclient import TestClient

from best_trading_agent.api.main import create_app


def test_api_runs_trading_demo_and_returns_audit_record(tmp_path: Path) -> None:
    client = TestClient(create_app(f"sqlite+pysqlite:///{tmp_path / 'trading-api.db'}"))

    response = client.post(
        "/api/trading/demo",
        json={"ticker": "nvda", "scenario": "approved"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["run_id"].startswith("trading-run-")
    assert body["market_event"]["symbol"] == "NVDA"
    assert body["signal_intent"]["intent_type"] == "OPEN_POSITION"
    assert body["risk_decision"]["decision"] == "APPROVED"
    assert body["simulated_order"]["status"] == "FILLED"
    assert body["audit_record"]["id"].startswith("audit-")
    assert body["audit_record"]["final_state"]["positions"][0]["quantity"] == 1


def test_api_lists_and_fetches_trading_audit_records(tmp_path: Path) -> None:
    client = TestClient(create_app(f"sqlite+pysqlite:///{tmp_path / 'trading-api.db'}"))
    created = client.post(
        "/api/trading/demo",
        json={"ticker": "nvda", "scenario": "approval-required"},
    ).json()
    audit_id = created["audit_record"]["id"]

    list_response = client.get("/api/trading/audits")
    get_response = client.get(f"/api/trading/audits/{audit_id}")
    missing_response = client.get("/api/trading/audits/missing")

    assert list_response.status_code == 200
    assert list_response.json()["audits"][0]["id"] == audit_id
    assert get_response.status_code == 200
    assert get_response.json()["audit"]["risk_decision"]["decision"] == "APPROVAL_REQUIRED"
    assert get_response.json()["audit"]["simulated_order"] is None
    assert missing_response.status_code == 404
