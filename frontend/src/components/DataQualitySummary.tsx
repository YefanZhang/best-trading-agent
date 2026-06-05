import type { Report, ResearchRun } from "../api/client";
import {
  deriveCoverageStatus,
  getSectionCount,
  getTradeIdeaCount,
  getUniqueSourceIds,
  getWarningCount,
} from "../domain/reportSelectors";

const coverageStatusLabels = {
  complete: "Coverage complete",
  warning: "Coverage warning",
  limited: "Coverage limited",
} as const;

type DataQualitySummaryProps = {
  run: ResearchRun;
  report: Report;
};

export function DataQualitySummary({ run, report }: DataQualitySummaryProps) {
  const evidenceSourceCount = getUniqueSourceIds(report).length;
  const sectionCount = getSectionCount(report);
  const tradeIdeaCount = getTradeIdeaCount(report);
  const warningCount = getWarningCount(run, report);
  const coverageStatus = deriveCoverageStatus(report, run);

  return (
    <section className="data-quality-summary" aria-label="Data quality">
      <div className="data-quality-heading">
        <div>
          <p className="eyebrow">Data quality</p>
          <h2>Data quality</h2>
        </div>
        <span className={`coverage-status-badge ${coverageStatus}`}>{coverageStatusLabels[coverageStatus]}</span>
      </div>
      <dl className="data-quality-metrics">
        <div>
          <dt>Evidence sources</dt>
          <dd>{evidenceSourceCount}</dd>
        </div>
        <div>
          <dt>Analyst sections</dt>
          <dd>{sectionCount}</dd>
        </div>
        <div>
          <dt>Trade ideas</dt>
          <dd>{tradeIdeaCount}</dd>
        </div>
        <div>
          <dt>Warnings</dt>
          <dd>{warningCount}</dd>
        </div>
      </dl>
    </section>
  );
}
