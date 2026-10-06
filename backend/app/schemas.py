from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field

Language = Literal["en", "hi"]
Verdict = Literal["lower_risk", "unclear", "high_risk"]
SignalStatus = Literal["safe", "warning", "info", "unavailable"]
Confidence = Literal["low", "medium", "high"]
IntegrationStatus = Literal["completed", "not_configured", "unavailable", "not_applicable"]


class LinkCheckRequest(BaseModel):
    url: AnyHttpUrl
    language: Language = "en"
    claimed_brand: str | None = Field(default=None, max_length=100)


class ScreenshotContext(BaseModel):
    language: Language = "en"
    expected_seller_name: str | None = Field(default=None, max_length=100)
    reference_price: float | None = Field(default=None, gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)


class Signal(BaseModel):
    code: str
    category: str
    status: SignalStatus
    title: str
    message: str
    score_delta: int = Field(ge=0, le=100)
    evidence: str | None = None
    source: str
    critical: bool = False


class AnalysisResult(BaseModel):
    analysis_id: str
    input_type: Literal["url", "screenshot"]
    verdict: Verdict
    risk_score: int = Field(ge=0, le=100)
    confidence: Confidence
    summary: str
    signals: list[Signal]
    advice: list[str]
    limitations: list[str]
    integrations: dict[str, IntegrationStatus]
    language: Language


class Capabilities(BaseModel):
    safe_browsing: bool
    gemini_vision: bool
    domain_registration: bool
    max_image_bytes: int
    languages: list[Language]

class ExtractionDetails(BaseModel):
    extracted_handle: str | None = None
    extracted_upi_id: str | None = None
    upi_handle_match: bool = False

class BusinessRequest(BaseModel):
    request_type: str = "business_request"
    company_name: str | None = None
    website: AnyHttpUrl | None = None
    message: str = Field(min_length=1, max_length=2000)
    language: Language = "en"

class AgentResult(BaseModel):
    agent_id: str
    request_type: str
    company_name: str

    analyses: list[AnalysisResult]

    overall_verdict: Verdict
    risk_score: int
    recommendation: str

    approval_required: bool
    action_status: str

    activity: list[str]

