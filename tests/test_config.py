from src.config import FEATURE_COLS, TARGET_FP, TARGET_MIN


def test_basic_config_values_exist():
    assert TARGET_MIN == "MIN"
    assert TARGET_FP == "FantasyPoints"
    assert len(FEATURE_COLS) > 0
