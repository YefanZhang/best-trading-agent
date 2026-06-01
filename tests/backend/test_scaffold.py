import json
import subprocess
import tomllib
from importlib.metadata import version
from pathlib import Path

import best_trading_agent

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_package_imports() -> None:
    assert best_trading_agent.__all__ == ["__version__"]
    assert best_trading_agent.__version__ == version("best-trading-agent")


def test_console_script_waits_for_cli_scaffold() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["scripts"]["best-trading-agent"] == "best_trading_agent.cli:app"


def test_root_npm_scripts_delegate_to_frontend_after_scaffold() -> None:
    package_json = json.loads((PROJECT_ROOT / "package.json").read_text())

    assert (PROJECT_ROOT / "frontend" / "package.json").exists()
    assert set(package_json["scripts"]) >= {"test", "dev", "build", "typecheck"}
    assert "npm --prefix frontend test -- --run" in package_json["scripts"]["test"]

    for command, expected_output in (
        (["npm", "run", "test", "--", "--run"], "vitest --run"),
        (["npm", "run", "build"], "vite build"),
        (["npm", "run", "typecheck"], "tsc -b"),
    ):
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert expected_output in result.stdout


def test_make_targets_reflect_frontend_scaffold_without_starting_server() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text()

    backend_result = subprocess.run(
        ["make", "backend"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert backend_result.returncode == 0
    assert "Backend available after API scaffolding" in backend_result.stdout
    assert "npm --prefix frontend test -- --run" in makefile
    assert "npm --prefix frontend run typecheck" in makefile
    assert "npm --prefix frontend run dev" in makefile
