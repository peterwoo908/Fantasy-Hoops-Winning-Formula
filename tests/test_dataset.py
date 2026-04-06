from pathlib import Path
import pandas as pd

from src.config import MODEL_READY_PATH

def test_model_ready_dataset_exists():
    assert Path(MODEL_READY_PATH).exists(), f"Missing dataset: {MODEL_READY_PATH}"

def test_model_ready_dataset_not_empty():
    df = pd.read_parquet(MODEL_READY_PATH)
    assert not df.empty, "Model-ready dataset is empty"

def test_model_ready_dataset_has_required_columns():
    df = pd.read_parquet(MODEL_READY_PATH)
    required = {"PLAYER_NAME", "GAME_DATE", "MIN", "FantasyPoints"}
    missing = required - set(df.columns)
    assert not missing, f"Missing required columns: {missing}"