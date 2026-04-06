import numpy as np
import pandas as pd

from src.utils import require_columns


def engineer_player_features(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = [
        "PLAYER_ID", "GAME_DATE", "FantasyPoints", "MIN", "FGA", "FGM", "FG3M", "FG3A", "OREB",
        "TOV", "FTA", "PF", "PLUS_MINUS", "Season_Year", "TEAM_ID",
    ]
    require_columns(df, required_cols, "player data")

    df = df.sort_values(["PLAYER_ID", "GAME_DATE"]).copy()
    df["MIN"] = np.where(df["MIN"] == 0, 0.5, df["MIN"])
    df["FP_per_Min"] = df["FantasyPoints"] / df["MIN"]
    df["Usage_Proxy"] = (df["FGA"] + df["TOV"] + 0.44 * df["FTA"]) / df["MIN"]
    df["OREB_per_Min"] = df["OREB"] / df["MIN"]

    cols_to_roll = ["MIN", "FantasyPoints", "FGA", "FGM", "FG3M", "FG3A", "OREB", "TOV", "FTA", "PF", "PLUS_MINUS"]
    spans = [3, 10]
    grouped = df.groupby("PLAYER_ID")

    for span in spans:
        prefix = f"L{span}"
        rolled = grouped[cols_to_roll].transform(lambda x: x.ewm(span=span).mean().shift(1))
        rolled.columns = [f"{prefix}_{c}" for c in cols_to_roll]
        df = pd.concat([df, rolled], axis=1)

        df[f"{prefix}_FP_per_Min"] = df[f"{prefix}_FantasyPoints"] / df[f"{prefix}_MIN"]
        df[f"{prefix}_Usage"] = (df[f"{prefix}_FGA"] + df[f"{prefix}_TOV"] + 0.44 * df[f"{prefix}_FTA"]) / df[f"{prefix}_MIN"]
        df[f"{prefix}_OREB_Rate"] = df[f"{prefix}_OREB"] / df[f"{prefix}_MIN"]
        df[f"{prefix}_3P_Pct"] = df[f"{prefix}_FG3M"] / df[f"{prefix}_FG3A"].replace(0, np.nan)
        df[f"{prefix}_3P_Pct"] = df[f"{prefix}_3P_Pct"].fillna(0.0)

    season_rolled = grouped[cols_to_roll].transform(lambda x: x.expanding().mean().shift(1))
    season_rolled.columns = [f"SZ_{c}" for c in cols_to_roll]
    df = pd.concat([df, season_rolled], axis=1)

    df["SZ_FP_per_Min"] = df["SZ_FantasyPoints"] / df["SZ_MIN"]
    df["SZ_Usage"] = (df["SZ_FGA"] + df["SZ_TOV"] + 0.44 * df["SZ_FTA"]) / df["SZ_MIN"]

    df["Lag1_MIN"] = grouped["MIN"].shift(1)
    df["Lag1_FP"] = grouped["FantasyPoints"].shift(1)
    df = df.sort_values(["PLAYER_ID", "GAME_DATE"])
    df["Last_Game_Date"] = grouped["GAME_DATE"].shift(1)
    df["Days_Since_Last_Game"] = (df["GAME_DATE"] - df["Last_Game_Date"]).dt.days

    df["Team_Season_Opener"] = (
        df["GAME_DATE"] == df.groupby(["Season_Year", "TEAM_ID"])["GAME_DATE"].transform("min")
    ).astype(int)

    df["Days_Since_Last_Game"] = np.where(df["Team_Season_Opener"] == 1, 4, df["Days_Since_Last_Game"])
    df["Schedule_Rest"] = df["Days_Since_Last_Game"].clip(upper=4)
    df["Long_Absence_Flag"] = (df["Days_Since_Last_Game"] > 14).astype(int)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df
