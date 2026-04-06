from pathlib import Path

from src.config import MIN_MODEL_PATH, FP_MODEL_PATH

def test_minutes_model_exists():
    assert Path(MIN_MODEL_PATH).exists(), f"Missing minutes model: {MIN_MODEL_PATH}"

def test_fantasy_model_exists():
    assert Path(FP_MODEL_PATH).exists(), f"Missing fantasy model: {FP_MODEL_PATH}"