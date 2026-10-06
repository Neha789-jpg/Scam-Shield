export type Language = "en" | "hi";
export type InputMode = "url" | "screenshot";
export type Verdict = "lower_risk" | "unclear" | "high_risk";
export type SignalStatus = "safe" | "warning" | "info" | "unavailable";

export interface Signal {
  code: string;
  category: string;
  status: SignalStatus;
  title: string;
  message: string;
  score_delta: number;
  evidence: string | null;
  source: string;
  critical: boolean;
}

export interface AnalysisResult {
  analysis_id: string;
  input_type: InputMode;
  verdict: Verdict;
  risk_score: number;
  confidence: "low" | "medium" | "high";
  summary: string;
  signals: Signal[];
  advice: string[];
  limitations: string[];
  integrations: Record<string, string>;
  language: Language;
}

export interface UrlCheckInput {
  url: string;
  claimedBrand: string;
}

export interface ScreenshotCheckInput {
  file: File;
  expectedSellerName: string;
  referencePrice: string;
}

export interface BusinessRequest {
  request_type: string;
  company_name: string;
  website: string;
  message: string;
  language: Language;
}

export interface AgentAnalysis {
  analysis_id: string;
  input_type: InputMode;
  verdict: Verdict;
  risk_score: number;
  confidence: "low" | "medium" | "high";
  summary: string;
  signals: Signal[];
  advice: string[];
  limitations: string[];
  integrations: Record<string, string>;
  language: Language;
}

export interface AgentResult {
  agent_id: string;
  request_type: string;
  company_name: string;
  analyses: AgentAnalysis[];
  overall_verdict: Verdict;
  risk_score: number;
  recommendation: string;
  approval_required: boolean;
  action_status: string;
  activity: string[];
}