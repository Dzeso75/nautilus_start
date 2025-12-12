# config/backtest.py
import pandas as pd
from pathlib import Path
from nautilus_trader.backtest.config import BacktestDataConfig, BacktestEngineConfig, BacktestRunConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import LoggingConfig, RiskEngineConfig
from nautilus_trader.data.csv import CSVReader
from nautilus_trader.model.data import Bar
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.objects import Money
from strategies.sma_cross import SMACross


def get_backtest_config():
    # Настройки инструмента
    venue = Venue("SIM")
    symbol = Symbol("AAPL")
    instrument_id = InstrumentId(symbol, venue)

    # Загрузка данных
    data_path = Path("data/AAPL_1min.csv")
    df = pd.read_csv(data_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp")

    # Создание инструмента
    from nautilus_trader.model.instruments import Equity
    from nautilus_trader.model.objects import Price, Quantity

    instrument = Equity(
        instrument_id=instrument_id,
        native_symbol=symbol,
        currency="USD",
        price_precision=2,
        price_increment=Price(0.01, precision=2),
        multiplier=Quantity.from_int(1),
        lot_size=Quantity.from_int(1),
        isin="US0378331005",
        ts_event=0,
        ts_init=0,
    )

    # Конфигурация данных
    reader = CSVReader(block_parser=lambda df: [Bar.from_dict(r) for r in df.to_dict("records")])
    data_config = BacktestDataConfig(
        catalog_path=None,
        data_cls=Bar,
        instrument=instrument,
        reader=reader,
        path=str(data_path),
    )

    # Конфигурация движка
    engine_config = BacktestEngineConfig(
        trader_id="TRADER-001",
        logging=LoggingConfig(log_level="INFO"),
        risk_engine=RiskEngineConfig(
            account_type=AccountType.CASH,
            starting_balance=[Money(1_000_000, "USD")],
            oms_type=OmsType.NETTING,
        ),
    )

    # Конфигурация запуска
    run_config = BacktestRunConfig(
        engine=engine_config,
        data=[data_config],
        strategies=[
            {
                "strategy_path": "strategies.sma_cross:SMACross",
                "config": {"instrument_id": instrument_id, "fast_period": 10, "slow_period": 20},
            }
        ],
    )

    return run_config