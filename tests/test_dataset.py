from pathlib import Path

import pandas as pd
import pytest

from src.config import MODEL_READY_PATH


def _require_dataset():
    if not Path(MODEL_READY_PATH).exists():
        pytest.skip("df_model_ready.parquet not present — run build-dataset first")


def test_model_ready_dataset_exists():
    if not Path(MODEL_READY_PATH).exists():
        pytest.skip("df_model_ready.parquet not present — run build-dataset first")


def test_model_ready_dataset_not_empty():
    _require_dataset()
    df = pd.read_parquet(MODEL_READY_PATH)
    assert not df.empty, "Model-ready dataset is empty"


def test_model_ready_dataset_has_required_columns():
    _require_dataset()
    df = pd.read_parquet(MODEL_READY_PATH)
    required = {"PLAYER_NAME", "GAME_DATE", "MIN", "FantasyPoints"}
    missing = required - set(df.columns)
    assert not missing, f"Missing required columns: {missing}"
