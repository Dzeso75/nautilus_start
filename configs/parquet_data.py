from pathlib import Path

from nautilus_trader.persistence.catalog import ParquetDataCatalog

PARQUET_DATA = "parquet_in"
PARQUET_RESULTS = "parquet_out"

class ParquetConfig:    
   
    def __init__(self, path: str = PARQUET_DATA):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.catalog = ParquetDataCatalog(self.path)

