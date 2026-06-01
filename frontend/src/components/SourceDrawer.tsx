import type { ReportSection } from "../api/client";

type SourceDrawerProps = {
  sections: ReportSection[];
};

export function SourceDrawer({ sections }: SourceDrawerProps) {
  const sourceIds = Array.from(new Set(sections.flatMap((section) => section.source_ids)));

  return (
    <aside className="source-drawer" aria-label="Source drawer">
      <h2>Sources</h2>
      <div className="source-chip-list">
        {sourceIds.map((sourceId) => (
          <button className="source-chip" key={sourceId} type="button">
            {sourceId}
          </button>
        ))}
      </div>
    </aside>
  );
}
