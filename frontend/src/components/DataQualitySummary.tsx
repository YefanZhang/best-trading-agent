import type { Report, ResearchRun } from "../api/client";
import {
  deriveCoverageStatus,
  getSectionCount,
  getTradeIdeaCount,
  getUniqueSourceIds,
  getWarningCount,
  type CoverageStatus,
} from "../domain/reportSelectors";

type DataQualitySummaryProps = {
  report: Report;
  run: ResearchRun;
};

const coverageLabels: Record<CoverageStatus, string> = {
  complete: "Coverage complete",
  warning: "Coverage warning",
  limited: "Limited coverage",
};

export function DataQualitySummary({ report, run }: DataQualitySummaryProps) {
  const sourceCount = getUniqueSourceIds(report).length;
  const sectionCount = getSectionCount(report);
  const tradeIdeaCount = getTradeIdeaCount(report);
  const warningCount = getWarningCount(run, report);
  const coverageStatus = deriveCoverageStatus(report, run);

  return (
    <section className="data-quality-summary" aria-label="Data quality">
      <div className="data-quality-summary__header">
        <h2>Data quality</h2>
        <span className={`coverage-badge coverage-badge--${coverageStatus}`}>
          {coverageLabels[coverageStatus]}
        </span>
      </div>
      <dl className="data-quality-metrics">
        <div>
          <dt>Evidence sources</dt>
          <dd>{sourceCount}</dd>
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
          <dt>Warning count</dt>
          <dd>{warningCount}</dd>
        </div>
      </dl>
    </section>
  );
}
