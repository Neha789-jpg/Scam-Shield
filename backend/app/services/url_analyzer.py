import ipaddress
import re
from urllib.parse import urlsplit

import tldextract
from rapidfuzz import fuzz

from app.config import Settings
from app.i18n import choose
from app.schemas import Language, LinkCheckRequest, Signal
from app.services.domain_registration import get_domain_age_days
from app.services.safe_browsing import check_safe_browsing
from app.services.scoring import build_result

EXTRACT_DOMAIN = tldextract.TLDExtract(suffix_list_urls=())
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "cutt.ly", "rb.gy", "is.gd", "ow.ly"}
SUSPICIOUS_TERMS = {"verify", "secure", "support", "payment", "offer", "deal", "login", "gift"}

class UnsafeUrlError(ValueError):
    pass


def _signal(
    code: str,
    status: str,
    score: int,
    english_title: str,
    hindi_title: str,
    english_message: str,
    hindi_message: str,
    language: Language,
    *,
    evidence: str | None = None,
    source: str = "local",
    critical: bool = False,
) -> Signal:
    return Signal(
        code=code,
        category="url",
        status=status,
        title=choose(language, english_title, hindi_title),
        message=choose(language, english_message, hindi_message),
        score_delta=score,
        evidence=evidence,
        source=source,
        critical=critical,
    )

def validate_and_extract(url: str) -> tuple[str, str, str]:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeUrlError("Only HTTP and HTTPS URLs are supported.")
    if parsed.username or parsed.password:
        raise UnsafeUrlError("URLs containing usernames or passwords are not accepted.")
    if not parsed.hostname:
        raise UnsafeUrlError("The URL must contain a hostname.")
    if parsed.port not in {None, 80, 443}:
        raise UnsafeUrlError("Only standard web ports 80 and 443 are supported.")

    hostname = parsed.hostname.rstrip(".").lower().encode("idna").decode("ascii")
    if hostname == "localhost" or hostname.endswith((".localhost", ".local", ".internal")):
        raise UnsafeUrlError("Local or internal addresses are not accepted.")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None:
        raise UnsafeUrlError("Direct IP-address URLs are not accepted.")

    extracted = EXTRACT_DOMAIN(hostname)
    if not extracted.domain or not extracted.suffix:
        raise UnsafeUrlError("The URL must use a public domain name.")

    registered_domain = f"{extracted.domain}.{extracted.suffix}"
    return hostname, registered_domain, extracted.domain

def local_url_signals(
    url: str,
    hostname: str,
    registered_domain: str,
    domain_label: str,
    claimed_brand: str | None,
    language: Language,
) -> list[Signal]:
    parsed = urlsplit(url)
    signals: list[Signal] = []

    secure = parsed.scheme == "https"
    signals.append(
        _signal(
            "HTTPS_ENABLED",
            "safe" if secure else "warning",
            0 if secure else 15,
            "HTTPS protection",
            "HTTPS सुरक्षा",
            "The link uses encrypted HTTPS." if secure else "The link does not use HTTPS.",
            "लिंक एन्क्रिप्टेड HTTPS का उपयोग करता है।" if secure else "लिंक HTTPS का उपयोग नहीं करता है।",
            
            language,
            evidence=parsed.scheme,
        )
    )

    is_shortener = registered_domain in SHORTENERS
    signals.append(
        _signal(
            "URL_SHORTENER",
            "warning" if is_shortener else "safe",
            12 if is_shortener else 0,
            "Shortened link",
            "छोटा किया गया लिंक",
            "The destination is hidden behind a link shortener." if is_shortener else "No common link shortener was detected.",
            "लिंक शॉर्टनर असली गंतव्य छिपाता है।" if is_shortener else "कोई सामान्य लिंक शॉर्टनर नहीं मिला।",
            language,
            evidence=registered_domain,
        )
    )

    uses_punycode = "xn--" in hostname
    signals.append(
        _signal(
            "PUNYCODE_HOST",
            "warning" if uses_punycode else "safe",
            15 if uses_punycode else 0,
            "Encoded domain name",
            "एन्कोड किया गया डोमेन",
            "The hostname uses punycode and should be checked carefully." if uses_punycode else "The hostname does not use punycode.",
            "होस्टनाम punycode का उपयोग करता है; इसे ध्यान से जाँचें।" if uses_punycode else "होस्टनाम punycode का उपयोग नहीं करता है।",
            language,
            evidence=hostname,
        )
    )

    subdomain_count = max(0, len(hostname.split(".")) - len(registered_domain.split(".")))
    excessive_subdomains = subdomain_count > 2
    signals.append(
        _signal(
            "EXCESSIVE_SUBDOMAINS",
            "warning" if excessive_subdomains else "safe",
            8 if excessive_subdomains else 0,
            "Domain structure",
            "डोमेन संरचना",
            "The link uses an unusually deep subdomain structure." if excessive_subdomains else "The domain structure looks ordinary.",
            "लिंक में असामान्य रूप से कई सबडोमेन हैं।" if excessive_subdomains else "डोमेन संरचना सामान्य दिखती है।",
            language,
            evidence=f"subdomains={subdomain_count}",
        )
    )

    suspicious = sorted(term for term in SUSPICIOUS_TERMS if term in re.split(r"[^a-z0-9]+", hostname))
    signals.append(
        _signal(
            "SUSPICIOUS_DOMAIN_WORDS",
            "warning" if suspicious else "safe",
            8 if suspicious else 0,
            "Domain wording",
            "डोमेन के शब्द",
            f"Sensitive words appear in the hostname: {', '.join(suspicious)}." if suspicious else "No common pressure or impersonation words appear in the hostname.",
            f"होस्टनाम में संवेदनशील शब्द हैं: {', '.join(suspicious)}।" if suspicious else "होस्टनाम में सामान्य दबाव या नकली पहचान वाले शब्द नहीं मिले।",
            language,
            evidence=",".join(suspicious) if suspicious else None,
        )
    )

    if claimed_brand:
        brand = re.sub(r"[^a-z0-9]", "", claimed_brand.lower())
        domain = re.sub(r"[^a-z0-9]", "", domain_label.lower())
        similarity = fuzz.ratio(brand, domain) if brand and domain else 0
        looks_alike = brand != domain and similarity >= 70
        signals.append(
            _signal(
                "BRAND_LOOKALIKE",
                "warning" if looks_alike else "safe",
                25 if looks_alike else 0,
                "Claimed brand comparison",
                "दावा किए गए ब्रांड की तुलना",
                "The domain resembles the claimed brand but is not an exact match." if looks_alike else "No close misspelling of the claimed brand was detected.",
                "डोमेन दावा किए गए ब्रांड जैसा है, लेकिन पूरी तरह समान नहीं है।" if looks_alike else "दावा किए गए ब्रांड की मिलती-जुलती गलत वर्तनी नहीं मिली।",
                language,
                evidence=f"similarity={similarity:.0f}%",
            )
        )

    return signals

async def analyze_url(request: LinkCheckRequest, settings: Settings):
    url = str(request.url)
    hostname, registered_domain, domain_label = validate_and_extract(url)
    signals = local_url_signals(
        url,
        hostname,
        registered_domain,
        domain_label,
        request.claimed_brand,
        request.language,
    )

    age_days = await get_domain_age_days(registered_domain, settings)
    if age_days is None:
        signals.append(
            _signal(
                "DOMAIN_AGE",
                "unavailable",
                0,
                "Domain age",
                "डोमेन की आयु",
                "Registration age could not be checked.",
                "पंजीकरण की आयु जाँची नहीं जा सकी।",
                request.language,
                source="rdap",
            )
        )
        domain_status = "unavailable"
    else:
        points = 25 if age_days < 30 else 15 if age_days < 180 else 8 if age_days < 365 else 0
        status = "warning" if points else "safe"
        signals.append(
            _signal(
                "DOMAIN_AGE",
                status,
                points,
                "Domain age",
                "डोमेन की आयु",
                f"The domain was registered about {age_days} days ago.",
                f"डोमेन लगभग {age_days} दिन पहले पंजीकृत हुआ था।",
                request.language,
                evidence=f"age_days={age_days}",
                source="rdap",
            )
        )
        domain_status = "completed"

    safe_browsing = await check_safe_browsing(url, settings)
    if safe_browsing is None:
        configured = bool(settings.google_safe_browsing_api_key)
        signals.append(
            _signal(
                "SAFE_BROWSING",
                "unavailable",
                0,
                "Threat database",
                "खतरा डेटाबेस",
                "The threat database check is unavailable." if configured else "Add a Google Safe Browsing API key to enable this check.",
                "खतरा डेटाबेस जाँच उपलब्ध नहीं है।" if configured else "यह जाँच चालू करने के लिए Google Safe Browsing API कुंजी जोड़ें।",
                request.language,
                source="google_safe_browsing",
            )
        )
        browsing_status = "unavailable" if configured else "not_configured"
    else:
        signals.append(
            _signal(
                "SAFE_BROWSING",
                "warning" if safe_browsing else "safe",
                60 if safe_browsing else 0,
                "Threat database",
                "खतरा डेटाबेस",
                "Google Safe Browsing reported this URL." if safe_browsing else "Google Safe Browsing did not report this URL.",
                "Google Safe Browsing ने इस URL को रिपोर्ट किया है।" if safe_browsing else "Google Safe Browsing ने इस URL को रिपोर्ट नहीं किया।",
                request.language,
                source="google_safe_browsing",
                critical=safe_browsing,
            )
        )
        browsing_status = "completed"

    return build_result(
        input_type="url",
        signals=signals,
        integrations={
            "safe_browsing": browsing_status,
            "domain_registration": domain_status,
            "vision": "not_applicable",
        },
        language=request.language,
    )

