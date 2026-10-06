from uuid import uuid4

from app.i18n import text
from app.schemas import AnalysisResult, IntegrationStatus, Language, Signal, Verdict
'''from app.schemas import AnalysisResult, Signal, Verdict'''


def build_result(
    *,
    input_type: str,
    signals: list[Signal],
    integrations: dict[str, IntegrationStatus],
    language: Language,
) -> AnalysisResult:
    score = min(100, sum(signal.score_delta for signal in signals if signal.status == "warning"))
    critical = any(signal.critical and signal.status == "warning" for signal in signals)
    completed = sum(signal.status != "unavailable" for signal in signals)
    coverage = completed / len(signals) if signals else 0

    if critical or score >= 45:
        verdict = "high_risk"
    elif score >= 20 or completed < 3 or coverage < 0.5:
        verdict = "unclear"
    else:
        verdict = "lower_risk"

    if coverage >= 0.8:
        confidence = "high"
    elif coverage >= 0.5:
        confidence = "medium"
    else:
        confidence = "low"

    advice = [text(language, "advice.default")]
    codes = {signal.code for signal in signals if signal.status == "warning"}
    if verdict == "high_risk":
        advice.insert(0, text(language, "advice.high_risk"))
    if "PAYMENT_NAME_MISMATCH" in codes:
        advice.append(text(language, "advice.payment"))
    if {"PRESSURE_LANGUAGE", "EXTREME_PRESSURE"} & codes:
        advice.append(text(language, "advice.pressure"))

    return AnalysisResult(
        analysis_id=str(uuid4()),
        input_type=input_type,
        verdict=verdict,
        risk_score=score,
        confidence=confidence,
        summary=text(language, f"summary.{verdict}"),
        signals=signals,
        advice=list(dict.fromkeys(advice)),
        limitations=[text(language, "limitation")],
        integrations=integrations,
        language=language,
    )