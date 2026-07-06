from pathlib import Path

import pytest

from src.config import FP_MODEL_PATH, MIN_MODEL_PATH


def test_minutes_model_exists():
    if not Path(MIN_MODEL_PATH).exists():
        pytest.skip("nba_min_model.pkl not present — run train-models first")


def test_fantasy_model_exists():
    if not Path(FP_MODEL_PATH).exists():
        pytest.skip("nba_fp_model.pkl not present — run train-models first")
