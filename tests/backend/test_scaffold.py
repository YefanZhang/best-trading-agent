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


def test_root_npm_scripts_skip_frontend_until_scaffolded() -> None:
    package_json = json.loads((PROJECT_ROOT / "package.json").read_text())

    assert not (PROJECT_ROOT / "frontend" / "package.json").exists()
    assert set(package_json["scripts"]) >= {"test", "dev", "build", "typecheck"}
    for script in ("test", "dev", "build", "typecheck"):
        result = subprocess.run(
            ["npm", "run", script],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "frontend/package.json not found" in result.stdout


def test_make_targets_skip_missing_later_scaffolds() -> None:
    for target, expected_output in (
        ("backend", "Backend available after API scaffolding"),
        ("frontend", "frontend/package.json not found"),
    ):
        result = subprocess.run(
            ["make", target],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert expected_output in result.stdout
