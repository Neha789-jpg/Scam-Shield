from app.schemas import Signal
from app.services.scoring import build_result


def make_signal(points: int, status: str = "warning", critical: bool = False) -> Signal:
    return Signal(
        code="TEST",
        category="test",
        status=status,
        title="Test",
        message="Test signal",
        score_delta=points,
        source="test",
        critical=critical,
    )


def result_for(points: int):
    return build_result(
        input_type="url",
        signals=[make_signal(points), make_signal(0, "safe"), make_signal(0, "safe")],
        integrations={
            "safe_browsing": "completed",
            "domain_registration": "completed",
            "vision": "not_applicable",
        },
        language="en",
    )


def test_scoring_boundaries() -> None:
    assert result_for(19).verdict == "lower_risk"
    assert result_for(20).verdict == "unclear"
    assert result_for(44).verdict == "unclear"
    assert result_for(45).verdict == "high_risk"


def test_critical_signal_overrides_score() -> None:
    result = build_result(
        input_type="url",
        signals=[make_signal(1, critical=True), make_signal(0, "safe"), make_signal(0, "safe")],
        integrations={
            "safe_browsing": "completed",
            "domain_registration": "completed",
            "vision": "not_applicable",
        },
        language="en",
    )

    assert result.verdict == "high_risk"