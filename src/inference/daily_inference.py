import pandas as pd

from src.config import DEFAULT_TEAM_DEF_RTG, DEFAULT_TEAM_PACE, FEATURE_COLS
from src.data_ingestion.schedule_data import get_schedule_matchups
from src.utils import normalize_name


def run_daily_inference(
    date_str: str,
    df_all_cols: pd.DataFrame,
    df_team_rolling: pd.DataFrame,
    model_min,
    model_fp,
    feature_cols: list[str] = FEATURE_COLS,
    df_espn_pool: pd.DataFrame | None = None,
) -> pd.DataFrame:
    id_map = df_all_cols[["TEAM_ID", "Team"]].drop_duplicates().set_index("TEAM_ID")["Team"].to_dict()

    schedule = get_schedule_matchups(date_str)
    if schedule.empty:
        print("No games found for target date.")
        return pd.DataFrame()
    schedule = schedule.drop_duplicates(subset=["TEAM_ID"])

    latest_players = df_all_cols.loc[df_all_cols.groupby("PLAYER_ID")["GAME_DATE"].idxmax()].copy()
    latest_game_in_db = df_all_cols["GAME_DATE"].max()
    cutoff_date = latest_game_in_db - pd.Timedelta(days=30)
    latest_players = latest_players[latest_players["GAME_DATE"] >= cutoff_date]
    latest_players["PLAYER_NAME"] = latest_players["PLAYER_NAME"].apply(normalize_name)

    if df_espn_pool is not None and not df_espn_pool.empty:
        print(f"Merging with ESPN pool ({len(df_espn_pool)} players)...")
        df_espn_pool = df_espn_pool.copy()
        df_espn_pool["ESPN_Name"] = df_espn_pool["ESPN_Name"].apply(normalize_name)
        latest_players = pd.merge(
            latest_players,
            df_espn_pool[["ESPN_Name", "Fantasy_Team", "Free_Agent", "Injury_Status"]],
            left_on="PLAYER_NAME",
            right_on="ESPN_Name",
            how="inner",
        )
    else:
        latest_players["Fantasy_Team"] = "Unknown"
        latest_players["Free_Agent"] = False
        latest_players["Injury_Status"] = None

    cols_to_keep = [
        "PLAYER_ID", "PLAYER_NAME", "TEAM_ID", "GAME_DATE", "MIN", "FantasyPoints",
        "Fantasy_Team", "Free_Agent", "Injury_Status",
    ]
    context_features = ["Schedule_Rest", "Long_Absence_Flag", "Team_Pace", "Team_DefRtg", "Opp_Pace", "Opp_DefRtg"]
    history_features = [c for c in feature_cols if c not in context_features]
    final_cols_needed = cols_to_keep + history_features
    available_cols = [c for c in final_cols_needed if c in latest_players.columns]

    player_pool_df = latest_players[available_cols].copy()
    player_pool_df = player_pool_df.drop(columns=["Lag1_MIN", "Lag1_FP"], errors="ignore")
    player_pool_df.rename(columns={"MIN": "Lag1_MIN", "FantasyPoints": "Lag1_FP", "GAME_DATE": "Last_Game_Date"}, inplace=True)

    latest_teams = df_team_rolling.sort_values("GAME_ID").groupby("TEAM_ID").tail(1)
    team_lookup = latest_teams[["TEAM_ID", "Rolling_Pace", "Rolling_DRtg"]]

    inference = pd.merge(schedule, player_pool_df, on="TEAM_ID")
    if inference.empty:
        print("No active players matched the schedule.")
        return pd.DataFrame()

    inference["Target_Date"] = pd.to_datetime(date_str)
    inference["Days_Since_Last_Game"] = (inference["Target_Date"] - inference["Last_Game_Date"]).dt.days
    inference["Schedule_Rest"] = inference["Days_Since_Last_Game"].clip(upper=4).fillna(3)
    inference["Long_Absence_Flag"] = (inference["Days_Since_Last_Game"] > 14).astype(int)

    inference = pd.merge(inference, team_lookup, on="TEAM_ID", how="left")
    inference.rename(columns={"Rolling_Pace": "Team_Pace", "Rolling_DRtg": "Team_DefRtg"}, inplace=True)
    inference = pd.merge(inference, team_lookup.rename(columns={"TEAM_ID": "OPP_TEAM_ID"}), on="OPP_TEAM_ID", how="left")
    inference.rename(columns={"Rolling_Pace": "Opp_Pace", "Rolling_DRtg": "Opp_DefRtg"}, inplace=True)

    inference.fillna(
        {
            "Team_Pace": DEFAULT_TEAM_PACE,
            "Team_DefRtg": DEFAULT_TEAM_DEF_RTG,
            "Opp_Pace": DEFAULT_TEAM_PACE,
            "Opp_DefRtg": DEFAULT_TEAM_DEF_RTG,
        },
        inplace=True,
    )

    inference["Pred_MIN"] = model_min.predict(inference[feature_cols])
    inference["Predicted_MIN"] = inference["Pred_MIN"]
    features_s2 = feature_cols + ["Predicted_MIN"]
    inference["Pred_FP"] = model_fp.predict(inference[features_s2])

    if "Injury_Status" in inference.columns:
        injury_status = inference["Injury_Status"].fillna("").astype(str).str.upper()
        mask_out = injury_status.str.contains("OUT|IR", regex=True)
        inference.loc[mask_out, ["Pred_FP", "Pred_MIN"]] = 0.0

    inference["Team"] = inference["TEAM_ID"].map(id_map)
    inference["Opp"] = inference["OPP_TEAM_ID"].map(id_map)

    final_cols = [
        "PLAYER_NAME", "Team", "Opp", "Fantasy_Team", "Free_Agent", "Injury_Status",
        "Pred_MIN", "Pred_FP", "L3_FP_per_Min", "Opp_DefRtg", "Schedule_Rest", "Long_Absence_Flag",
    ]
    result = inference[[c for c in final_cols if c in inference.columns]].copy()
    round_cols = [c for c in ["Pred_MIN", "Pred_FP", "L3_FP_per_Min", "Opp_DefRtg"] if c in result.columns]
    result[round_cols] = result[round_cols].round(2)
    result = result.drop_duplicates(subset=["PLAYER_NAME"])
    result["Date"] = date_str
    result.insert(0, "Date", result.pop("Date"))
    return result.sort_values("Pred_FP", ascending=False)
