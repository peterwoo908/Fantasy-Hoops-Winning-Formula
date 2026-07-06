from datetime import timedelta
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguegamelog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config import CURRENT_SEASON, TARGET_SEASONS, TEAM_DATA_PATH
from src.features.team_features import apply_bayesian_smoothing, calculate_advanced_stats

_NBA_RETRY = dict(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=3, max=20),
    reraise=True,
)


@retry(**_NBA_RETRY)
def _fetch_team_log(season: str) -> pd.DataFrame:
    log = leaguegamelog.LeagueGameLog(
        season=season,
        player_or_team_abbreviation="T",
        season_type_all_star="Regular Season",
        timeout=60,
    )
    return log.get_data_frames()[0]


def fetch_team_history(seasons: list[str] | None = None) -> pd.DataFrame:
    seasons = seasons or TARGET_SEASONS
    all_teams = []
    print("Fetching team logs...")

    for season in seasons:
        df = _fetch_team_log(season)
        df["Season_Year"] = season
        all_teams.append(df)

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


@retry(**_NBA_RETRY)
def _fetch_team_delta(season: str, date_str: str) -> pd.DataFrame:
    log = leaguegamelog.LeagueGameLog(
        season=season,
        player_or_team_abbreviation="T",
        season_type_all_star="Regular Season",
        date_from_nullable=date_str,
        timeout=60,
    )
    return log.get_data_frames()[0]


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

    new_df = _fetch_team_delta(current_season, date_str)

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
