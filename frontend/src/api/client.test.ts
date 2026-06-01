import { describe, expect, it, vi } from "vitest";

import { createResearchRun } from "./client";

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
