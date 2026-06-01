import { Play } from "lucide-react";

const panels = ["Ticker command", "Market snapshot", "Catalysts", "Generated memo"];

export function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Workbench navigation">
        <div className="brand">best-trading-agent</div>
        <nav>
          <a href="#research">Research</a>
          <a href="#watchlist">Watchlist</a>
          <a href="#sources">Sources</a>
          <a href="#settings">Settings</a>
        </nav>
      </aside>
      <section className="workspace" id="research">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">US equities and options</p>
            <h1>Research Workbench</h1>
          </div>
          <button className="primary-button" type="button">
            <Play size={17} strokeWidth={2.2} aria-hidden="true" />
            Start research
          </button>
        </header>
        <section className="panel-grid" aria-label="Research panels">
          {panels.map((panel) => (
            <div className={`panel${panel === "Generated memo" ? " wide" : ""}`} key={panel}>
              {panel}
            </div>
          ))}
        </section>
      </section>
    </main>
  );
}
