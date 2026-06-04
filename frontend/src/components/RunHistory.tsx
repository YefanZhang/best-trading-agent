import type { ResearchRun } from "../api/client";

type RunHistoryProps = {
  onSelectRun: (runId: string) => void;
  runs: ResearchRun[];
};

const runTimestampFormatter = new Intl.DateTimeFormat("en-US", {
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
  month: "short",
  timeZone: "UTC",
  timeZoneName: "short",
  year: "numeric",
});

function formatRunTimestamp(createdAt?: string): string {
  if (!createdAt) {
    return "No timestamp";
  }

  const timestamp = new Date(createdAt);
  if (Number.isNaN(timestamp.getTime())) {
    return "No timestamp";
  }

  return runTimestampFormatter.format(timestamp);
}

export function RunHistory({ onSelectRun, runs }: RunHistoryProps) {
  return (
    <section className="run-history" aria-label="Run history">
      <h2>Run history</h2>
      {runs.length === 0 ? <p>No saved runs yet.</p> : null}
      {runs.map((run) => {
        const createdAt = formatRunTimestamp(run.created_at);
        const warningCount = run.warnings.length;

        return (
          <button
            aria-label={`Open analysis for ${run.ticker} ${run.status}. Created ${createdAt}. ${warningCount} warnings.`}
            className="run-history-entry"
            key={run.id}
            onClick={() => onSelectRun(run.id)}
            type="button"
          >
            <span className="run-history-entry-main">
              <strong>{run.ticker}</strong>
              <span className="run-history-timestamp">{createdAt}</span>
            </span>
            <span className="run-history-entry-meta">
              <span className="run-history-status-badge">{run.status}</span>
              <span className="run-history-warning-count">{warningCount} warnings</span>
              <span className="run-history-action">Open analysis</span>
            </span>
          </button>
        );
      })}
    </section>
  );
}
