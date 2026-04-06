import os
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.config import EVALUATIONS_DIR, EXTERNAL_DATA_DIR, LOGS_DIR, MODELS_DIR, PROCESSED_DATA_DIR, PROJECTIONS_DIR, RAW_DATA_DIR


def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    return unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("utf-8")


def ensure_directories() -> None:
    for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EXTERNAL_DATA_DIR, MODELS_DIR, PROJECTIONS_DIR, EVALUATIONS_DIR, LOGS_DIR]:
        Path(path).mkdir(parents=True, exist_ok=True)


def require_columns(df: pd.DataFrame, required_cols: Iterable[str], df_name: str = "DataFrame") -> None:
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required columns: {missing}")


def get_nba_day_string(offset_days: int = 0, hour_shift: int = 6) -> str:
    return (datetime.now() - timedelta(hours=hour_shift) + timedelta(days=offset_days)).strftime("%Y-%m-%d")


def get_env_or_raise(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value
