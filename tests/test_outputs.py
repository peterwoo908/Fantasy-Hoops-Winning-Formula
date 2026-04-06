from pathlib import Path
import pandas as pd

def _latest_projection_file():
    projection_dir = Path("outputs/projections")
    files = sorted(projection_dir.glob("*_projections.csv"))
    assert files, "No projection files found in outputs/projections"
    return files[-1]

def test_projection_file_exists():
    path = _latest_projection_file()
    assert path.exists()

def test_projection_file_has_required_columns():
    df = pd.read_csv(_latest_projection_file())
    required = {"Date", "PLAYER_NAME", "Pred_MIN", "Pred_FP"}
    missing = required - set(df.columns)
    assert not missing, f"Missing required columns: {missing}"

def test_projection_file_not_empty():
    df = pd.read_csv(_latest_projection_file())
    assert not df.empty, "Projection file is empty"

def test_free_agent_output_if_present():
    free_agent_dir = Path("outputs/free_agents")
    files = sorted(free_agent_dir.glob("*_top_free_agents.csv"))
    if not files:
        return

    df = pd.read_csv(files[-1])
    assert "Pred_FP" in df.columns