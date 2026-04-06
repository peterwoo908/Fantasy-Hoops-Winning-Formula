from pathlib import Path

import pandas as pd

from src.config import PROJECTIONS_DIR


def update_projections_with_actuals(date_obj, player_data: pd.DataFrame, projections_dir=PROJECTIONS_DIR) -> None:
    date_str = date_obj if isinstance(date_obj, str) else date_obj.strftime("%Y-%m-%d")
    file_path = Path(projections_dir) / f"{date_str}_projections.csv"

    if not file_path.exists():
        print(f"Projection file not found: {file_path}")
        return

    df_proj = pd.read_csv(file_path)

    def is_nonempty(col: str) -> bool:
        return col in df_proj.columns and df_proj[col].notna().any()

    if is_nonempty("Actual_FP"):
        print(f"Actuals already exist in {file_path}. Skipping update.")
        return

    df_proj = df_proj.drop(columns=[c for c in ["Actual_Min", "Min_Diff", "Actual_FP", "FP_Diff"] if c in df_proj.columns])
    player_data = player_data.copy()
    player_data["Match_Date"] = pd.to_datetime(player_data["GAME_DATE"]).dt.strftime("%Y-%m-%d")
    df_actuals = player_data.loc[player_data["Match_Date"] == date_str, ["PLAYER_NAME", "MIN", "FantasyPoints"]].copy()
    df_actuals = df_actuals.rename(columns={"MIN": "Actual_Min", "FantasyPoints": "Actual_FP"})
    df_actuals = df_actuals.groupby("PLAYER_NAME").mean(numeric_only=True).reset_index()

    df_merged = pd.merge(df_proj, df_actuals, on="PLAYER_NAME", how="left")
    df_merged["Min_Diff"] = (df_merged["Actual_Min"] - df_merged["Pred_MIN"]).round(3)
    df_merged["FP_Diff"] = (df_merged["Actual_FP"] - df_merged["Pred_FP"]).round(3)

    cols = list(df_proj.columns)
    if "Pred_MIN" in cols:
        idx = cols.index("Pred_MIN") + 1
        cols[idx:idx] = ["Actual_Min", "Min_Diff"]
    else:
        cols.extend(["Actual_Min", "Min_Diff"])

    if "Pred_FP" in cols:
        idx = cols.index("Pred_FP") + 1
        cols[idx:idx] = ["Actual_FP", "FP_Diff"]
    else:
        cols.extend(["Actual_FP", "FP_Diff"])

    df_merged[cols].to_csv(file_path, index=False)
    print(f"Updated {file_path} with actuals.")
