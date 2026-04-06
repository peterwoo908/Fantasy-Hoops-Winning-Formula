type SummaryCardProps = {
  title: string;
  value: string | number;
};

export default function SummaryCard({ title, value }: SummaryCardProps) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: "12px",
        padding: "16px",
        background: "#fff",
      }}
    >
      <div style={{ fontSize: "14px", color: "#666", marginBottom: "8px" }}>
        {title}
      </div>
      <div style={{ fontSize: "24px", fontWeight: 700 }}>{value}</div>
    </div>
  );
}