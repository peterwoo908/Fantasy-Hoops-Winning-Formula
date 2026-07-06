import pandas as pd
from nba_api.stats.endpoints import scoreboardv3
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

_NBA_RETRY = dict(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=3, max=20),
    reraise=True,
)


@retry(**_NBA_RETRY)
def get_schedule_matchups(date_str: str) -> pd.DataFrame:
    print(f"Fetching NBA schedule for {date_str}...")
    board = scoreboardv3.ScoreboardV3(game_date=date_str, timeout=30)
    line_score = board.line_score.get_data_frame()
    if line_score.empty:
        return pd.DataFrame()

    # line_score has two rows per game (one per team); pair them to get home/away matchups
    matchups = []
    for game_id, group in line_score.groupby("gameId"):
        team_ids = group["teamId"].tolist()
        if len(team_ids) == 2:
            matchups.append({"TEAM_ID": team_ids[0], "OPP_TEAM_ID": team_ids[1]})
            matchups.append({"TEAM_ID": team_ids[1], "OPP_TEAM_ID": team_ids[0]})
    return pd.DataFrame(matchups)
