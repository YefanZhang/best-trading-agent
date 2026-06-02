import { describe, expect, it, vi } from "vitest";

import { createResearchRun, getRun, getSource, listRunSources, listRuns } from "./client";

describe("createResearchRun", () => {
  it("posts ticker and returns run result", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        run: { id: "run-1", ticker: "NVDA", status: "completed_with_warnings", warnings: [] },
        report: { id: "report-1", run_id: "run-1", sections: [], trade_ideas: [], warnings: [] },
      }),
    });

    const result = await createResearchRun("nvda", fetchMock);

    expect(fetchMock).toHaveBeenCalledWith("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker: "nvda" }),
    });
    expect(result.run.ticker).toBe("NVDA");
  });
});

describe("run and source API helpers", () => {
  it("lists persisted runs", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        runs: [{ id: "run-1", ticker: "NVDA", status: "completed", warnings: [] }],
      }),
    });

    const runs = await listRuns(fetchMock);

    expect(fetchMock).toHaveBeenCalledWith("/api/runs");
    expect(runs).toEqual([{ id: "run-1", ticker: "NVDA", status: "completed", warnings: [] }]);
  });

  it("gets a persisted run report", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        run: { id: "run-2", ticker: "MSFT", status: "completed", warnings: [] },
        report: { id: "report-2", run_id: "run-2", sections: [], trade_ideas: [], warnings: [] },
      }),
    });

    const result = await getRun("run-2", fetchMock);

    expect(fetchMock).toHaveBeenCalledWith("/api/runs/run-2");
    expect(result.report.run_id).toBe("run-2");
  });

  it("lists sources for a run", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        sources: [
          {
            id: "src-1",
            run_id: "run-1",
            source_type: "market",
            title: "Market snapshot",
            url: "https://example.test/market",
            retrieved_at: "2026-06-01T12:00:00Z",
            payload: { price: 123 },
          },
        ],
      }),
    });

    const sources = await listRunSources("run-1", fetchMock);

    expect(fetchMock).toHaveBeenCalledWith("/api/runs/run-1/sources");
    expect(sources[0].payload).toEqual({ price: 123 });
  });

  it("gets a single source document", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        source: {
          id: "src-1",
          run_id: "run-1",
          source_type: "news",
          title: "News item",
          url: null,
          retrieved_at: "2026-06-01T12:00:00Z",
          payload: ["headline"],
        },
      }),
    });

    const source = await getSource("src-1", fetchMock);

    expect(fetchMock).toHaveBeenCalledWith("/api/sources/src-1");
    expect(source.title).toBe("News item");
    expect(source.payload).toEqual(["headline"]);
  });
});
