from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.config import PROJECTIONS_DIR, FREE_AGENTS_DIR


app = FastAPI(title="Fantasy Hoops API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _latest_csv(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files found in {directory} matching {pattern}")
    return files[-1]


def _load_csv(path: Path) -> list[dict]:
    df = pd.read_csv(path)
    df = df.fillna("")
    return df.to_dict(orient="records")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/projections/latest")
def get_latest_projections() -> dict:
    try:
        path = _latest_csv(PROJECTIONS_DIR, "*_projections.csv")
        return {
            "file": path.name,
            "rows": _load_csv(path),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/free-agents/latest")
def get_latest_free_agents() -> dict:
    try:
        path = _latest_csv(FREE_AGENTS_DIR, "*_top_free_agents.csv")
        return {
            "file": path.name,
            "rows": _load_csv(path),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/projections/by-date/{date_str}")
def get_projections_by_date(date_str: str) -> dict:
    path = PROJECTIONS_DIR / f"{date_str}_projections.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No projections file found for {date_str}")
    return {
        "file": path.name,
        "rows": _load_csv(path),
    }


@app.get("/api/free-agents/by-date/{date_str}")
def get_free_agents_by_date(date_str: str) -> dict:
    path = FREE_AGENTS_DIR / f"{date_str}_top_free_agents.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No free-agent file found for {date_str}")
    return {
        "file": path.name,
        "rows": _load_csv(path),
    }