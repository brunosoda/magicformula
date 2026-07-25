"""Shared file-path helpers so scripts and the Streamlit app agree on where data lives."""
import glob
import os
from datetime import datetime

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PACKAGE_DIR)

DATA_FILE_PATTERN = "magic_formula_nyse_*.csv"
RANKING_FILENAME = "ranking_magic_formula_nyse.csv"


def data_file_path(date: datetime | None = None) -> str:
    """Path for a raw fundamentals CSV, date-stamped DDMMYYYY."""
    date = date or datetime.now()
    filename = f"magic_formula_nyse_{date.strftime('%d%m%Y')}.csv"
    return os.path.join(BASE_DIR, filename)


def ranking_file_path() -> str:
    """Path for the single, always-latest ranking CSV."""
    return os.path.join(BASE_DIR, RANKING_FILENAME)


def latest_data_file() -> str | None:
    """Most recently modified raw fundamentals CSV, or None if none exist."""
    candidates = glob.glob(os.path.join(BASE_DIR, DATA_FILE_PATTERN))
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)
