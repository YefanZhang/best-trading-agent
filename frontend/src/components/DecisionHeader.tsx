import type { Report, ResearchRun } from "../api/client";
import { getUniqueSourceIds, getWarningCount } from "../domain/reportSelectors";

type DecisionHeaderProps = {
  run: ResearchRun;
  report: Report;
};

export function DecisionHeader({ run, report }: DecisionHeaderProps) {
  const primaryIdea = report.trade_ideas[0]?.structure ?? "No primary trade idea";
  const warningCount = getWarningCount(run, report);
  const uniqueSourceCount = getUniqueSourceIds(report).length;

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
