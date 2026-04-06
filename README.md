# Fantasy NBA ML Pipeline

Starter project scaffold for an NBA fantasy-points pipeline refactored out of a Jupyter notebook.

## What this project does

- Pulls and updates player game logs from `nba_api`
- Pulls and updates team game logs from `nba_api`
- Engineers player and team rolling features
- Merges those features into a model-ready dataset
- Trains a two-stage XGBoost pipeline:
  - Stage 1: predict minutes
  - Stage 2: predict fantasy points using predicted minutes
- Runs daily inference for a target date
- Saves projection CSVs and can later append actual results

## Project layout

```text
fantasy-project/
├─ notebooks/
├─ src/
│  ├─ config.py
│  ├─ utils.py
│  ├─ data_ingestion/
│  ├─ features/
│  ├─ modeling/
│  ├─ inference/
│  └─ pipelines/
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ external/
├─ models/
├─ outputs/
│  ├─ projections/
│  ├─ evaluations/
│  └─ logs/
└─ tests/
```

## First steps

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables for ESPN access:

```bash
export ESPN_LEAGUE_ID="your_league_id"
export ESPN_YEAR="2026"
export ESPN_SWID="{YOUR-SWID}"
export ESPN_S2="your_espn_s2"
```

4. Build/update the model dataset:

```bash
python -m src.main build-dataset
```

5. Train models:

```bash
python -m src.main train-models
```

6. Run daily projections for a date:

```bash
python -m src.main run-inference --date 2026-04-06
```

## Important notes

- ESPN credentials are intentionally **not** stored in code.
- Model-ready feature lists are centralized in `src/config.py` so training and inference stay aligned.
- This scaffold keeps your logic modular, but you will likely still want to tune, test, and simplify pieces once you validate the first end-to-end run.
