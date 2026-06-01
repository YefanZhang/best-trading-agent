from importlib.metadata import version

import best_trading_agent


def test_package_imports() -> None:
    assert best_trading_agent.__all__ == ["__version__"]
    assert best_trading_agent.__version__ == version("best-trading-agent")
