"""
crazyyaml package initialization.
Exports main API functions for YAML compression and decompression.
"""
from .crazyyaml import (
    yaml_to_crazy,
    crazy_to_yaml,
    load_crazy,
    store_data_to_crazy,
    DEFAULT_THRESHOLD,
    DEFAULT_DTYPE
)
