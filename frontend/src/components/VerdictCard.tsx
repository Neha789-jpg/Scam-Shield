import type { AgentResult, Language } from "../types";

interface VerdictCardProps {
  result: AgentResult;
  language: Language;
  onReset: () => void;
}

const verdictLabel = {
  en: {
    lower_risk: "Lower risk",
    unclear: "Unclear",
    high_risk: "High risk",
  },
  hi: {
    lower_risk: "कम जोखिम",
    unclear: "अस्पष्ट",
    high_risk: "अधिक जोखिम",
  },
};

export function VerdictCard({
  result,
  language,
  onReset,
}: VerdictCardProps) {
  const isApprovalRequired = result.approval_required;

  return (
    <section
      className={`result-card verdict-${result.overall_verdict}`}
      aria-live="polite"
    >
      <div className="verdict-header">
        <div>
          <p className="eyebrow">TRUSTCHECK AGENT</p>

          <h2>{verdictLabel[language][result.overall_verdict]}</h2>

          <p>
            {result.company_name}
          </p>
        </div>

        <div
          className="score-ring"
          aria-label={`Risk score: ${result.risk_score}`}
        >
          <strong>{result.risk_score}</strong>
          <span>/100</span>
        </div>
      </div>

      <div className="agent-recommendation">
        <p className="eyebrow">AGENT RECOMMENDATION</p>
        <p>{result.recommendation}</p>
      </div>

      <div className="agent-activity">
        <h3>Agent activity</h3>

        <ol>
          {result.activity.map((step, index) => (
            <li key={`${step}-${index}`}>
              <span className="activity-number">
                {String(index + 1).padStart(2, "0")}
              </span>

              <span>{step}</span>
            </li>
          ))}
        </ol>
      </div>

      {result.analyses.length > 0 && (
        <div className="agent-analysis">
          <h3>Verification results</h3>

          {result.analyses.map((analysis) => (
            <div className="analysis-summary" key={analysis.analysis_id}>
              <div>
                <strong>
                  {analysis.input_type === "url"
                    ? "Website verification"
                    : "Visual verification"}
                </strong>

                <p>{analysis.summary}</p>
              </div>

              <span>
                {analysis.risk_score}/100
              </span>
            </div>
          ))}
        </div>
      )}

      <div
        className={`approval-box ${
          isApprovalRequired ? "approval-required" : "approval-cleared"
        }`}
      >
        <strong>
          {isApprovalRequired
            ? "Human approval required"
            : "Ready to proceed"}
        </strong>

        <p>
          {isApprovalRequired
            ? "The agent has paused this request because it should not proceed automatically."
            : "The agent found no major risk indicators requiring human approval."}
        </p>
      </div>

      <button
        className="secondary-button"
        type="button"
        onClick={onReset}
      >
        Start another request
      </button>
    </section>
  );
}