import os

import pandas as pd
from espn_api.basketball import League

from src.config import ESPN_POOL_PATH
from src.utils import normalize_name, get_env_or_raise

def normalize_injury_status(value) -> str:
    if value is None:
        return "ACTIVE"
    if isinstance(value, list):
        return "ACTIVE" if len(value) == 0 else ", ".join(str(v) for v in value)
    value = str(value).strip()
    return "ACTIVE" if value == "" else value

def fetch_espn_player_pool(free_agent_size: int = 1500) -> pd.DataFrame:
    league_id = int(get_env_or_raise("ESPN_LEAGUE_ID"))
    year = int(os.getenv("ESPN_YEAR", "2026"))
    swid = get_env_or_raise("ESPN_SWID")
    espn_s2 = get_env_or_raise("ESPN_S2")

    print("Fetching ESPN league data...")
    league = League(league_id=league_id, year=year, swid=swid, espn_s2=espn_s2)

    espn_data = []
    for team in league.teams:
        for player in team.roster:
            espn_data.append(
                {
                    "ESPN_Name": normalize_name(player.name),
                    "Fantasy_Team": team.team_name,
                    "Free_Agent": False,
                    "Injury_Status": player.injuryStatus,
                }
            )

    for player in league.free_agents(size=free_agent_size):
        espn_data.append(
            {
                "ESPN_Name": normalize_name(player.name),
                "Fantasy_Team": "Free Agent",
                "Free_Agent": True,
                "Injury_Status": player.injuryStatus,
            }
        )

    df = pd.DataFrame(espn_data).drop_duplicates(subset=["ESPN_Name"], keep="first")

    if "Injury_Status" in df.columns:
        df["Injury_Status"] = df["Injury_Status"].apply(normalize_injury_status)

    print(f"Loaded ESPN player pool with {len(df)} players")
    return df


def save_espn_player_pool(df: pd.DataFrame, path=ESPN_POOL_PATH) -> None:
    df = df.copy()
    if "Injury_Status" in df.columns:
        df["Injury_Status"] = df["Injury_Status"].apply(normalize_injury_status)
    df.to_parquet(path, index=False)

def load_or_fetch_espn_player_pool(path=ESPN_POOL_PATH) -> pd.DataFrame:
    if path.exists():
        return pd.read_parquet(path)
    df = fetch_espn_player_pool()
    save_espn_player_pool(df, path=path)
    return df
