import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

afterEach(() => {
  cleanup();
});

describe("App", () => {
  it("keeps a persistent live status region and updates it during a run", async () => {
    const user = userEvent.setup();
    const createRun = vi.fn(
      () =>
        new Promise<never>(() => {
          // Keep the request pending so the loading state can be asserted.
        }),
    );

    render(<App createRun={createRun} />);

    const status = screen.getByRole("status");
    expect(status).toHaveAttribute("aria-live", "polite");
    expect(status).toHaveAttribute("aria-atomic", "true");
    expect(status).toHaveTextContent("");

    await user.click(screen.getByRole("button", { name: "Start research" }));

    expect(status).toHaveTextContent("Running research...");
    expect(
      screen.getAllByText("Running research...").find((element) => element !== status),
    ).toHaveAttribute("aria-hidden", "true");
  });

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

  it("clears the previous report when a follow-up research run fails", async () => {
    const user = userEvent.setup();
    const createRun = vi
      .fn()
      .mockResolvedValueOnce({
        run: {
          id: "run-1",
          ticker: "NVDA",
          status: "completed",
          warnings: [],
        },
        report: {
          id: "report-1",
          run_id: "run-1",
          sections: [{ title: "Prior Market Snapshot", body: "Fixture body", source_ids: ["src-1"] }],
          trade_ideas: [
            {
              structure: "Prior call spread",
              thesis: "Upside with limited premium risk",
              risk_notes: ["Can expire worthless"],
              source_ids: ["src-1"],
            },
          ],
          warnings: [],
        },
      })
      .mockRejectedValueOnce(new Error("Research request failed: 500"));

    render(<App createRun={createRun} />);

    await user.click(screen.getByRole("button", { name: "Start research" }));
    expect(await screen.findByText("Prior Market Snapshot")).toBeInTheDocument();
    expect(screen.getByText("Prior call spread")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Start research" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Research request failed: 500");
    expect(screen.queryByText("Prior Market Snapshot")).not.toBeInTheDocument();
    expect(screen.queryByText("Prior call spread")).not.toBeInTheDocument();
  });
});
