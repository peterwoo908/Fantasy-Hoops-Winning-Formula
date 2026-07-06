"""
Integration smoke test — makes live nba_api network calls.

Excluded from the default pytest run (see pytest.ini).
Run explicitly with:  pytest -m integration
"""
import pytest

from src.config import FP_MODEL_PATH, MIN_MODEL_PATH, MODEL_READY_PATH

pytestmark = pytest.mark.integration

# The last in-season date present in the seeded parquets
_TEST_DATE = "2026-04-09"


def test_full_inference_pipeline_for_known_date():
    """
    Runs daily inference for a known in-season date and asserts non-empty output.

    Prerequisites (all satisfied when run after the pipeline steps):
    - data/processed/df_model_ready.parquet exists
    - models/nba_min_model.pkl and nba_fp_model.pkl exist
    - data/external/espn_player_pool.parquet exists (avoids ESPN API call)
    - nba_api is reachable (one schedule lookup for the target date)
    """
    missing = [p for p in [MODEL_READY_PATH, MIN_MODEL_PATH, FP_MODEL_PATH] if not p.exists()]
    if missing:
        pytest.skip(f"Required artifacts missing: {[str(p) for p in missing]}")

    from src.pipelines.run_daily_pipeline import run_daily_pipeline

    result = run_daily_pipeline(date_str=_TEST_DATE)

    assert result is not None, "run_daily_pipeline returned None"
    assert not result.empty, f"Inference produced zero rows for {_TEST_DATE}"
    assert "Pred_FP" in result.columns, "Missing Pred_FP column in inference output"
    assert "PLAYER_NAME" in result.columns, "Missing PLAYER_NAME column in inference output"
    assert (result["Pred_FP"] > 0).any(), "All Pred_FP values are zero or negative"

    print(f"\nSmoke test passed: {len(result)} players projected for {_TEST_DATE}")
    print(result[["PLAYER_NAME", "Team", "Pred_MIN", "Pred_FP"]].head(10).to_string(index=False))
