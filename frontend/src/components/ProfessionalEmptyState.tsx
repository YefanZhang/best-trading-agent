const workflowSteps = ["Ticker input", "Market data", "News/filings/options", "Risk review", "Trade plan"];
const coverageItems = ["Market", "SEC filings", "News", "Options"];
const agentRoles = [
  "Market analyst",
  "Fundamentals analyst",
  "News analyst",
  "Options analyst",
  "Risk manager",
];
const expectedOutputs = [
  "Recommendation",
  "Confidence",
  "Evidence memo",
  "Trade setup",
  "Risk notes",
  "Source audit",
];

export function ProfessionalEmptyState() {
  return (
    <section className="empty-state-grid" aria-label="Research empty state">
      <article className="empty-state-card workflow-card">
        <p className="empty-state-kicker">Start here</p>
        <h2>Research workflow</h2>
        <ol className="workflow-list">
          {workflowSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </article>

      <article className="empty-state-card">
        <p className="empty-state-kicker">Coverage monitor</p>
        <h2>Data coverage</h2>
        <div className="coverage-list" aria-label="Data coverage statuses">
          {coverageItems.map((item) => (
            <div className="coverage-pill" key={item}>
              <span>{item}</span>
              <span className="coverage-status">Pending</span>
            </div>
          ))}
        </div>
      </article>

      <article className="empty-state-card">
        <p className="empty-state-kicker">Specialist team</p>
        <h2>Agent roles</h2>
        <ul className="empty-state-list">
          {agentRoles.map((role) => (
            <li key={role}>{role}</li>
          ))}
        </ul>
      </article>

      <article className="empty-state-card">
        <p className="empty-state-kicker">Report package</p>
        <h2>Expected outputs</h2>
        <ul className="output-list">
          {expectedOutputs.map((output) => (
            <li key={output}>{output}</li>
          ))}
        </ul>
      </article>
    </section>
  );
}
