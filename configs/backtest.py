from configs.parquet_data import ParquetConfig
from nautilus_trader.model import QuoteTick
from nautilus_trader.config import ImportableStrategyConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.backtest.config import BacktestVenueConfig
from nautilus_trader.backtest.config import BacktestDataConfig
from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.config import BacktestRunConfig
from nautilus_trader.persistence.config import PersistenceConfig


def get_backtest_config(data: ParquetConfig, result: ParquetConfig):

    # Настройки инструмента
    venue_config = BacktestVenueConfig(
        name="SIM",
        oms_type="NETTING",
        account_type="MARGIN",
        base_currency="USD",
        starting_balances=["1_000_000 USD"]
    )

    # Загрузка данных
    # data = ParquetConfig()
    # result = ParquetConfig(PARQUET_RESULTS)
    instruments = data.catalog.instruments()

    # Конфигурация данных
    data_config = BacktestDataConfig(
        catalog_path=str(data.path),
        data_cls=QuoteTick,
        instrument_id=instruments[0].id,
        end_time="2020-01-10",
    )

    # Настройка сохранения
    persistence = PersistenceConfig(
        catalog_path=str(result.path),  # путь к папке Parquet
        fs_protocol="file",              # локальная файловая система
        # fs_storage_options={}         # опции для S3 и т.д. (не нужны для локального диска)
    )

    # Конфигурация движка
    engine_config = BacktestEngineConfig(
        persistence=persistence, 
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