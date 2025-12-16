from pathlib import Path
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.model import QuoteTick
from nautilus_trader.config import ImportableStrategyConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.backtest.config import BacktestVenueConfig
from nautilus_trader.backtest.config import BacktestDataConfig
from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.config import BacktestRunConfig


def get_backtest_config():

    # Настройки инструмента
    venue_config = BacktestVenueConfig(
        name="SIM",
        oms_type="NETTING",
        account_type="MARGIN",
        base_currency="USD",
        starting_balances=["1_000_000 USD"]
    )

    # Загрузка данных
    catalog = ParquetDataCatalog(Path("parquet"))
    instruments = catalog.instruments()

    # Конфигурация данных
    data_config = BacktestDataConfig(
        catalog_path=str(catalog.path),
        data_cls=QuoteTick,
        instrument_id=instruments[0].id,
        end_time="2020-01-10",
    )

    # Конфигурация движка
    engine_config = BacktestEngineConfig(
        strategies=[
            ImportableStrategyConfig(
                strategy_path="strategies.macd:MACDStrategy",
                config_path="configs.macd:MACDConfig",
                config={
                "instrument_id": instruments[0].id,
                },
            )
        ],
        logging=LoggingConfig(
            log_level="ERROR",
            log_level_file = "WARN",
            log_directory="logs",
            log_file_name="backtest.log",
            clear_log_file = True
            ),
    )

    # Конфигурация запуска
    run_config = BacktestRunConfig(
        engine=engine_config,
        data=[data_config],
        venues=[venue_config],
    )

    return run_config