from app.config import Settings
from app.schemas import (
    AnalysisResult,
    Language,
    LinkCheckRequest,
    ScreenshotContext,
)
from app.services.screenshot_analyzer import analyze_screenshot
from app.services.url_analyzer import analyze_url


async def check_website(
    url: str,
    language: Language,
    settings: Settings,
) -> AnalysisResult:
    """Run TrustCheck's existing URL verification tool."""
    request = LinkCheckRequest(
        url=url,
        language=language,
    )

    return await analyze_url(request, settings)


async def check_screenshot(
    image_data: bytes,
    content_type: str | None,
    language: Language,
    settings: Settings,
    expected_seller_name: str | None = None,
    reference_price: float | None = None,
) -> AnalysisResult:
    """Run TrustCheck's existing screenshot verification tool."""
    context = ScreenshotContext(
        language=language,
        expected_seller_name=expected_seller_name,
        reference_price=reference_price,
        currency="INR",
    )

    return await analyze_screenshot(
        image_data,
        content_type,
        context,
        settings,
    )