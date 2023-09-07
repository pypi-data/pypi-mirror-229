import importlib

from club404.encoders import Encoder, TextEncoder, HtmlEncoder, JsonEncoder, CsvEncoder, YamlEncoder

# Define common encoders
TEXT = TextEncoder()
HTML = HtmlEncoder()
JSON = JsonEncoder()
CSV = CsvEncoder()

# Register common encoders
Encoder.register(
    TEXT,
    HTML,
    CSV,
    JSON
)

# -----------------------------------------------------------------
# Load optional encoders only if the dependencies are installed
# -----------------------------------------------------------------
# Try and load the YAML encoder if `yaml` module found
YAML = None
try:
    YAML = YamlEncoder(importlib.import_module('yaml'))
    Encoder.register(YAML)
except ImportError:
    pass  # Module `yaml` not found...
