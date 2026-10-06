import httpx

from app.config import Settings


async def check_safe_browsing(url: str, settings: Settings) -> bool | None:
    if not settings.google_safe_browsing_api_key:
        return None

    endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    payload = {
        "client": {"clientId": "trustcheck", "clientVersion": "0.1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                endpoint,
                params={"key": settings.google_safe_browsing_api_key},
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPError:
        return None

    return bool(response.json().get("matches"))