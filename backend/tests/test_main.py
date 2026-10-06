from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings, get_settings
from app.main import app


def override_settings() -> Settings:
    return Settings(
        google_safe_browsing_api_key=None,
        gemini_api_key=None,
        rdap_enabled=False,
    )


app.dependency_overrides[get_settings] = override_settings
client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "trustcheck-api",
    }
    assert response.json() == {"status": "ok", "service": "trustcheck-api"}


def test_capabilities_report_optional_services() -> None:
    response = client.get("/api/capabilities")

    assert response.status_code == 200
    assert response.json()["safe_browsing"] is False
    assert response.json()["gemini_vision"] is False


def test_url_check_returns_explainable_result() -> None:
    response = client.post(
        "/api/check/url",
        json={"url": "https://example.com", "language": "en"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["input_type"] == "url"
    assert result["verdict"] in {"lower_risk", "unclear", "high_risk"}
    assert len(result["signals"]) >= 6
    assert result["limitations"]


def test_url_check_rejects_ip_addresses() -> None:
    response = client.post("/api/check/url", json={"url": "http://127.0.0.1"})

    assert response.status_code == 400


def test_valid_screenshot_is_unclear_without_gemini() -> None:
    image = Image.new("RGB", (20, 20), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    response = client.post(
        "/api/check/screenshot",
        files={"file": ("seller.png", buffer.getvalue(), "image/png")},
        data={"language": "en"},
    )

    assert response.status_code == 200
    assert response.json()["verdict"] == "unclear"
    assert response.json()["integrations"]["vision"] == "not_configured"


def test_fake_image_is_rejected() -> None:
    response = client.post(
        "/api/check/screenshot",
        files={"file": ("seller.png", b"not-an-image", "image/png")},
    )

    assert response.status_code == 400