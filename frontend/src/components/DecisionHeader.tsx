import type { Report, ResearchRun } from "../api/client";

type DecisionHeaderProps = {
  run: ResearchRun;
  report: Report;
};

function countUniqueSources(report: Report): number {
  const sourceIds = new Set([
    ...report.sections.flatMap((section) => section.source_ids),
    ...report.trade_ideas.flatMap((idea) => idea.source_ids),
  ]);

  return sourceIds.size;
}

export function DecisionHeader({ run, report }: DecisionHeaderProps) {
  const primaryIdea = report.trade_ideas[0]?.structure ?? "No primary trade idea";
  const warningCount = report.warnings.length + run.warnings.length;
  const uniqueSourceCount = countUniqueSources(report);

  return (
    <header className="decision-header" aria-label="Decision summary">
      <div className="decision-metric">
        <span>Ticker</span>
        <strong>{run.ticker}</strong>
      </div>
      <div className="decision-metric">
        <span>Status</span>
        <strong>{run.status}</strong>
      </div>
      <div className="decision-metric">
        <span>Primary idea</span>
        <strong>{primaryIdea}</strong>
      </div>
      <div className="decision-metric">
        <span>Warnings</span>
        <strong>{warningCount}</strong>
      </div>
      <div className="decision-metric">
        <span>Sources</span>
        <strong>{uniqueSourceCount}</strong>
      </div>
      <div className="recommendation-badge">Structured recommendation pending</div>
      <div className="confidence-placeholder">Confidence pending</div>
    </header>
  );
}
