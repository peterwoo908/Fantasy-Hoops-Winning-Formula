from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"
PROJECTIONS_DIR = OUTPUTS_DIR / "projections"
EVALUATIONS_DIR = OUTPUTS_DIR / "evaluations"
LOGS_DIR = OUTPUTS_DIR / "logs"
FREE_AGENTS_DIR = OUTPUTS_DIR / "free_agents"

TARGET_SEASONS = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
CURRENT_SEASON = "2025-26"
TEST_SEASON = "2025-26"

PLAYER_DATA_PATH = RAW_DATA_DIR / "nba_fantasy_master_data.parquet"
TEAM_DATA_PATH = RAW_DATA_DIR / "nba_team_stats_master.parquet"
MODEL_READY_PATH = PROCESSED_DATA_DIR / "df_model_ready.parquet"
ESPN_POOL_PATH = EXTERNAL_DATA_DIR / "espn_player_pool.parquet"

MIN_MODEL_PATH = MODELS_DIR / "nba_min_model.pkl"
FP_MODEL_PATH = MODELS_DIR / "nba_fp_model.pkl"

TARGET_MIN = "MIN"
TARGET_FP = "FantasyPoints"

SCORING_RULES = {
    "FGM": 2.0,
    "FGA": -1.0,
    "FTM": 1.0,
    "FTA": -1.0,
    "FG3M": 1.0,
    "REB": 1.0,
    "AST": 2.0,
    "STL": 4.0,
    "BLK": 4.0,
    "TOV": -2.0,
    "PTS": 1.0,
}

FEATURE_COLS = [
    "Schedule_Rest",
    "Long_Absence_Flag",
    "Team_Pace",
    "Team_DefRtg",
    "Opp_Pace",
    "Opp_DefRtg",
    "Lag1_MIN",
    "Lag1_FP",
    "L3_MIN",
    "L3_FP_per_Min",
    "L3_Usage",
    "L3_FGA",
    "L3_TOV",
    "L3_PLUS_MINUS",
    "L10_MIN",
    "L10_FantasyPoints",
    "L10_FP_per_Min",
    "L10_Usage",
    "L10_FGA",
    "L10_TOV",
    "L10_3P_Pct",
    "SZ_MIN",
    "SZ_FantasyPoints",
    "SZ_FP_per_Min",
    "SZ_Usage",
]

META_COLS = [
    "PLAYER_ID",
    "PLAYER_NAME",
    "GAME_ID",
    "GAME_DATE",
    "Team",
    "Opp",
    "Season_Year",
    "SEASON_ID",
    "TEAM_ID",
]

DEFAULT_TEAM_PACE = 100.0
DEFAULT_TEAM_DEF_RTG = 112.0
