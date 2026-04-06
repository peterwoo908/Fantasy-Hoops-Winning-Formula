import joblib
import pandas as pd
import xgboost as xgb

from src.config import FEATURE_COLS, FP_MODEL_PATH, MIN_MODEL_PATH, TARGET_FP, TARGET_MIN


def train_final_models(df_full: pd.DataFrame):
    print(f"Training final production models on {len(df_full)} games...")

    final_model_min = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=5,
        n_jobs=-1,
        random_state=42,
    )
    final_model_min.fit(df_full[FEATURE_COLS], df_full[TARGET_MIN])

    df_stage2 = df_full.copy()
    df_stage2["Predicted_MIN"] = final_model_min.predict(df_stage2[FEATURE_COLS])
    features_final = FEATURE_COLS + ["Predicted_MIN"]

    final_model_fp = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=5,
        n_jobs=-1,
        random_state=42,
    )
    final_model_fp.fit(df_stage2[features_final], df_stage2[TARGET_FP])

    return final_model_min, final_model_fp, features_final


def save_models(model_min, model_fp, min_model_path=MIN_MODEL_PATH, fp_model_path=FP_MODEL_PATH) -> None:
    joblib.dump(model_min, min_model_path)
    joblib.dump(model_fp, fp_model_path)
    print(f"Saved minutes model to {min_model_path}")
    print(f"Saved fantasy points model to {fp_model_path}")
