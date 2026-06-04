import type { ReportSection } from "../api/client";

export type SectionKind =
  | "market"
  | "fundamentals"
  | "news"
  | "options"
  | "risk"
  | "general";

export function deriveSectionKind(section: ReportSection): SectionKind {
  const title = section.title.toLowerCase();

  if (
    title.includes("market") ||
    title.includes("price") ||
    title.includes("snapshot")
  ) {
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
  if (
    title.includes("option") ||
    title.includes("iv") ||
    title.includes("volatility")
  ) {
    return "options";
  }
  if (
    title.includes("risk") ||
    title.includes("downside") ||
    title.includes("warning")
  ) {
    return "risk";
  }
  return "general";
}
