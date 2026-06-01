import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("runs research and renders report with separated trade ideas", async () => {
    const user = userEvent.setup();
    const createRun = vi.fn().mockResolvedValue({
      run: {
        id: "run-1",
        ticker: "NVDA",
        status: "completed_with_warnings",
        warnings: [{ source: "news", message: "Partial coverage" }],
      },
      report: {
        id: "report-1",
        run_id: "run-1",
        sections: [{ title: "Market Snapshot", body: "Fixture body", source_ids: ["src-1"] }],
        trade_ideas: [
          {
            structure: "Defined-risk call spread",
            thesis: "Upside with limited premium risk",
            risk_notes: ["Can expire worthless"],
            source_ids: ["src-1"],
          },
        ],
        warnings: [{ source: "news", message: "Partial coverage" }],
      },
    });

    render(<App createRun={createRun} />);
    await user.clear(screen.getByLabelText("Ticker"));
    await user.type(screen.getByLabelText("Ticker"), "nvda");
    await user.click(screen.getByRole("button", { name: "Start research" }));

    expect(await screen.findByText("Market Snapshot")).toBeInTheDocument();
    expect(screen.getByText("Defined-risk call spread")).toBeInTheDocument();
    expect(screen.getByText("Partial coverage")).toBeInTheDocument();
  });
});
