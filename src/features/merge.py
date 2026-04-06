import pandas as pd

from src.config import FEATURE_COLS, META_COLS, TARGET_FP, TARGET_MIN
from src.utils import require_columns


def merge_data_for_modeling(df_player_features: pd.DataFrame, df_team_rolling: pd.DataFrame) -> pd.DataFrame:
    print("Merging player and team data...")
    df_main = df_player_features.copy()
    require_columns(df_main, ["GAME_ID", "TEAM_ID"], "player features")
    require_columns(df_team_rolling, ["GAME_ID", "TEAM_ID", "Rolling_Pace", "Rolling_DRtg"], "team rolling data")

    df_team_lookup = df_team_rolling[["GAME_ID", "TEAM_ID", "Rolling_Pace", "Rolling_DRtg"]].copy()

    df_main = pd.merge(df_main, df_team_lookup, on=["GAME_ID", "TEAM_ID"], how="left")
    df_main.rename(columns={"Rolling_Pace": "Team_Pace", "Rolling_DRtg": "Team_DefRtg"}, inplace=True)

    game_teams = df_team_rolling[["GAME_ID", "TEAM_ID"]].drop_duplicates()
    df_main = pd.merge(df_main, game_teams, on="GAME_ID", suffixes=("", "_OppLookup"))
    df_main = df_main[df_main["TEAM_ID"] != df_main["TEAM_ID_OppLookup"]].copy()

    df_main = pd.merge(
        df_main,
        df_team_lookup,
        left_on=["GAME_ID", "TEAM_ID_OppLookup"],
        right_on=["GAME_ID", "TEAM_ID"],
        how="left",
        suffixes=("", "_OppJoin"),
    )
    df_main.rename(columns={"Rolling_Pace": "Opp_Pace", "Rolling_DRtg": "Opp_DefRtg"}, inplace=True)
    df_main.drop(columns=["TEAM_ID_OppJoin", "TEAM_ID_OppLookup"], inplace=True, errors="ignore")

    print(f"Merge complete. Final shape: {df_main.shape}")
    return df_main


def prepare_model_ready_dataset(df_all_cols: pd.DataFrame, drop_na: bool = True) -> pd.DataFrame:
    all_needed_cols = META_COLS + [TARGET_MIN, TARGET_FP] + FEATURE_COLS
    require_columns(df_all_cols, all_needed_cols, "merged modeling dataset")
    df_model_ready = df_all_cols[all_needed_cols].copy()

    print(f"Shape before dropping NAs: {df_model_ready.shape}")
    if drop_na:
        df_model_ready.dropna(inplace=True)
    print(f"Shape after dropping NAs:  {df_model_ready.shape}")
    return df_model_ready
