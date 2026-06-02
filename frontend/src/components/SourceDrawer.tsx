import { useEffect, useMemo, useRef, useState } from "react";

import type { Report, SourceDocument } from "../api/client";

type SourceReference = {
  id: string;
  count: number;
};

type SourceDrawerProps = {
  getSource: (sourceId: string) => Promise<SourceDocument>;
  listRunSources: (runId: string) => Promise<SourceDocument[]>;
  report: Report;
};

function collectSourceReferences(report: Report, runSources: SourceDocument[]): SourceReference[] {
  const sourceIds = [
    ...report.sections.flatMap((section) => section.source_ids),
    ...report.trade_ideas.flatMap((idea) => idea.source_ids),
  ];
  const countsBySourceId = new Map<string, number>();
  for (const sourceId of sourceIds) {
    countsBySourceId.set(sourceId, (countsBySourceId.get(sourceId) ?? 0) + 1);
  }
  const citedReferences = Array.from(countsBySourceId, ([id, count]) => ({ id, count }));
  const uncitedReferences = runSources
    .filter((source) => !countsBySourceId.has(source.id))
    .map((source) => ({ id: source.id, count: 0 }));
  return [...citedReferences, ...uncitedReferences];
}

function formatPayload(payload: SourceDocument["payload"]): string {
  return JSON.stringify(payload, null, 2);
}

export function SourceDrawer({ getSource, listRunSources, report }: SourceDrawerProps) {
  const [runSources, setRunSources] = useState<SourceDocument[]>([]);
  const sourceReferences = useMemo(() => collectSourceReferences(report, runSources), [report, runSources]);
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [source, setSource] = useState<SourceDocument | null>(null);
  const [isLoadingSource, setIsLoadingSource] = useState(false);
  const [isLoadingRunSources, setIsLoadingRunSources] = useState(false);
  const [sourceError, setSourceError] = useState<string | null>(null);
  const runSourcesRequestSequenceRef = useRef(0);
  const sourceDetailRequestSequenceRef = useRef(0);

  useEffect(() => {
    runSourcesRequestSequenceRef.current += 1;
    sourceDetailRequestSequenceRef.current += 1;
    setSelectedSourceId(null);
    setSource(null);
    setRunSources([]);
    setIsLoadingSource(false);
    setIsLoadingRunSources(true);
    setSourceError(null);

    const requestSequence = runSourcesRequestSequenceRef.current;
    void listRunSources(report.run_id)
      .then((nextRunSources) => {
        if (runSourcesRequestSequenceRef.current === requestSequence) {
          setRunSources(nextRunSources);
        }
      })
      .catch((error) => {
        if (runSourcesRequestSequenceRef.current === requestSequence) {
          setSourceError(error instanceof Error ? error.message : "Run sources request failed");
        }
      })
      .finally(() => {
        if (runSourcesRequestSequenceRef.current === requestSequence) {
          setIsLoadingRunSources(false);
        }
      });
  }, [listRunSources, report.run_id]);

  async function handleSelectSource(sourceId: string) {
    const requestSequence = sourceDetailRequestSequenceRef.current + 1;
    sourceDetailRequestSequenceRef.current = requestSequence;
    setSelectedSourceId(sourceId);
    setSource(null);
    setSourceError(null);
    setIsLoadingSource(true);
    try {
      const nextSource = await getSource(sourceId);
      if (sourceDetailRequestSequenceRef.current === requestSequence) {
        setSource(nextSource);
      }
    } catch (error) {
      if (sourceDetailRequestSequenceRef.current === requestSequence) {
        setSourceError(error instanceof Error ? error.message : "Source detail request failed");
      }
    } finally {
      if (sourceDetailRequestSequenceRef.current === requestSequence) {
        setIsLoadingSource(false);
      }
    }
  }

  return (
    <aside className="source-drawer" aria-label="Source drawer">
      <h2>Sources</h2>
      <div className="source-chip-list">
        {sourceReferences.map((sourceReference) => (
          <button
            className="source-chip"
            key={sourceReference.id}
            onClick={() => void handleSelectSource(sourceReference.id)}
            type="button"
          >
            <span>{sourceReference.id}</span>
            {sourceReference.count > 1 ? <span>{sourceReference.count} references</span> : null}
            {sourceReference.count === 0 ? <span>uncited</span> : null}
          </button>
        ))}
      </div>
      {isLoadingRunSources ? <p className="source-status">Loading complete source list...</p> : null}
      {isLoadingSource ? (
        <p className="source-status" role="status">
          Loading source {selectedSourceId}...
        </p>
      ) : null}
      {sourceError ? <p role="alert">{sourceError}</p> : null}
      {source ? (
        <article className="source-detail" aria-label="Source detail">
          <h3>{source.title}</h3>
          <dl>
            <div>
              <dt>Type</dt>
              <dd>{source.source_type}</dd>
            </div>
            <div>
              <dt>URL</dt>
              <dd>
                {source.url ? (
                  <a href={source.url} rel="noreferrer" target="_blank">
                    {source.url}
                  </a>
                ) : (
                  "No URL"
                )}
              </dd>
            </div>
            <div>
              <dt>Retrieved</dt>
              <dd>{source.retrieved_at}</dd>
            </div>
          </dl>
          <pre>{formatPayload(source.payload)}</pre>
        </article>
      ) : null}
    </aside>
  );
}
