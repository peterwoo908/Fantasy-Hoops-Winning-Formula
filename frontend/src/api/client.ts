import type { ApiResponse, ProjectionRow } from "../types/index";

const API_BASE = "http://127.0.0.1:8000";

export async function fetchLatestProjections(): Promise<ApiResponse<ProjectionRow>> {
  const res = await fetch(`${API_BASE}/api/projections/latest`);
  if (!res.ok) {
    throw new Error("Failed to fetch latest projections");
  }
  return res.json();
}

export async function fetchLatestFreeAgents(): Promise<ApiResponse<ProjectionRow>> {
  const res = await fetch(`${API_BASE}/api/free-agents/latest`);
  if (!res.ok) {
    throw new Error("Failed to fetch latest free agents");
  }
  return res.json();
}