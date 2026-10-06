from datetime import datetime, timezone
from urllib.parse import quote

import httpx

from app.config import Settings


async def get_domain_age_days(domain: str, settings: Settings) -> int | None:
    if not settings.rdap_enabled:
        return None

    url = f"https://rdap.org/domain/{quote(domain, safe='')}"
    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = await client.get(url, headers={"Accept": "application/rdap+json"})
            response.raise_for_status()
    except httpx.HTTPError:
        return None

    for event in response.json().get("events", []):
        if event.get("eventAction") == "registration" and event.get("eventDate"):
            try:
                registered_at = datetime.fromisoformat(event["eventDate"].replace("Z", "+00:00"))
            except ValueError:
                return None
            return max(0, (datetime.now(timezone.utc) - registered_at).days)

    return None