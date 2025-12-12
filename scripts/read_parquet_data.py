import os
from pathlib import Path
from nautilus_trader.persistence.catalog import ParquetDataCatalog

# Load the catalog from the project root directory
# project_root = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
# catalog_path = os.path.join(project_root, "catalog")

original_cwd = os.getcwd()
catalog_path = Path("parquet")

catalog = ParquetDataCatalog(catalog_path)
instruments = catalog.instruments()

print(f"Loaded catalog from: {catalog_path}")
print(f"Available instruments: {[str(i.id) for i in instruments]}")

if instruments:
    print(f"\nUsing instrument: {instruments[0].id}")
else:
    print("\nNo instruments found. Please run the data download cell first.")