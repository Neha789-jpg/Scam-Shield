import { useEffect, useState } from "react";

import { runAgent } from "./api";
import { CheckForm } from "./components/CheckForm";
import { VerdictCard } from "./components/VerdictCard";
import { t } from "./i18n";
import type { AgentResult, BusinessRequest, Language } from "./types";

function App() {
  const [language, setLanguage] = useState<Language>(() =>
    localStorage.getItem("trustcheck-language") === "hi" ? "hi" : "en",
  );

  const [result, setResult] = useState<AgentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    localStorage.setItem("trustcheck-language", language);
  }, [language]);

  async function submitRequest(request: BusinessRequest, file?: File) {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const agentResult = await runAgent(request, file);
      setResult(agentResult);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "TrustCheck Agent could not complete the request.",
      );
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setError("");
  }

  return (
    <main>
      <nav className="topbar" aria-label="Main navigation">
        <a className="brand" href="#top" aria-label="TrustCheck home">
          <span className="brand-mark">T</span>
          TrustCheck
        </a>

        <div className="language-switch" aria-label="Language">
          <button
            className={language === "en" ? "selected" : ""}
            onClick={() => setLanguage("en")}
          >
            EN
          </button>

          <button
            className={language === "hi" ? "selected" : ""}
            onClick={() => setLanguage("hi")}
          >
            हिंदी
          </button>
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">AI BUSINESS OPERATIONS AGENT</p>

          <h1>
            TrustCheck
            <br />
            Agent
          </h1>

          <p className="hero-subtitle">
            An AI agent that investigates business requests, verifies
            potentially risky evidence, and recommends the next action.
          </p>

          <div className="trust-points" aria-label="Product principles">
            <span>Evidence first</span>
            <span>Autonomous verification</span>
            <span>Human approval for critical actions</span>
          </div>
        </div>

        {!result ? (
          <CheckForm
            language={language}
            loading={loading}
            onSubmit={submitRequest}
          />
        ) : (
          <VerdictCard
            result={result}
            language={language}
            onReset={reset}
          />
        )}

        {error && (
          <p className="global-error" role="alert">
            {error}
          </p>
        )}
      </section>

      <section className="how-it-works">
        <p className="eyebrow">REQUEST → INVESTIGATE → DECIDE</p>

        <div className="steps">
          <article>
            <strong>01</strong>
            <h2>Business Request</h2>
            <p>
              Submit a vendor, partnership, customer, or external business
              request with the available evidence.
            </p>
          </article>

          <article>
            <strong>02</strong>
            <h2>Agent Investigation</h2>
            <p>
              The agent identifies relevant evidence and chooses the
              verification tools needed to investigate the request.
            </p>
          </article>

          <article>
            <strong>03</strong>
            <h2>Decision & Action</h2>
            <p>
              TrustCheck combines the evidence and recommends whether the
              request can proceed or requires human approval.
            </p>
          </article>
        </div>
      </section>

      <footer>
        TrustCheck estimates risk from available evidence. It does not
        guarantee that a business or request is legitimate.
      </footer>
    </main>
  );
}

export default App;