import type { ResearchRun } from "../api/client";

type RunHistoryProps = {
  onSelectRun: (runId: string) => void;
  runs: ResearchRun[];
};

export function RunHistory({ onSelectRun, runs }: RunHistoryProps) {
  return (
    <section className="run-history" aria-label="Run history">
      <h2>Run history</h2>
      {runs.length === 0 ? <p>No saved runs yet.</p> : null}
      {runs.map((run) => (
        <button className="run-history-entry" key={run.id} onClick={() => onSelectRun(run.id)} type="button">
          <strong>{run.ticker}</strong>
          <span>{run.status}</span>
        </button>
      ))}
    </section>
  );
}
