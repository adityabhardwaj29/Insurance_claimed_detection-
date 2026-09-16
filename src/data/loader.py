"""
src/data/loader.py
------------------
Backward-compatible shim. New code should use src.data.load_data directly.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def load_csv(relative_path: str) -> pd.DataFrame:
    """Load any CSV relative to the project root."""
    return pd.read_csv(ROOT / relative_path)


# Re-export modern API
try:
    from src.data.load_data import load_all_raw, load_raw_table  # noqa: F401
except ImportError:
    pass
