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
      <div className="trade-plan-header">
        <p className="eyebrow">Strategy</p>
        <h3>{idea.structure}</h3>
      </div>

      <section aria-label="Thesis">
        <h4>Thesis</h4>
        <p>{idea.thesis}</p>
      </section>

      <section aria-label="Risk checklist">
        <h4>Risk checklist</h4>
        <div className="risk-note-list">
          {idea.risk_notes.map((note) => (
            <span className="risk-note-chip" key={note}>
              {note}
            </span>
          ))}
        </div>
      </section>

      <div className="source-count">
        <span>Source count</span>
        <strong>{idea.source_ids.length}</strong>
      </div>

      <section aria-label="Execution placeholders">
        <h4>Execution placeholders</h4>
        <dl className="execution-grid">
          {executionPlaceholders.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </article>
  );
}
