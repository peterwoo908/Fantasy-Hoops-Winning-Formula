import pandas as pd
from pathlib import Path

from src.config import MODEL_READY_PATH, PROJECTIONS_DIR, TEAM_DATA_PATH, FREE_AGENTS_DIR
from src.data_ingestion.espn_data import load_or_fetch_espn_player_pool
from src.inference.daily_inference import run_daily_inference
from src.inference.free_agents import build_top_free_agents
from src.modeling.model_io import load_production_models
from src.utils import ensure_directories, get_nba_day_string


def run_daily_pipeline(date_str: str | None = None) -> pd.DataFrame:
    ensure_directories()
    date_str = date_str or get_nba_day_string(1)

    if not MODEL_READY_PATH.exists():
        raise FileNotFoundError(
            f"Model-ready dataset not found at {MODEL_READY_PATH}. Run build-dataset first."
        )
    if not TEAM_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Team data not found at {TEAM_DATA_PATH}. Run build-dataset first."
        )

    df_model_ready = pd.read_parquet(MODEL_READY_PATH)
    df_team_rolling = pd.read_parquet(TEAM_DATA_PATH)
    model_min, model_fp = load_production_models()
    df_espn_pool = load_or_fetch_espn_player_pool()

    daily_projections = run_daily_inference(
        date_str=date_str,
        df_all_cols=df_model_ready,
        df_team_rolling=df_team_rolling,
        model_min=model_min,
        model_fp=model_fp,
        df_espn_pool=df_espn_pool,
    )

    if not daily_projections.empty:
        output_path = PROJECTIONS_DIR / f"{date_str}_projections.csv"
        daily_projections.to_csv(output_path, index=False)
        print(f"Saved daily projections to {output_path}")

        free_agent_output = FREE_AGENTS_DIR / f"{date_str}_top_free_agents.csv"
        build_top_free_agents(
            projections_path=output_path,
            output_path=free_agent_output,
            min_pred_fp=25.0,
            limit=50,
        )
        print(f"Saved top free agents to {free_agent_output}")

    return daily_projections