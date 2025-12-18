from nautilus_trader.persistence.config import StreamingConfig, DataCatalogConfig
import inspect

print(StreamingConfig)             # просто чтобы убедиться, что класс импортируется
print(inspect.signature(StreamingConfig))
help(StreamingConfig)
help(DataCatalogConfig)
