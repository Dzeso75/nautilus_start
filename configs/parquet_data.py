from pathlib import Path

from nautilus_trader.persistence.catalog import ParquetDataCatalog

PARQUET_DATA: str = "parquet_in"
PARQUET_RESULTS: str = "parquet_out"

class ParquetConfig:    
   
    def __init__(self, path: str, name: str):
        self.path = Path(path) / name
        self.path.mkdir(parents=True, exist_ok=True)
        self.catalog = ParquetDataCatalog(self.path)

