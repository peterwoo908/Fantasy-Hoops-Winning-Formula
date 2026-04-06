from dataclasses import dataclass

import pandas as pd
import xgboost as xgb

from src.config import FEATURE_COLS, TARGET_FP, TARGET_MIN, TEST_SEASON


@dataclass
class TrainTestSplit:
    X_train: pd.DataFrame
    y_train_min: pd.Series
    y_train_fp: pd.Series
    X_test: pd.DataFrame
    y_test_min: pd.Series
    y_test_fp: pd.Series
    mask_test: pd.Series
    split_idx: int


def split_train_test_by_season(
    df: pd.DataFrame,
    feature_cols: list[str] = FEATURE_COLS,
    target_min: str = TARGET_MIN,
    target_fp: str = TARGET_FP,
    test_season: str = TEST_SEASON,
) -> TrainTestSplit:
    df = df.sort_values("GAME_DATE").copy()
    mask_test = df["Season_Year"] == test_season
    mask_train = ~mask_test

    X_train = df.loc[mask_train, feature_cols]
    y_train_min = df.loc[mask_train, target_min]
    y_train_fp = df.loc[mask_train, target_fp]
    X_test = df.loc[mask_test, feature_cols]
    y_test_min = df.loc[mask_test, target_min]
    y_test_fp = df.loc[mask_test, target_fp]
    split_idx = int(len(X_train) * 0.9)

    return TrainTestSplit(X_train, y_train_min, y_train_fp, X_test, y_test_min, y_test_fp, mask_test, split_idx)


def train_minutes_model(X_train: pd.DataFrame, y_train_min: pd.Series, split_idx: int):
    model_min = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=5,
        early_stopping_rounds=50,
        n_jobs=-1,
        random_state=42,
    )
    X_tr_sub, X_val_sub = X_train.iloc[:split_idx], X_train.iloc[split_idx:]
    y_tr_sub, y_val_sub = y_train_min.iloc[:split_idx], y_train_min.iloc[split_idx:]
    model_min.fit(X_tr_sub, y_tr_sub, eval_set=[(X_val_sub, y_val_sub)], verbose=100)
    return model_min


def build_stage2_matrices(model_min, X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    X_train_s2 = X_train.copy()
    X_train_s2["Predicted_MIN"] = model_min.predict(X_train)
    X_test_s2 = X_test.copy()
    X_test_s2["Predicted_MIN"] = model_min.predict(X_test)
    features_stage2 = list(X_train_s2.columns)
    return X_train_s2, X_test_s2, features_stage2


def train_fantasy_points_model(X_train_s2: pd.DataFrame, y_train_fp: pd.Series, split_idx: int):
    model_fp = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=6,
        early_stopping_rounds=50,
        n_jobs=-1,
        random_state=42,
    )
    X_tr_sub2, X_val_sub2 = X_train_s2.iloc[:split_idx], X_train_s2.iloc[split_idx:]
    y_tr_fp_sub, y_val_fp_sub = y_train_fp.iloc[:split_idx], y_train_fp.iloc[split_idx:]
    model_fp.fit(X_tr_sub2, y_tr_fp_sub, eval_set=[(X_val_sub2, y_val_fp_sub)], verbose=100)
    return model_fp
