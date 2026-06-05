import type { Report, ReportSection, ResearchRun } from "../api/client";

export type SectionKind = "market" | "fundamentals" | "news" | "options" | "risk" | "general";

export function deriveSectionKind(section: ReportSection): SectionKind {
  const title = section.title.toLowerCase();

  if (title.includes("market") || title.includes("price") || title.includes("snapshot")) {
    return "market";
  }

  if (
    title.includes("revenue") ||
    title.includes("earnings") ||
    title.includes("margin") ||
    title.includes("valuation")
  ) {
    return "fundamentals";
  }

  if (title.includes("news") || title.includes("catalyst")) {
    return "news";
  }

  if (title.includes("option") || title.includes("iv") || title.includes("volatility")) {
    return "options";
  }

  if (title.includes("risk") || title.includes("downside") || title.includes("warning")) {
    return "risk";
  }

  return "general";
}

export type CoverageStatus = "complete" | "warning" | "limited";

export function getUniqueSourceIds(report: Report): string[] {
  return Array.from(
    new Set([
      ...report.sections.flatMap((section) => section.source_ids),
      ...report.trade_ideas.flatMap((idea) => idea.source_ids),
    ]),
  );
}

export function getWarningCount(run: ResearchRun, report: Report): number {
  return run.warnings.length + report.warnings.length;
}

export function getTradeIdeaCount(report: Report): number {
  return report.trade_ideas.length;
}

export function getSectionCount(report: Report): number {
  return report.sections.length;
}

export function deriveCoverageStatus(report: Report, run: ResearchRun): CoverageStatus {
  if (getUniqueSourceIds(report).length === 0 || getSectionCount(report) === 0 || getTradeIdeaCount(report) === 0) {
    return "limited";
  }

  if (run.status === "failed" || run.status === "pending" || run.status === "running") {
    return "limited";
  }

  if (run.status === "completed_with_warnings" || getWarningCount(run, report) > 0) {
    return "warning";
  }

  return "complete";
}
