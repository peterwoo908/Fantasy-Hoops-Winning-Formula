from datetime import timedelta
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

from src.config import CURRENT_SEASON, TARGET_SEASONS, TEAM_DATA_PATH
from src.features.team_features import apply_bayesian_smoothing, calculate_advanced_stats


def fetch_team_history(seasons: list[str] | None = None) -> pd.DataFrame:
    seasons = seasons or TARGET_SEASONS
    all_teams = []
    print("Fetching team logs...")

    for season in seasons:
        try:
            log = leaguegamelog.LeagueGameLog(
                season=season,
                player_or_team_abbreviation="T",
                season_type_all_star="Regular Season",
            )
            df = log.get_data_frames()[0]
            df["Season_Year"] = season
            all_teams.append(df)
        except Exception as exc:
            print(f"Error fetching team data for {season}: {exc}")

    if not all_teams:
        raise RuntimeError("No team data fetched.")

    master_team = pd.concat(all_teams, ignore_index=True)
    master_team["GAME_DATE"] = pd.to_datetime(master_team["GAME_DATE"])
    return master_team.sort_values("GAME_DATE")


def initialize_team_database(data_path: Path = TEAM_DATA_PATH) -> pd.DataFrame:
    team_data = fetch_team_history()
    df_calc = calculate_advanced_stats(team_data)
    df_final = apply_bayesian_smoothing(df_calc)
    df_final.to_parquet(data_path, index=False)
    print(f"Saved team database to {data_path}")
    return df_final


def update_team_database(data_path: Path = TEAM_DATA_PATH, current_season: str = CURRENT_SEASON) -> pd.DataFrame:
    if not data_path.exists():
        print("No existing team database found. Initializing first...")
        return initialize_team_database(data_path=data_path)

    df_master = pd.read_parquet(data_path)
    df_master["GAME_DATE"] = pd.to_datetime(df_master["GAME_DATE"])
    last_date = df_master["GAME_DATE"].max()
    start_fetch_date = last_date + timedelta(days=1)
    date_str = start_fetch_date.strftime("%m/%d/%Y")

    print(f"Team database current through: {last_date.date()}")
    print(f"Checking for new team games since {date_str}...")

    try:
        log = leaguegamelog.LeagueGameLog(
            season=current_season,
            player_or_team_abbreviation="T",
            season_type_all_star="Regular Season",
            date_from_nullable=date_str,
            timeout=200,
        )
        new_df = log.get_data_frames()[0]
    except Exception as exc:
        print(f"Team update failed: {exc}")
        return df_master

    if new_df.empty:
        print("No new team games found.")
        return df_master

    new_df["Season_Year"] = current_season
    new_df["GAME_DATE"] = pd.to_datetime(new_df["GAME_DATE"])

    combined = pd.concat([df_master, new_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["TEAM_ID", "GAME_ID"], keep="last")
    combined = combined.sort_values("GAME_DATE")

    print("Recalculating team advanced stats and smoothing...")
    df_calc = calculate_advanced_stats(combined)
    df_final = apply_bayesian_smoothing(df_calc)
    df_final.to_parquet(data_path, index=False)
    print(f"Updated team database. Total rows: {len(df_final)}")
    return df_final
