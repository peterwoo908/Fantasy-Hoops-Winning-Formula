import argparse


from src.pipelines.build_model_dataset import build_model_dataset
from src.pipelines.run_daily_pipeline import run_daily_pipeline
from src.pipelines.train_models import train_models


from dotenv import load_dotenv
from pathlib import Path


def main():

    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    parser = argparse.ArgumentParser(description="Fantasy NBA ML pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-dataset", help="Update raw data and build the model-ready dataset")
    build_parser.add_argument(
        "--skip-fetch",
        action="store_true",
        default=False,
        help="Skip nba_api calls and build features from the committed parquets only (used in CI)",
    )
    subparsers.add_parser("train-models", help="Train/evaluate models and save production models")

    inference_parser = subparsers.add_parser("run-inference", help="Run daily inference")
    inference_parser.add_argument("--date", dest="date_str", default=None, help="Target date in YYYY-MM-DD format")

    args = parser.parse_args()

    if args.command == "build-dataset":
        build_model_dataset(skip_fetch=args.skip_fetch)
    elif args.command == "train-models":
        train_models()
    elif args.command == "run-inference":
        run_daily_pipeline(date_str=args.date_str)


if __name__ == "__main__":
    main()
