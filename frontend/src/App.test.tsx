import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the research workbench shell", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Research Workbench" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start research" })).toBeInTheDocument();
  });
});
