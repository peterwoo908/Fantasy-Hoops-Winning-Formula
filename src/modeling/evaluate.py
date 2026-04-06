import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error


def evaluate_predictions(y_true, y_pred) -> float:
    return float(mean_absolute_error(y_true, y_pred))


def build_prediction_results(df: pd.DataFrame, mask_test, y_test_min, pred_min, y_test_fp, pred_fp) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Player": df.loc[mask_test, "PLAYER_NAME"],
            "Date": df.loc[mask_test, "GAME_DATE"],
            "Actual_MIN": y_test_min,
            "Pred_MIN": np.round(pred_min, 1),
            "Actual_FP": y_test_fp,
            "Pred_FP": np.round(pred_fp, 1),
            "Error": np.round(pred_fp - y_test_fp, 1),
        }
    )


def get_feature_importance(model_fp, features_stage2: list[str], top_n: int = 10) -> pd.DataFrame:
    return (
        pd.DataFrame({"Feature": features_stage2, "Gain": model_fp.feature_importances_})
        .sort_values("Gain", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
