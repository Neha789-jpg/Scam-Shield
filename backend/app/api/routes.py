from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.config import Settings, get_settings
from app.schemas import AnalysisResult, Capabilities, Language, LinkCheckRequest, ScreenshotContext

from app.schemas import (
    AgentResult,
    AnalysisResult,
    BusinessRequest,
    Capabilities,
    Language,
    LinkCheckRequest,
    ScreenshotContext,
)

from app.agent.agent import run_agent

from app.services.screenshot_analyzer import ImageValidationError, analyze_screenshot
from app.services.url_analyzer import UnsafeUrlError, analyze_url

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "trustcheck-api"}


@router.get("/capabilities", response_model=Capabilities)
def capabilities(settings: Annotated[Settings, Depends(get_settings)]) -> Capabilities:
    return Capabilities(
        safe_browsing=bool(settings.google_safe_browsing_api_key),
        gemini_vision=bool(settings.gemini_api_key),
        domain_registration=settings.rdap_enabled,
        max_image_bytes=settings.max_image_bytes,
        languages=["en", "hi"],
    )


@router.post("/check/url", response_model=AnalysisResult)
async def check_url(
    request: LinkCheckRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AnalysisResult:
    try:
        return await analyze_url(request, settings)
    except UnsafeUrlError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/check/screenshot", response_model=AnalysisResult)
async def check_screenshot(
    settings: Annotated[Settings, Depends(get_settings)],
    file: Annotated[UploadFile, File()],
    language: Annotated[Language, Form()] = "en",
    expected_seller_name: Annotated[str | None, Form(max_length=100)] = None,
    reference_price: Annotated[float | None, Form(gt=0)] = None,
    currency: Annotated[str, Form(min_length=3, max_length=3)] = "INR",
) -> AnalysisResult:
    data = await file.read(settings.max_image_bytes + 1)
    context = ScreenshotContext(
        language=language,
        expected_seller_name=expected_seller_name,
        reference_price=reference_price,
        currency=currency,
    )
    try:
        return await analyze_screenshot(data, file.content_type, context, settings)
    except ImageValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        await file.close()

@router.post("/agent/run", response_model=AgentResult)
async def run_business_agent(
    settings: Annotated[Settings, Depends(get_settings)],
    request: Annotated[str, Form()],
    file: Annotated[UploadFile | None, File()] = None,
) -> AgentResult:
    try:
        business_request = BusinessRequest.model_validate_json(request)

        screenshot_data = None
        screenshot_content_type = None

        if file:
            screenshot_data = await file.read(settings.max_image_bytes + 1)
            screenshot_content_type = file.content_type

        return await run_agent(
            business_request,
            settings,
            screenshot_data=screenshot_data,
            screenshot_content_type=screenshot_content_type,
        )

    finally:
        if file:
            await file.close()