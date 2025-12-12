# scripts/run_backtest.py
from nautilus_trader.backtest.node import BacktestNode
from config.backtest import get_backtest_config


if __name__ == "__main__":
    config = get_backtest_config()
    node = BacktestNode(configs=[config])
    results = node.run()
    node.dispose()

    # Вывод результатов
    print("\n=== BACKTEST RESULTS ===")
    for run in results:
        print(run)