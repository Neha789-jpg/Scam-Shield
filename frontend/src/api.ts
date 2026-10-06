import type {
  AgentResult,
  AnalysisResult,
  BusinessRequest,
  Language,
  ScreenshotCheckInput,
  UrlCheckInput,
} from "./types";

async function parseResponse(response: Response): Promise<AnalysisResult> {
  if (response.ok) {
    return response.json() as Promise<AnalysisResult>;
  }

  const body = (await response.json().catch(() => null)) as { detail?: string } | null;
  throw new Error(body?.detail ?? "TrustCheck could not complete the request.");
}

export async function checkUrl(input: UrlCheckInput, language: Language): Promise<AnalysisResult> {
  const response = await fetch("/api/check/url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url: input.url,
      language,
      claimed_brand: input.claimedBrand || null,
    }),
  });
  return parseResponse(response);
}

export async function checkScreenshot(
  input: ScreenshotCheckInput,
  language: Language,
): Promise<AnalysisResult> {
  const data = new FormData();
  data.append("file", input.file);
  data.append("language", language);
  if (input.expectedSellerName) data.append("expected_seller_name", input.expectedSellerName);
  if (input.referencePrice) data.append("reference_price", input.referencePrice);
  data.append("currency", "INR");

  const response = await fetch("/api/check/screenshot", { method: "POST", body: data });
  return parseResponse(response);
}

export async function runAgent(
  request: BusinessRequest,
  file?: File,
): Promise<AgentResult> {
  const data = new FormData();

  data.append("request", JSON.stringify(request));

  if (file) {
    data.append("file", file);
  }

  const response = await fetch("/api/agent/run", {
    method: "POST",
    body: data,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;

    throw new Error(
      body?.detail ?? "TrustCheck Agent could not complete the request.",
    );
  }

  return response.json() as Promise<AgentResult>;
}