import os
import urllib.request
from pathlib import Path

from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.persistence.loaders import CSVTickDataLoader
from nautilus_trader.persistence.wranglers import QuoteTickDataWrangler
from nautilus_trader.test_kit.providers import TestInstrumentProvider


# Change to project root directory
original_cwd = os.getcwd()
# project_root = os.path.abspath(os.path.join(os.getcwd(), "nautilus_project", "data"))
# os.chdir(project_root)

print(f"Working directory: {os.getcwd()}")

# Create catalog directory
catalog_path = Path("parquet")
catalog_path.mkdir(exist_ok=True)

print(f"Catalog directory: {catalog_path.absolute()}")

try:
    # Download EUR/USD sample data
    print("Downloading EUR/USD sample data...")
    url = "https://raw.githubusercontent.com/nautechsystems/nautilus_data/main/raw_data/fx_hist_data/DAT_ASCII_EURUSD_T_202001.csv.gz"
    filename = "EURUSD_202001.csv.gz"

    print(f"Downloading from: {url}")
    urllib.request.urlretrieve(url, filename)  # noqa: S310
    print("Download complete")

    # Create the instrument using the current schema (includes multiplier)
    print("Creating EUR/USD instrument...")
    instrument = TestInstrumentProvider.default_fx_ccy("EUR/USD")

    # Load and process the tick data
    print("Loading tick data...")
    wrangler = QuoteTickDataWrangler(instrument)

    df = CSVTickDataLoader.load(
        filename,
        index_col=0,
        datetime_format="%Y%m%d %H%M%S%f",
    )
    df.columns = ["bid_price", "ask_price", "size"]
    print(f"Loaded {len(df)} ticks")

    # Process ticks
    print("Processing ticks...")
    ticks = wrangler.process(df)

    # Write to catalog
    print("Writing data to catalog...")
    catalog = ParquetDataCatalog(str(catalog_path))

    # Write instrument first
    catalog.write_data([instrument])
    print("Instrument written to catalog")

    # Write tick data
    catalog.write_data(ticks)
    print("Tick data written to catalog")

    # Verify what was written
    print("\nVerifying catalog contents...")
    test_catalog = ParquetDataCatalog(str(catalog_path))
    loaded_instruments = test_catalog.instruments()
    print(f"Instruments in catalog: {[str(i.id) for i in loaded_instruments]}")

    # Clean up downloaded file
    os.unlink(filename)
    print("\nData setup complete!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    os.chdir(original_cwd)
    print(f"Changed back to: {os.getcwd()}")