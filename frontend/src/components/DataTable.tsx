import type { ProjectionRow } from "../types";

type DataTableProps = {
  title: string;
  rows: ProjectionRow[];
};

export default function DataTable({ title, rows }: DataTableProps) {
  return (
    <div style={{ marginTop: "24px" }}>
      <h2 style={{ marginBottom: "12px" }}>{title}</h2>
      <div
        style={{
          overflowX: "auto",
          background: "#fff",
          borderRadius: "12px",
          border: "1px solid #ddd",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f5f5f5", textAlign: "left" }}>
              <th style={thStyle}>Player</th>
              <th style={thStyle}>Team</th>
              <th style={thStyle}>Opp</th>
              <th style={thStyle}>Pred Min</th>
              <th style={thStyle}>Pred FP</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Free Agent</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={`${row.PLAYER_NAME}-${idx}`} style={{ borderTop: "1px solid #eee" }}>
                <td style={tdStyle}>{row.PLAYER_NAME}</td>
                <td style={tdStyle}>{row.Team}</td>
                <td style={tdStyle}>{row.Opp}</td>
                <td style={tdStyle}>{Number(row.Pred_MIN).toFixed(1)}</td>
                <td style={tdStyle}>{Number(row.Pred_FP).toFixed(1)}</td>
                <td style={tdStyle}>{row.Injury_Status || "ACTIVE"}</td>
                <td style={tdStyle}>{row.Free_Agent ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const thStyle: React.CSSProperties = {
  padding: "12px",
  fontSize: "14px",
  fontWeight: 600,
};

const tdStyle: React.CSSProperties = {
  padding: "12px",
  fontSize: "14px",
};