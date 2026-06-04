import type { Report, ResearchRun, SourceDocument } from "../api/client";
import { SourceDrawer } from "./SourceDrawer";
import { TradePlanCard } from "./TradePlanCard";

type ReportViewProps = {
  getSource: (sourceId: string) => Promise<SourceDocument>;
  listRunSources: (runId: string) => Promise<SourceDocument[]>;
  run: ResearchRun;
  report: Report;
};

export function ReportView({ getSource, listRunSources, run, report }: ReportViewProps) {
  return (
    <section className="report-view" aria-label="Research report">
      <div className="status-line">
        <strong>{run.ticker}</strong>
        <span>{run.status}</span>
      </div>
      {report.warnings.length > 0 ? (
        <section className="warning-list" aria-label="Warnings">
          {report.warnings.map((warning) => (
            <p key={`${warning.source}-${warning.message}`}>
              <strong>{warning.source}:</strong> {warning.message}
            </p>
          ))}
        </section>
      ) : null}
      <section>
        <h2>Evidence memo</h2>
        {report.sections.map((section) => (
          <article className="report-card" key={section.title}>
            <h3>{section.title}</h3>
            <p>{section.body}</p>
          </article>
        ))}
      </section>
      <section>
        <h2>Trade ideas</h2>
        {report.trade_ideas.map((idea) => (
          <TradePlanCard idea={idea} key={idea.structure} />
        ))}
      </section>
      <SourceDrawer getSource={getSource} listRunSources={listRunSources} report={report} />
    </section>
  );
}
