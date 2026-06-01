import type { ResearchRun } from "../api/client";

type RunHistoryProps = {
  runs: ResearchRun[];
};

export function RunHistory({ runs }: RunHistoryProps) {
  return (
    <section className="run-history" aria-label="Run history">
      <h2>Run history</h2>
      {runs.length === 0 ? <p>No saved runs yet.</p> : null}
      {runs.map((run) => (
        <article key={run.id}>
          <strong>{run.ticker}</strong>
          <span>{run.status}</span>
        </article>
      ))}
    </section>
  );
}
