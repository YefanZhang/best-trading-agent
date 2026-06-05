import type { TradeIdea } from "../api/client";

type TradePlanCardProps = {
  idea: TradeIdea;
};

const executionPlaceholders = [
  ["Entry", "Pending structured entry"],
  ["Target", "Pending target"],
  ["Stop / invalidation", "Pending invalidation"],
  ["Max loss", "Pending risk model"],
  ["Time horizon", "Pending horizon"],
  ["Position sizing", "Pending portfolio context"],
] as const;

export function TradePlanCard({ idea }: TradePlanCardProps) {
  return (
    <article className="trade-plan-card">
      <div className="section-card-meta">
        <span className="section-kind-badge options">Strategy</span>
        <span className="source-count">Source count: {idea.source_ids.length}</span>
      </div>
      <h3>{idea.structure}</h3>
      <p><strong>Thesis:</strong> {idea.thesis}</p>
      <h4>Risk checklist</h4>
      <div aria-label="Risk checklist" className="risk-note-list">
        {idea.risk_notes.map((note) => (
          <span className="risk-note-chip" key={note}>
            {note}
          </span>
        ))}
      </div>
      <dl className="execution-grid" aria-label="Execution placeholders">
        {executionPlaceholders.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}
