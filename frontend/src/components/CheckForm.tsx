import { useState } from "react";
import type { Language } from "../types";

interface CheckFormProps {
  language: Language;
  loading: boolean;
  onSubmit: (
    request: {
      request_type: string;
      company_name: string;
      website: string | null;
      message: string;
      language: Language;
    },
    file?: File,
  ) => void;
}

export function CheckForm({
  language,
  loading,
  onSubmit,
}: CheckFormProps) {
  const [request, setRequest] = useState("");
  const [file, setFile] = useState<File | undefined>();

  function investigateRequest() {
    if (!request.trim()) return;

    onSubmit(
      {
        request_type: "business_request",
        company_name: "Unknown",
        website: null,
        message: request.trim(),
        language,
      },
      file,
    );
  }

  return (
    <section className="incoming-request-card">
      <div className="request-card-header">
        <div>
          <p className="eyebrow">INCOMING BUSINESS REQUEST</p>
          <h2>Request received by the business</h2>
        </div>

        <span className="request-status">NEW</span>
      </div>

      <div className="request-input-section">
        <label htmlFor="business-request">
          Paste the request you received
        </label>

        <textarea
          id="business-request"
          value={request}
          onChange={(event) => setRequest(event.target.value)}
          placeholder={`Example:

Acme Technologies has requested to become an approved vendor for our organization. They have provided their website https://example.com and asked us to verify their business details before onboarding.

Please review this request and determine whether it is safe to proceed.`}
          rows={9}
        />
      </div>

      <div className="request-evidence">
        <div>
          <span>Supporting evidence</span>

          <label className="file-upload">
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp"
              onChange={(event) =>
                setFile(event.target.files?.[0] ?? undefined)
              }
            />

            {file ? `📎 ${file.name}` : "📎 Attach screenshot / evidence"}
          </label>
        </div>
      </div>

      <div className="agent-handoff">
        <span>What happens next</span>

        <strong>
          TrustCheck Agent will understand the request, identify relevant
          evidence, select verification tools, and recommend what should
          happen next.
        </strong>
      </div>

      <button
        className="execute-button"
        type="button"
        disabled={loading || !request.trim()}
        onClick={investigateRequest}
      >
        {loading
          ? "Agent is investigating..."
          : "Investigate Request →"}
      </button>
    </section>
  );
}