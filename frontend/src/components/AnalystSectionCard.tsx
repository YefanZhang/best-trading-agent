import type { ReportSection } from "../api/client";
import { deriveSectionKind } from "../domain/reportSelectors";

type AnalystSectionCardProps = {
  section: ReportSection;
};

const sectionKindLabels: Record<ReturnType<typeof deriveSectionKind>, string> = {
  market: "Market",
  fundamentals: "Fundamentals",
  news: "News",
  options: "Options",
  risk: "Risk",
  general: "General",
};

export function AnalystSectionCard({ section }: AnalystSectionCardProps) {
  const sectionKind = deriveSectionKind(section);
  const sourceCount = section.source_ids.length;

  return (
    <article className="analyst-section-card">
      <div className="section-card-meta">
        <span className={`section-kind-badge ${sectionKind}`}>{sectionKindLabels[sectionKind]}</span>
        <span className="source-count">
          {sourceCount} {sourceCount === 1 ? "source" : "sources"}
        </span>
      </div>
      <h3>{section.title}</h3>
      <p>{section.body}</p>
    </article>
  );
}
