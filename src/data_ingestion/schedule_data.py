import pandas as pd
from nba_api.stats.endpoints import scoreboardv2


def get_schedule_matchups(date_str: str) -> pd.DataFrame:
    print(f"Fetching NBA schedule for {date_str}...")
    try:
        board = scoreboardv2.ScoreboardV2(game_date=date_str)
        games = board.game_header.get_data_frame()
        matchups = []
        for _, row in games.iterrows():
            matchups.append({"TEAM_ID": row["HOME_TEAM_ID"], "OPP_TEAM_ID": row["VISITOR_TEAM_ID"]})
            matchups.append({"TEAM_ID": row["VISITOR_TEAM_ID"], "OPP_TEAM_ID": row["HOME_TEAM_ID"]})
        return pd.DataFrame(matchups)
    except Exception as exc:
        print(f"Error fetching NBA schedule: {exc}")
        return pd.DataFrame()
