import pandas as pd

from src.config import MODEL_READY_PATH, PLAYER_DATA_PATH, TEAM_DATA_PATH
from src.data_ingestion.player_data import update_current_season
from src.data_ingestion.team_data import update_team_database
from src.features.merge import merge_data_for_modeling, prepare_model_ready_dataset
from src.features.player_features import engineer_player_features
from src.utils import ensure_directories


def build_model_dataset(skip_fetch: bool = False) -> pd.DataFrame:
    ensure_directories()

    if skip_fetch:
        # Used in CI/GitHub Actions where nba_api is blocked.
        # Reads the committed raw parquets directly — no network calls.
        if not PLAYER_DATA_PATH.exists() or not TEAM_DATA_PATH.exists():
            raise FileNotFoundError(
                "Raw parquets not found. Cannot use --skip-fetch without committed seed data."
            )
        player_data = pd.read_parquet(PLAYER_DATA_PATH)
        player_data["GAME_DATE"] = pd.to_datetime(player_data["GAME_DATE"])
        team_data = pd.read_parquet(TEAM_DATA_PATH)
        team_data["GAME_DATE"] = pd.to_datetime(team_data["GAME_DATE"])
        print(f"skip-fetch: loaded {len(player_data)} player rows and {len(team_data)} team rows from committed parquets.")
    else:
        player_data = update_current_season(data_path=PLAYER_DATA_PATH)
        team_data = update_team_database(data_path=TEAM_DATA_PATH)

    player_features = engineer_player_features(player_data)
    merged = merge_data_for_modeling(player_features, team_data)
    df_model_ready = prepare_model_ready_dataset(merged)
    df_model_ready.to_parquet(MODEL_READY_PATH, index=False)
    print(f"Saved model-ready dataset to {MODEL_READY_PATH}")
    return df_model_ready
