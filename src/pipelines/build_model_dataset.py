import pandas as pd

from src.config import MODEL_READY_PATH, PLAYER_DATA_PATH, TEAM_DATA_PATH
from src.data_ingestion.player_data import update_current_season
from src.data_ingestion.team_data import update_team_database
from src.features.merge import merge_data_for_modeling, prepare_model_ready_dataset
from src.features.player_features import engineer_player_features
from src.utils import ensure_directories


def build_model_dataset() -> pd.DataFrame:
    ensure_directories()
    player_data = update_current_season(data_path=PLAYER_DATA_PATH)
    team_data = update_team_database(data_path=TEAM_DATA_PATH)

    player_features = engineer_player_features(player_data)
    merged = merge_data_for_modeling(player_features, team_data)
    df_model_ready = prepare_model_ready_dataset(merged)
    df_model_ready.to_parquet(MODEL_READY_PATH, index=False)
    print(f"Saved model-ready dataset to {MODEL_READY_PATH}")
    return df_model_ready
