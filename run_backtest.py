# scripts/run_backtest.py
from nautilus_trader.backtest.node import BacktestNode
from nautilus_trader.backtest.results import BacktestResult
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model import Venue

from configs.backtest import get_backtest_config
from configs.parquet_data import ParquetConfig, PARQUET_RESULTS, PARQUET_DATA

data = ParquetConfig(PARQUET_DATA, "data")
results = ParquetConfig(PARQUET_RESULTS, "22")

# Get backtest configuration
config = get_backtest_config(data, results)
node = BacktestNode(configs=[config])

# Runs one or many configs synchronously
results: list[BacktestResult] = node.run()


# Analyze results
engine: BacktestEngine = node.get_engine(config.id)
# len(engine.trader.generate_order_fills_report())
# engine.trader.generate_positions_report()
# engine.trader.generate_account_report(Venue("SIM"))

# Get performance statistics]

# Get the account and positions
account = engine.trader.generate_account_report(Venue("SIM"))
positions = engine.trader.generate_positions_report()
orders = engine.trader.generate_order_fills_report()
orders_report = engine.trader.generate_orders_report()
fills_report = engine.trader.generate_fills_report()

# account.write(data.catalog)
# orders.to_parquet(data.path / "orders.parquet")
# orders_report.to_parquet(data.path / "orders_report.parquet")
# data.catalog.write_data(fills_report)
# # fills_report.to_parquet(data.path / "fills_report.parquet")
# account.to_parquet(data.path / "account.parquet")
# positions.to_parquet(data.path / "positions.parquet")

# Access portfolio analyzer
portfolio = engine.portfolio

# Get different categories of statistics
stats_pnls = portfolio.analyzer.get_performance_stats_pnls()
stats_returns = portfolio.analyzer.get_performance_stats_returns()
stats_general = portfolio.analyzer.get_performance_stats_general()

# stats_pnls.to_parquet(data.path / "stats_pnls.parquet")
# stats_returns.to_parquet(data.path / "stats_returns.parquet")
# stats_general.to_parquet(data.path / "stats_general.parquet")
# stats_pnls.write(data.catalog)

# data.catalog.write_data(stats_pnls)
# data.catalog.write_data(stats_returns)
# data.catalog.write_data(stats_general)

# Get the positions and orders
# Print summary statistics
print("=== STRATEGY PERFORMANCE ===")
print(f"Total Orders: {len(orders)}")
print(f"Total Positions: {len(positions)}")

if len(positions) > 0:
    # Convert P&L strings to numeric values
    positions["pnl_numeric"] = positions["realized_pnl"].apply(
        lambda x: float(str(x).replace(" USD", "").replace(",", "")) if isinstance(x, str) else float(x)
    )

    # Calculate win rate
    winning_trades = positions[positions["pnl_numeric"] > 0]
    losing_trades = positions[positions["pnl_numeric"] < 0]

    win_rate = len(winning_trades) / len(positions) * 100 if len(positions) > 0 else 0

    print(f"\nWin Rate: {win_rate:.1f}%")
    print(f"Winning Trades: {len(winning_trades)}")
    print(f"Losing Trades: {len(losing_trades)}")

    # Calculate returns
    total_pnl = positions["pnl_numeric"].sum()
    avg_pnl = positions["pnl_numeric"].mean()
    max_win = positions["pnl_numeric"].max()
    max_loss = positions["pnl_numeric"].min()

    print(f"\nTotal P&L: {total_pnl:.2f} USD")
    print(f"Average P&L: {avg_pnl:.2f} USD")
    print(f"Best Trade: {max_win:.2f} USD")
    print(f"Worst Trade: {max_loss:.2f} USD")

    # Calculate risk metrics if we have both wins and losses
    if len(winning_trades) > 0 and len(losing_trades) > 0:
        avg_win = winning_trades["pnl_numeric"].mean()
        avg_loss = abs(losing_trades["pnl_numeric"].mean())
        profit_factor = winning_trades["pnl_numeric"].sum() / abs(losing_trades["pnl_numeric"].sum())

        print(f"\nAverage Win: {avg_win:.2f} USD")
        print(f"Average Loss: {avg_loss:.2f} USD")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Risk/Reward Ratio: {avg_win/avg_loss:.2f}")
else:
    print("\nNo positions generated. Check strategy parameters.")

print("\n=== FINAL ACCOUNT STATE ===")
print(account.tail(1).to_string())