import type { ReportSection } from "../api/client";
import { deriveSectionKind, type SectionKind } from "../domain/reportSelectors";

type AnalystSectionCardProps = {
  section: ReportSection;
};

const sectionKindLabels: Record<SectionKind, string> = {
  market: "Market",
  fundamentals: "Fundamentals",
  news: "News",
  options: "Options",
  risk: "Risk",
  general: "General",
};

function formatSourceCount(count: number): string {
  return `${count} ${count === 1 ? "source" : "sources"}`;
}

export function AnalystSectionCard({ section }: AnalystSectionCardProps) {
  const sectionKind = deriveSectionKind(section);

  return (
    <article className="analyst-section-card">
      <div className="analyst-section-card__meta">
        <span className={`section-kind-badge ${sectionKind}`}>
          {sectionKindLabels[sectionKind]}
        </span>
        <span className="source-count">
          {formatSourceCount(section.source_ids.length)}
        </span>
      </div>
      <h3>{section.title}</h3>
      <p>{section.body}</p>
    </article>
  );
}
