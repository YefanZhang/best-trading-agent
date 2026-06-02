export type RunStatus = "pending" | "running" | "completed" | "completed_with_warnings" | "failed";

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export type DataWarning = {
  source: string;
  message: string;
};

export type ResearchRun = {
  id: string;
  ticker: string;
  created_at?: string;
  status: RunStatus;
  warnings: DataWarning[];
};

export type ReportSection = {
  title: string;
  body: string;
  source_ids: string[];
};

export type TradeIdea = {
  structure: string;
  thesis: string;
  risk_notes: string[];
  source_ids: string[];
};

export type Report = {
  id: string;
  run_id: string;
  sections: ReportSection[];
  trade_ideas: TradeIdea[];
  warnings: DataWarning[];
};

export type ResearchResult = {
  run: ResearchRun;
  report: Report;
};

export type SourceDocument = {
  id: string;
  run_id: string;
  source_type: string;
  title: string;
  url: string | null;
  retrieved_at: string;
  payload: JsonValue;
};

async function parseJsonResponse<T>(response: Response, failureMessage: string): Promise<T> {
  if (!response.ok) {
    throw new Error(`${failureMessage}: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function createResearchRun(
  ticker: string,
  fetcher: typeof fetch = fetch,
): Promise<ResearchResult> {
  const response = await fetcher("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker }),
  });

  return parseJsonResponse<ResearchResult>(response, "Research request failed");
}

export async function listRuns(fetcher: typeof fetch = fetch): Promise<ResearchRun[]> {
  const response = await fetcher("/api/runs");
  const payload = await parseJsonResponse<{ runs: ResearchRun[] }>(response, "Run history request failed");
  return payload.runs;
}

export async function getRun(runId: string, fetcher: typeof fetch = fetch): Promise<ResearchResult> {
  const response = await fetcher(`/api/runs/${encodeURIComponent(runId)}`);
  return parseJsonResponse<ResearchResult>(response, "Saved run request failed");
}

export async function listRunSources(
  runId: string,
  fetcher: typeof fetch = fetch,
): Promise<SourceDocument[]> {
  const response = await fetcher(`/api/runs/${encodeURIComponent(runId)}/sources`);
  const payload = await parseJsonResponse<{ sources: SourceDocument[] }>(
    response,
    "Run sources request failed",
  );
  return payload.sources;
}

export async function getSource(
  sourceId: string,
  fetcher: typeof fetch = fetch,
): Promise<SourceDocument> {
  const response = await fetcher(`/api/sources/${encodeURIComponent(sourceId)}`);
  const payload = await parseJsonResponse<{ source: SourceDocument }>(
    response,
    "Source detail request failed",
  );
  return payload.source;
}
