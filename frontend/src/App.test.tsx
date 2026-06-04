import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import type { ResearchResult, ResearchRun, SourceDocument } from "./api/client";

afterEach(() => {
  cleanup();
});

const completedRun = (id: string, ticker: string): ResearchRun => ({
  id,
  ticker,
  status: "completed",
  warnings: [],
});

const resultFixture = ({
  run = completedRun("run-1", "NVDA"),
  sectionSourceIds = ["src-section"],
  tradeSourceIds = ["src-trade"],
}: {
  run?: ResearchRun;
  sectionSourceIds?: string[];
  tradeSourceIds?: string[];
} = {}): ResearchResult => ({
  run,
  report: {
    id: `${run.id}-report`,
    run_id: run.id,
    sections: [
      {
        title: `${run.ticker} Market Snapshot`,
        body: "Fixture body",
        source_ids: sectionSourceIds,
      },
    ],
    trade_ideas: [
      {
        structure: `${run.ticker} call spread`,
        thesis: "Upside with limited premium risk",
        risk_notes: ["Can expire worthless"],
        source_ids: tradeSourceIds,
      },
    ],
    warnings: [],
  },
});

const sourceFixture = (id: string, overrides: Partial<SourceDocument> = {}): SourceDocument => ({
  id,
  run_id: "run-1",
  source_type: "news",
  title: "Primary source title",
  url: "https://example.test/source",
  retrieved_at: "2026-06-01T12:00:00Z",
  payload: { headline: "Source headline", scores: [1, 2] },
  ...overrides,
});

describe("App", () => {
  it("renders the professional empty state before a report is available", () => {
    render(<App listRuns={vi.fn().mockResolvedValue([])} />);

    expect(screen.getByText("Research workflow")).toBeInTheDocument();
    expect(screen.getByText("Data coverage")).toBeInTheDocument();
    expect(screen.getByText("Agent roles")).toBeInTheDocument();
    expect(screen.getByText("Expected outputs")).toBeInTheDocument();
  });

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
    expect(screen.getByLabelText("Source drawer")).toBeInTheDocument();
    expect(screen.getByText("src-1")).toBeInTheDocument();
    expect(screen.getByLabelText("Run history")).toBeInTheDocument();
  });

  it("loads persisted runs on startup and preserves newly created runs without duplicates", async () => {
    const user = userEvent.setup();
    const persistedRun = completedRun("run-1", "NVDA");
    const listRuns = vi.fn().mockResolvedValue([persistedRun]);
    const createRun = vi.fn().mockResolvedValue(resultFixture({ run: persistedRun }));

    render(<App createRun={createRun} listRuns={listRuns} />);

    expect(await screen.findByRole("button", { name: /NVDA completed/i })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Start research" }));

    await waitFor(() => expect(createRun).toHaveBeenCalled());
    expect(screen.getAllByRole("button", { name: /NVDA completed/i })).toHaveLength(1);
  });

  it("shows an alert when persisted runs fail to load", async () => {
    const listRuns = vi.fn().mockRejectedValue(new Error("Runs unavailable"));

    render(<App listRuns={listRuns} />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Runs unavailable");
  });

  it("loads and renders a previous run when selected from history", async () => {
    const user = userEvent.setup();
    const run = completedRun("run-2", "MSFT");
    const listRuns = vi.fn().mockResolvedValue([run]);
    let resolveSavedRun: (result: ResearchResult) => void = () => {};
    const getRun = vi.fn(
      () =>
        new Promise<ResearchResult>((resolve) => {
          resolveSavedRun = resolve;
        }),
    );

    render(<App listRuns={listRuns} getRun={getRun} />);

    await user.click(await screen.findByRole("button", { name: /MSFT completed/i }));

    expect(screen.getByRole("status")).toHaveTextContent("Loading saved run...");
    resolveSavedRun(resultFixture({ run }));
    expect(await screen.findByText("MSFT Market Snapshot")).toBeInTheDocument();
    expect(screen.getByText("MSFT call spread")).toBeInTheDocument();
    expect(getRun).toHaveBeenCalledWith("run-2");
  });

  it("shows an alert when a previous run fails to load", async () => {
    const user = userEvent.setup();
    const listRuns = vi.fn().mockResolvedValue([completedRun("run-2", "MSFT")]);
    const getRun = vi.fn().mockRejectedValue(new Error("Saved run unavailable"));

    render(<App listRuns={listRuns} getRun={getRun} />);

    await user.click(await screen.findByRole("button", { name: /MSFT completed/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Saved run unavailable");
  });

  it("shows source ids from sections, trade ideas, and uncited run sources with duplicate references counted", async () => {
    const createRun = vi.fn().mockResolvedValue(
      resultFixture({
        sectionSourceIds: ["src-shared", "src-section"],
        tradeSourceIds: ["src-shared", "src-trade"],
      }),
    );
    const listRunSources = vi.fn().mockResolvedValue([
      sourceFixture("src-shared", {
        source_type: "market",
        payload: { provider: "yfinance", price: 501.25 },
      }),
      sourceFixture("src-section", {
        source_type: "filing",
        payload: { provider: "sec", form: "10-Q" },
      }),
      sourceFixture("src-trade", {
        source_type: "options",
        payload: { provider: "yfinance", expiration: "2026-06-19" },
      }),
      sourceFixture("src-uncited"),
    ]);

    render(<App createRun={createRun} listRunSources={listRunSources} />);

    await userEvent.click(screen.getByRole("button", { name: "Start research" }));

    const sourceDrawer = await screen.findByLabelText("Source drawer");
    expect(within(sourceDrawer).getByRole("button", { name: /src-section.*SEC.*live/i })).toBeInTheDocument();
    expect(
      within(sourceDrawer).getByRole("button", { name: /src-trade.*Yahoo Finance.*live/i }),
    ).toBeInTheDocument();
    expect(
      within(sourceDrawer).getByRole("button", {
        name: /src-shared.*Yahoo Finance.*live.*2 references/i,
      }),
    ).toBeInTheDocument();
    expect(
      await within(sourceDrawer).findByRole("button", { name: /src-uncited.*fixture.*uncited/i }),
    ).toBeInTheDocument();
    expect(listRunSources).toHaveBeenCalledWith("run-1");
  });

  it("opens source details with metadata and formatted payload", async () => {
    const user = userEvent.setup();
    const createRun = vi.fn().mockResolvedValue(resultFixture({ tradeSourceIds: ["src-trade"] }));
    const getSource = vi.fn().mockResolvedValue(sourceFixture("src-trade"));

    render(<App createRun={createRun} getSource={getSource} />);

    await user.click(screen.getByRole("button", { name: "Start research" }));
    await user.click(await screen.findByRole("button", { name: /src-trade/i }));

    expect(await screen.findByText("Primary source title")).toBeInTheDocument();
    expect(screen.getByText("news")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "https://example.test/source" })).toHaveAttribute(
      "href",
      "https://example.test/source",
    );
    expect(screen.getByText("2026-06-01T12:00:00Z")).toBeInTheDocument();
    expect(screen.getByText(/"headline": "Source headline"/)).toBeInTheDocument();
    expect(getSource).toHaveBeenCalledWith("src-trade");
  });

  it("shows failed source detail errors without stale source details", async () => {
    const user = userEvent.setup();
    const createRun = vi.fn().mockResolvedValue(
      resultFixture({
        sectionSourceIds: ["src-ok"],
        tradeSourceIds: ["src-missing"],
      }),
    );
    const getSource = vi
      .fn()
      .mockResolvedValueOnce(sourceFixture("src-ok"))
      .mockRejectedValueOnce(new Error("Source not found"));

    render(<App createRun={createRun} getSource={getSource} />);

    await user.click(screen.getByRole("button", { name: "Start research" }));
    await user.click(await screen.findByRole("button", { name: /src-ok/i }));
    expect(await screen.findByText("Primary source title")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /src-missing/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Source not found");
    expect(screen.queryByText("Primary source title")).not.toBeInTheDocument();
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
