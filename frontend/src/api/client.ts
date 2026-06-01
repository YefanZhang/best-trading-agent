export type RunStatus = "pending" | "running" | "completed" | "completed_with_warnings" | "failed";

export type DataWarning = {
  source: string;
  message: string;
};

export type ResearchRun = {
  id: string;
  ticker: string;
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

export async function createResearchRun(
  ticker: string,
  fetcher: typeof fetch = fetch,
): Promise<ResearchResult> {
  const response = await fetcher("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker }),
  });

  if (!response.ok) {
    throw new Error(`Research request failed: ${response.status}`);
  }

  return response.json() as Promise<ResearchResult>;
}
