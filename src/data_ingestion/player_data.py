import time
from pathlib import Path

import numpy as np
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog

from src.config import CURRENT_SEASON, PLAYER_DATA_PATH, SCORING_RULES, TARGET_SEASONS
from src.utils import normalize_name, require_columns


def process_league_log(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, ["GAME_DATE", "MATCHUP"], "raw player league log")
    df = df.copy()
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df["FantasyPoints"] = 0.0

    for cat, val in SCORING_RULES.items():
        if cat in df.columns:
            df["FantasyPoints"] += df[cat] * val

    def parse_matchup(value: str):
        try:
            parts = value.split()
            return parts[0], parts[2]
        except Exception:
            return None, None

    df[["Team", "Opp"]] = df["MATCHUP"].apply(lambda x: pd.Series(parse_matchup(x)))
    df["Home"] = df["MATCHUP"].apply(lambda x: 1 if "vs." in x else (0 if "@" in x else np.nan))

    if "Season_Year" not in df.columns:
        df["Season_Year"] = None

    desired_cols = [
        "PLAYER_NAME", "FantasyPoints", "GAME_DATE", "Home", "Team", "Opp", "MIN", "PTS", "AST", "REB", "FGM",
        "FGA", "FG_PCT", "FG3M", "FTM", "FTA", "STL", "BLK", "TOV", "PF", "WL", "FG3A", "FG3_PCT", "FT_PCT",
        "OREB", "DREB", "PLUS_MINUS", "SEASON_ID", "PLAYER_ID", "TEAM_ID", "GAME_ID", "Season_Year",
    ]
    return df[[c for c in desired_cols if c in df.columns]].copy()


def fetch_season_whole(season_str: str) -> pd.DataFrame:
    print(f"Fetching full player log for season: {season_str}...")
    try:
        log = leaguegamelog.LeagueGameLog(
            season=season_str,
            player_or_team_abbreviation="P",
            season_type_all_star="Regular Season",
        )
        df = log.get_data_frames()[0]
        df["Season_Year"] = season_str
        return process_league_log(df)
    except Exception as exc:
        print(f"Error fetching player data for {season_str}: {exc}")
        return pd.DataFrame()


def build_historical_database(data_path: Path = PLAYER_DATA_PATH) -> pd.DataFrame:
    all_dfs = []
    for season in TARGET_SEASONS:
        df = fetch_season_whole(season)
        if not df.empty:
            all_dfs.append(df)
            print(f"Loaded {len(df)} player rows for {season}")
        time.sleep(1.0)

    if not all_dfs:
        raise RuntimeError("No player data fetched.")

    master_df = pd.concat(all_dfs, ignore_index=True)
    master_df["PLAYER_NAME"] = master_df["PLAYER_NAME"].apply(normalize_name)
    master_df.to_parquet(data_path, index=False)
    print(f"Saved {len(master_df)} player rows to {data_path}")
    return master_df


def update_current_season(data_path: Path = PLAYER_DATA_PATH, current_season: str = CURRENT_SEASON) -> pd.DataFrame:
    if not data_path.exists():
        print("No player database found. Building historical database first...")
        return build_historical_database(data_path=data_path)

    master_df = pd.read_parquet(data_path)
    master_df["GAME_DATE"] = pd.to_datetime(master_df["GAME_DATE"])
    max_date = master_df["GAME_DATE"].max()
    start_fetch_date = max_date + pd.Timedelta(days=1)
    date_str = start_fetch_date.strftime("%m/%d/%Y")

    print(f"Player database current through: {max_date.date()}")
    print(f"Fetching player updates since {date_str}...")

    try:
        log = leaguegamelog.LeagueGameLog(
            season=current_season,
            player_or_team_abbreviation="P",
            season_type_all_star="Regular Season",
            date_from_nullable=date_str,
            timeout=60,
        )
        new_df = log.get_data_frames()[0]
    except Exception as exc:
        print(f"Player update failed: {exc}")
        return master_df

    if new_df.empty:
        print("No new player games found.")
        return master_df

    new_df["Season_Year"] = current_season
    processed_new = process_league_log(new_df)
    combined = pd.concat([master_df, processed_new], ignore_index=True)
    combined = combined.drop_duplicates(subset=["PLAYER_ID", "GAME_DATE"], keep="last")
    combined["PLAYER_NAME"] = combined["PLAYER_NAME"].apply(normalize_name)
    combined = combined.sort_values("GAME_DATE")
    combined.to_parquet(data_path, index=False)

    print(f"Updated player database. Total rows: {len(combined)}")
    return combined
