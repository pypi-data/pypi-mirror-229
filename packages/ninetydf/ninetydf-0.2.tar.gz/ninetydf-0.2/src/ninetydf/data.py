from io import StringIO

import pandas as pd

# Attempt to use the standard library resources module if available (Python 3.9+).
# Otherwise, fall back to the backported version.
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files


def _load_data(filename: str) -> pd.DataFrame:
    resource_path = files("ninetydf") / filename
    with resource_path.open(encoding="utf-8") as f:
        content = f.read()
    return pd.read_csv(StringIO(content))


def _load_seasons() -> pd.DataFrame:
    return _load_data("seasons.csv")


def _load_couples() -> pd.DataFrame:
    return _load_data("couples.csv")
