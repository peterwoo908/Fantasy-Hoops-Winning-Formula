import pandas as pd

from src.config import EVALUATIONS_DIR, MODEL_READY_PATH
from src.modeling.evaluate import build_prediction_results, evaluate_predictions, get_feature_importance
from src.modeling.save_models import save_models, train_final_models
from src.modeling.train import build_stage2_matrices, split_train_test_by_season, train_fantasy_points_model, train_minutes_model
from src.utils import ensure_directories


def train_models() -> dict:
    ensure_directories()
    if not MODEL_READY_PATH.exists():
        raise FileNotFoundError(f"Model-ready dataset not found at {MODEL_READY_PATH}. Run build-dataset first.")

    df = pd.read_parquet(MODEL_READY_PATH).sort_values("GAME_DATE")
    split = split_train_test_by_season(df)

    print(f"Training on {len(split.X_train)} historical games")
    print(f"Testing on {len(split.X_test)} current-season games")

    model_min = train_minutes_model(split.X_train, split.y_train_min, split.split_idx)
    pred_min = model_min.predict(split.X_test)
    mae_min = evaluate_predictions(split.y_test_min, pred_min)
    print(f"Minutes MAE: {mae_min:.2f}")

    X_train_s2, X_test_s2, features_stage2 = build_stage2_matrices(model_min, split.X_train, split.X_test)
    model_fp = train_fantasy_points_model(X_train_s2, split.y_train_fp, split.split_idx)
    pred_fp = model_fp.predict(X_test_s2)
    mae_fp = evaluate_predictions(split.y_test_fp, pred_fp)
    print(f"Fantasy Points MAE: {mae_fp:.2f}")

    results = build_prediction_results(df, split.mask_test, split.y_test_min, pred_min, split.y_test_fp, pred_fp)
    importance = get_feature_importance(model_fp, features_stage2)
    results.to_csv(EVALUATIONS_DIR / "holdout_predictions.csv", index=False)
    importance.to_csv(EVALUATIONS_DIR / "feature_importance.csv", index=False)

    final_model_min, final_model_fp, final_features = train_final_models(df)
    save_models(final_model_min, final_model_fp)

    return {
        "minutes_mae": mae_min,
        "fantasy_points_mae": mae_fp,
        "results_path": str(EVALUATIONS_DIR / "holdout_predictions.csv"),
        "importance_path": str(EVALUATIONS_DIR / "feature_importance.csv"),
        "stage2_features": final_features,
    }
