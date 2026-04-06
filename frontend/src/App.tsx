import { useEffect, useMemo, useState } from "react";
import { fetchLatestFreeAgents, fetchLatestProjections } from "./api/client";
import DataTable from "./components/DataTable";
import SummaryCard from "./components/SummaryCard";
import type { ProjectionRow } from "./types";

export default function App() {
  const [projections, setProjections] = useState<ProjectionRow[]>([]);
  const [freeAgents, setFreeAgents] = useState<ProjectionRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);

        const [projectionRes, freeAgentRes] = await Promise.all([
          fetchLatestProjections(),
          fetchLatestFreeAgents(),
        ]);

        const sortedProjections = [...projectionRes.rows].sort(
          (a, b) => Number(b.Pred_FP) - Number(a.Pred_FP)
        );
        const sortedFreeAgents = [...freeAgentRes.rows].sort(
          (a, b) => Number(b.Pred_FP) - Number(a.Pred_FP)
        );

        setProjections(sortedProjections);
        setFreeAgents(sortedFreeAgents);
        setError("");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const topProjection = useMemo(() => projections[0], [projections]);
  const topFreeAgent = useMemo(() => freeAgents[0], [freeAgents]);

  const topFreeAgentMinutes = useMemo(() => {
    if (!freeAgents.length) return undefined;
    return [...freeAgents].sort(
      (a, b) => Number(b.Pred_MIN) - Number(a.Pred_MIN)
    )[0];
  }, [freeAgents]);

  if (loading) {
    return <div style={pageStyle}>Loading dashboard...</div>;
  }

  if (error) {
    return <div style={pageStyle}>Error: {error}</div>;
  }

  return (
    <div style={pageStyle}>
      <h1 style={{ marginBottom: "8px" }}>Fantasy Hoops Winning Formula</h1>
      <p style={{ marginTop: 0, color: "#666" }}>
        Latest projections and waiver-wire recommendations
      </p>

      <div style={gridStyle}>
        <SummaryCard
          title="Top Overall Projection"
          value={
            topProjection
              ? `${topProjection.PLAYER_NAME} (${Number(topProjection.Pred_FP).toFixed(1)} FP)`
              : "N/A"
          }
        />
        <SummaryCard
          title="Top Free Agent"
          value={
            topFreeAgent
              ? `${topFreeAgent.PLAYER_NAME} (${Number(topFreeAgent.Pred_FP).toFixed(1)} FP)`
              : "N/A"
          }
        />
        <SummaryCard
          title="Top Minutes Projection Among Free Agents"
          value={
            topFreeAgentMinutes
              ? `${topFreeAgentMinutes.PLAYER_NAME} (${Number(topFreeAgentMinutes.Pred_MIN).toFixed(1)} MIN)`
              : "N/A"
          }
        />
      </div>

      <DataTable title="Top Free Agents" rows={freeAgents.slice(0, 25)} />
      <DataTable title="Top Overall Projections" rows={projections.slice(0, 25)} />
    </div>
  );
}

const pageStyle: React.CSSProperties = {
  maxWidth: "1200px",
  margin: "0 auto",
  padding: "24px",
  fontFamily: "Arial, sans-serif",
  background: "#fafafa",
  minHeight: "100vh",
};

const gridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: "16px",
  marginTop: "24px",
};