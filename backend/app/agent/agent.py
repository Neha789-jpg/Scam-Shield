import re
from uuid import uuid4

from app.config import Settings
from app.schemas import AgentResult, BusinessRequest, AnalysisResult
from app.agent.tools import check_screenshot, check_website


URL_PATTERN = re.compile(r"https?://[^\s<>\"]+")


def extract_request_details(request: BusinessRequest):
    message = request.message

    # Extract website from the raw request
    website = str(request.website) if request.website else None

    if not website:
        match = URL_PATTERN.search(message)
        if match:
            website = match.group(0).rstrip(".,)")


    # Extract company name from common business-request wording
    company_name = request.company_name

    if not company_name:
        patterns = [
            r"our company,\s*([A-Z][A-Za-z0-9&.,' -]{2,80}?)(?:\s+provides|\s+is|\s+has|\.)",
            r"company name\s*[:\-]\s*([A-Za-z0-9&.,' -]{2,80})",
            r"(?:company|vendor|supplier)\s*[:\-]\s*([A-Za-z0-9&.,' -]{2,80})",
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                break

    if not company_name:
        company_name = "Unknown entity"

    # Infer the business request type
    text = message.lower()

    if any(word in text for word in ["vendor", "supplier", "onboarding"]):
        request_type = "vendor_approval"
    elif any(word in text for word in ["payment", "bank account", "account details"]):
        request_type = "payment_change"
    elif any(word in text for word in ["partnership", "collaboration", "sponsor"]):
        request_type = "partnership"
    else:
        request_type = request.request_type

    return company_name, website, request_type


async def run_agent(
    request: BusinessRequest,
    settings: Settings,
    screenshot_data: bytes | None = None,
    screenshot_content_type: str | None = None,
) -> AgentResult:

    activity: list[str] = [
        "Business request received",
        "Understanding request",
    ]

    analyses: list[AnalysisResult] = []

    # ---------------------------------------------------------
    # STEP 1 — UNDERSTAND THE RAW REQUEST
    # ---------------------------------------------------------

    company_name, website, request_type = extract_request_details(request)

    activity.append(f"Business entity identified: {company_name}")

    if website:
        activity.append("Website evidence detected")
    else:
        activity.append("No website detected in request")

    # ---------------------------------------------------------
    # STEP 2 — SELECT RELEVANT TOOLS
    # ---------------------------------------------------------

    if website:
        activity.append("Selecting website verification tool")
        activity.append("Running website verification")

        website_result = await check_website(
            website,
            request.language,
            settings,
        )

        analyses.append(website_result)

        activity.append("Website verification completed")

    if screenshot_data:
        activity.append("Supporting visual evidence detected")
        activity.append("Selecting visual verification tool")
        activity.append("Running visual verification")

        screenshot_result = await check_screenshot(
            screenshot_data,
            screenshot_content_type,
            request.language,
            settings,
            expected_seller_name=company_name,
        )

        analyses.append(screenshot_result)

        activity.append("Visual verification completed")

    # ---------------------------------------------------------
    # STEP 3 — REASON OVER THE EVIDENCE
    # ---------------------------------------------------------

    activity.append("Evaluating combined evidence")

    if not analyses:

        overall_verdict = "unclear"
        risk_score = 0

        recommendation = (
            "Insufficient evidence to safely evaluate this business request."
        )

        approval_required = True

    else:

        risk_score = max(
            result.risk_score
            for result in analyses
        )

        if any(
            result.verdict == "high_risk"
            for result in analyses
        ):
            overall_verdict = "high_risk"

        elif any(
            result.verdict == "unclear"
            for result in analyses
        ):
            overall_verdict = "unclear"

        else:
            overall_verdict = "lower_risk"

        if overall_verdict == "high_risk":

            recommendation = (
                "Do not approve this request without additional verification."
            )

            approval_required = True

        elif overall_verdict == "unclear":

            recommendation = (
                "Additional verification is recommended before approval."
            )

            approval_required = True

        else:

            recommendation = (
                "No major risk indicators were detected. "
                "The request can proceed."
            )

            approval_required = False

    # ---------------------------------------------------------
    # STEP 4 — BUSINESS ACTION
    # ---------------------------------------------------------

    if approval_required:

        action_status = "approval_required"
        activity.append("Human approval required")

    else:

        action_status = "ready_to_execute"
        activity.append("Request cleared for execution")

    activity.append("Agent decision completed")

    return AgentResult(
        agent_id=str(uuid4()),
        request_type=request_type,
        company_name=company_name,
        analyses=analyses,
        overall_verdict=overall_verdict,
        risk_score=risk_score,
        recommendation=recommendation,
        approval_required=approval_required,
        action_status=action_status,
        activity=activity,
    )