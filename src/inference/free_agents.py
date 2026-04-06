from pathlib import Path
import pandas as pd


def build_top_free_agents(
    projections_path: str | Path,
    output_path: str | Path,
    min_pred_fp: float = 25.0,
    limit: int = 50,
) -> pd.DataFrame:
    projections_path = Path(projections_path)
    output_path = Path(output_path)

    df = pd.read_csv(projections_path)

    required = {"Free_Agent", "Pred_FP"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in projections file: {missing}")

    free_agents = df[df["Free_Agent"] == True].copy()
    free_agents = free_agents[free_agents["Pred_FP"] >= min_pred_fp].copy()
    free_agents = free_agents.sort_values("Pred_FP", ascending=False).head(limit)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    free_agents.to_csv(output_path, index=False)

    return free_agents