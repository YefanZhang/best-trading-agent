import type { Report, ResearchRun } from "../api/client";

export type CoverageStatus = "complete" | "warning" | "limited";

const warningKey = (warning: { source: string; message: string }): string =>
  `${warning.source}\u0000${warning.message}`;

export function getUniqueSourceIds(report: Report): string[] {
  return Array.from(
    new Set([
      ...report.sections.flatMap((section) => section.source_ids),
      ...report.trade_ideas.flatMap((idea) => idea.source_ids),
    ]),
  ).filter(Boolean);
}

export function getWarningCount(run: ResearchRun, report: Report): number {
  return new Set([...run.warnings, ...report.warnings].map(warningKey)).size;
}

export function getTradeIdeaCount(report: Report): number {
  return report.trade_ideas.length;
}

export function getSectionCount(report: Report): number {
  return report.sections.length;
}

export function deriveCoverageStatus(report: Report, run: ResearchRun): CoverageStatus {
  if (getUniqueSourceIds(report).length === 0 || getSectionCount(report) === 0) {
    return "limited";
  }

  if (run.status === "completed_with_warnings" || getWarningCount(run, report) > 0) {
    return "warning";
  }

  return "complete";
}
