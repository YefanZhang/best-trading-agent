import { useState } from "react";

import { createResearchRun, type ResearchResult } from "./api/client";
import { ReportView } from "./components/ReportView";
import { RunForm } from "./components/RunForm";
import { RunHistory } from "./components/RunHistory";

const panels = ["Ticker command", "Market snapshot", "Catalysts", "Generated memo"];

type AppProps = {
  createRun?: (ticker: string) => Promise<ResearchResult>;
};

export function App({ createRun = createResearchRun }: AppProps) {
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [runs, setRuns] = useState<ResearchResult["run"][]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun(ticker: string) {
    setIsRunning(true);
    setError(null);
    setResult(null);
    try {
      const nextResult = await createRun(ticker);
      setResult(nextResult);
      setRuns((existingRuns) => [nextResult.run, ...existingRuns]);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Research request failed");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Workbench navigation">
        <div className="brand">best-trading-agent</div>
        <nav>
          <a href="#research">Research</a>
          <a href="#watchlist">Watchlist</a>
          <a href="#sources">Sources</a>
          <a href="#settings">Settings</a>
        </nav>
      </aside>
      <section className="workspace" id="research">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">US equities and options</p>
            <h1>Research Workbench</h1>
          </div>
          <RunForm disabled={isRunning} onSubmit={handleRun} />
        </header>
        <p className="sr-only" role="status" aria-live="polite" aria-atomic="true">
          {isRunning ? "Running research..." : ""}
        </p>
        {isRunning ? (
          <p className="status-line" aria-hidden="true">
            Running research...
          </p>
        ) : null}
        {error ? <p role="alert">{error}</p> : null}
        {result ? (
          <ReportView report={result.report} run={result.run} />
        ) : (
          <section className="panel-grid" aria-label="Research panels">
            {panels.map((panel) => (
              <div className={`panel${panel === "Generated memo" ? " wide" : ""}`} key={panel}>
                {panel}
              </div>
            ))}
          </section>
        )}
        <RunHistory runs={runs} />
      </section>
    </main>
  );
}
