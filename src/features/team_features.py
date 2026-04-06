import numpy as np
import pandas as pd

from src.utils import require_columns


def calculate_advanced_stats(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, ["GAME_ID", "TEAM_ID", "FGA", "FTA", "TOV", "OREB", "PTS", "MIN"], "team data")
    df = df.copy()
    cols_to_drop = ["Poss", "Game_Pace", "DefRtg", "OPP_TEAM_ID", "OPP_POSS", "OPP_PTS"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    df["Poss"] = df["FGA"] + 0.44 * df["FTA"] + df["TOV"] - df["OREB"]

    opponent_view = df[["GAME_ID", "TEAM_ID", "Poss", "PTS"]].copy().rename(
        columns={"TEAM_ID": "OPP_TEAM_ID", "Poss": "OPP_POSS", "PTS": "OPP_PTS"}
    )

    merged = pd.merge(df, opponent_view, on="GAME_ID", suffixes=("", "_dup"))
    merged = merged[merged["TEAM_ID"] != merged["OPP_TEAM_ID"]].copy()

    merged["Game_Pace"] = merged.apply(
        lambda row: ((row["Poss"] + row["OPP_POSS"]) / 2) * (48 / (row["MIN"] / 5)) if row["MIN"] > 0 else 0,
        axis=1,
    )
    merged["DefRtg"] = merged.apply(
        lambda row: (row["OPP_PTS"] / row["Poss"]) * 100 if row["Poss"] > 0 else 0,
        axis=1,
    )
    return merged


def apply_bayesian_smoothing(df: pd.DataFrame, k: int = 10) -> pd.DataFrame:
    require_columns(df, ["Season_Year", "GAME_DATE", "TEAM_ID", "Game_Pace", "DefRtg"], "team advanced stats")
    seasons = sorted(df["Season_Year"].dropna().unique())
    smoothed_results = []
    priors: dict[int, dict[str, float]] = {}

    for season in seasons:
        season_df = df[df["Season_Year"] == season].sort_values("GAME_DATE")
        for team_id in season_df["TEAM_ID"].unique():
            t_df = season_df[season_df["TEAM_ID"] == team_id].copy()
            t_df["Cum_Pace"] = t_df["Game_Pace"].expanding().mean()
            t_df["Cum_DRtg"] = t_df["DefRtg"].expanding().mean()
            t_df["Game_N"] = np.arange(1, len(t_df) + 1)

            prior_pace = priors.get(team_id, {}).get("Pace", 100.0)
            prior_drtg = priors.get(team_id, {}).get("DRtg", 112.0)

            t_df["Pace_Feature"] = ((t_df["Cum_Pace"] * t_df["Game_N"]) + (prior_pace * k)) / (t_df["Game_N"] + k)
            t_df["DRtg_Feature"] = ((t_df["Cum_DRtg"] * t_df["Game_N"]) + (prior_drtg * k)) / (t_df["Game_N"] + k)
            t_df["Rolling_Pace"] = t_df["Pace_Feature"].shift(1)
            t_df["Rolling_DRtg"] = t_df["DRtg_Feature"].shift(1)

            t_df.iloc[0, t_df.columns.get_loc("Rolling_Pace")] = prior_pace
            t_df.iloc[0, t_df.columns.get_loc("Rolling_DRtg")] = prior_drtg

            priors[team_id] = {
                "Pace": t_df["Cum_Pace"].iloc[-1],
                "DRtg": t_df["Cum_DRtg"].iloc[-1],
            }
            smoothed_results.append(t_df)

    if not smoothed_results:
        raise RuntimeError("No smoothed team results generated.")

    return pd.concat(smoothed_results, ignore_index=True)
