import pytest

from app.services.url_analyzer import UnsafeUrlError, local_url_signals, validate_and_extract


def test_extracts_registered_domain() -> None:
    hostname, registered_domain, label = validate_and_extract("https://shop.example.com/product")

    assert hostname == "shop.example.com"
    assert registered_domain == "example.com"
    assert label == "example"


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/test",
        "http://10.0.0.1/test",
        "https://user:password@example.com",
        "https://example.com:8080",
    ],
)
def test_rejects_unsafe_url_shapes(url: str) -> None:
    with pytest.raises(UnsafeUrlError):
        validate_and_extract(url)


def test_detects_shortener_and_http() -> None:
    signals = local_url_signals(
        "http://bit.ly/example",
        "bit.ly",
        "bit.ly",
        "bit",
        None,
        "en",
    )
    warnings = {signal.code for signal in signals if signal.status == "warning"}

    assert "HTTPS_ENABLED" in warnings
    assert "URL_SHORTENER" in warnings