import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import App from "./App";

const result = {
  analysis_id: "test-id",
  input_type: "url",
  verdict: "lower_risk",
  risk_score: 5,
  confidence: "high",
  summary: "No strong warning signs were found.",
  signals: [
    {
      code: "HTTPS_ENABLED",
      category: "url",
      status: "safe",
      title: "HTTPS protection",
      message: "The link uses HTTPS.",
      score_delta: 0,
      evidence: "https",
      source: "local",
      critical: false,
    },
  ],
  advice: ["Verify independently."],
  limitations: ["This is a risk estimate."],
  integrations: {},
  language: "en",
};

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  localStorage.clear();
});

test("submits a seller URL and displays the verdict", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
    ok: true,
    json: async () => result,
  }));
  render(<App />);

  fireEvent.change(screen.getByLabelText("Seller or shop link"), {
    target: { value: "https://example.com" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Analyze risk" }));

  await waitFor(() => expect(screen.getByText("Lower risk")).toBeInTheDocument());
  expect(screen.getByText("HTTPS protection")).toBeInTheDocument();
});

test("switches to Hindi", () => {
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: "हिंदी" }));

  expect(screen.getByText("भुगतान से पहले विक्रेता की जाँच करें।")).toBeInTheDocument();
});