#!/bin/bash
# Runs daily via launchd on your Mac (see com.fantasy-hoops.fetch.plist).
# Fetches the nba_api incremental delta from your home IP (not blocked),
# then commits and pushes the updated raw parquets so GitHub Actions can
# rebuild features and run inference without touching nba_api itself.

set -euo pipefail

PROJECT_DIR="/Users/petewoo/Downloads/fantasy-project"
VENV="$PROJECT_DIR/.venv/bin/activate"
LOG_PREFIX="[fantasy-fetch $(date '+%Y-%m-%d %H:%M:%S')]"

echo "$LOG_PREFIX Starting incremental data fetch..."

cd "$PROJECT_DIR"
source "$VENV"

# Pull any commits the GitHub Actions bot may have pushed (projection CSVs)
# before we push our own commit, to avoid a non-fast-forward rejection.
git pull --rebase origin main

# Fetch the nba_api delta and rebuild the model-ready dataset locally.
# This is the only step that calls stats.nba.com — it must run from your home IP.
python -m src.main build-dataset

# Stage only the raw parquets — these are the files GitHub Actions needs.
# The processed parquet (df_model_ready) is gitignored and rebuilt in the cloud.
git add data/raw/nba_fantasy_master_data.parquet data/raw/nba_team_stats_master.parquet

if git diff --cached --quiet; then
    echo "$LOG_PREFIX No new game data found — parquets unchanged, nothing to push."
    exit 0
fi

DATE=$(date +%F)
git commit -m "chore: update raw parquets for $DATE"
git push origin main

echo "$LOG_PREFIX Done — pushed updated parquets for $DATE."
