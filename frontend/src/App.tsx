import { useEffect, useState } from "react";

import {
  createResearchRun,
  getRun as fetchRun,
  getSource as fetchSource,
  listRunSources as fetchRunSources,
  listRuns as fetchRuns,
  type ResearchResult,
  type ResearchRun,
  type SourceDocument,
} from "./api/client";
import { ProfessionalEmptyState } from "./components/ProfessionalEmptyState";
import { ReportView } from "./components/ReportView";
import { RunForm } from "./components/RunForm";
import { RunHistory } from "./components/RunHistory";


type AppProps = {
  createRun?: (ticker: string) => Promise<ResearchResult>;
  getRun?: (runId: string) => Promise<ResearchResult>;
  getSource?: (sourceId: string) => Promise<SourceDocument>;
  listRunSources?: (runId: string) => Promise<SourceDocument[]>;
  listRuns?: () => Promise<ResearchRun[]>;
};

function mergeRuns(primaryRuns: ResearchRun[], secondaryRuns: ResearchRun[]): ResearchRun[] {
  const seenRunIds = new Set<string>();
  return [...primaryRuns, ...secondaryRuns].filter((run) => {
    if (seenRunIds.has(run.id)) {
      return false;
    }
    seenRunIds.add(run.id);
    return true;
  });
}

export function App({
  createRun = createResearchRun,
  getRun = fetchRun,
  getSource = fetchSource,
  listRunSources = fetchRunSources,
  listRuns = fetchRuns,
}: AppProps) {
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [runs, setRuns] = useState<ResearchRun[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isLoadingRun, setIsLoadingRun] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    async function loadRuns() {
      try {
        const persistedRuns = await listRuns();
        if (isCurrent) {
          setRuns((existingRuns) => mergeRuns(existingRuns, persistedRuns));
        }
      } catch (error) {
        if (isCurrent) {
          setError(error instanceof Error ? error.message : "Run history request failed");
        }
      }
    }

    void loadRuns();

    return () => {
      isCurrent = false;
    };
  }, [listRuns]);

  async function handleRun(ticker: string) {
    setIsRunning(true);
    setError(null);
    setResult(null);
    try {
      const nextResult = await createRun(ticker);
      setResult(nextResult);
      setRuns((existingRuns) => mergeRuns([nextResult.run], existingRuns));
    } catch (error) {
      setError(error instanceof Error ? error.message : "Research request failed");
    } finally {
      setIsRunning(false);
    }
  }

  async function handleSelectRun(runId: string) {
    setIsLoadingRun(true);
    setError(null);
    setResult(null);
    try {
      const savedResult = await getRun(runId);
      setResult(savedResult);
      setRuns((existingRuns) => mergeRuns([savedResult.run], existingRuns));
    } catch (error) {
      setError(error instanceof Error ? error.message : "Saved run request failed");
    } finally {
      setIsLoadingRun(false);
    }
  }

  const statusText = isRunning ? "Running research..." : isLoadingRun ? "Loading saved run..." : "";

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
          {statusText}
        </p>
        {statusText ? (
          <p className="status-line" aria-hidden="true">
            {statusText}
          </p>
        ) : null}
        {error ? <p role="alert">{error}</p> : null}
        {result ? (
          <ReportView
            getSource={getSource}
            listRunSources={listRunSources}
            report={result.report}
            run={result.run}
          />
        ) : (
          <ProfessionalEmptyState />
        )}
        <RunHistory onSelectRun={handleSelectRun} runs={runs} />
      </section>
    </main>
  );
}
