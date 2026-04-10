from datetime import date

from src.pipelines.build_model_dataset import build_model_dataset
from src.pipelines.run_daily_pipeline import run_daily_pipeline


def refresh_for_date(date_str: str | None = None):
    target_date = date_str or date.today().isoformat()

    # Rebuild raw/processed data
    build_model_dataset()

    # Run inference for the chosen date
    projections = run_daily_pipeline(date_str=target_date)

    return {
        "date": target_date,
        "projection_count": 0 if projections is None else len(projections),
    }