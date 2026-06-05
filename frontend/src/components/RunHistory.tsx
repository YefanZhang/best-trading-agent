import type { ResearchRun } from "../api/client";

type RunHistoryProps = {
  onSelectRun: (runId: string) => void;
  runs: ResearchRun[];
};

const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "short",
});

function formatRunTimestamp(createdAt?: string) {
  if (!createdAt) {
    return "No timestamp";
  }

  const createdAtDate = new Date(createdAt);
  if (Number.isNaN(createdAtDate.getTime())) {
    return "No timestamp";
  }

  return dateTimeFormatter.format(createdAtDate);
}

function formatWarningCount(count: number) {
  return `${count} ${count === 1 ? "warning" : "warnings"}`;
}

export function RunHistory({ onSelectRun, runs }: RunHistoryProps) {
  return (
    <section className="run-history" aria-label="Run history">
      <h2>Run history</h2>
      {runs.length === 0 ? <p>No saved runs yet.</p> : null}
      {runs.map((run) => {
        const createdAtLabel = formatRunTimestamp(run.created_at);
        const warningCountLabel = formatWarningCount(run.warnings.length);

        return (
          <button
            aria-label={`Open analysis for ${run.ticker} ${run.status} run`}
            className="run-history-entry"
            key={run.id}
            onClick={() => onSelectRun(run.id)}
            type="button"
          >
            <span className="run-history-primary">
              <strong>{run.ticker}</strong>
              <span className="run-history-timestamp">{createdAtLabel}</span>
            </span>
            <span className="run-history-secondary">
              <span className="run-history-status-badge">{run.status}</span>
              <span className="run-history-warning-count">{warningCountLabel}</span>
              <span className="run-history-action">Open analysis</span>
            </span>
          </button>
        );
      })}
    </section>
  );
}
