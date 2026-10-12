"""Checks for challenge-page detection in the polite HTTP client."""

import pytest

from lawtrail.http_client import BlockedByChallenge, PoliteSession, _looks_like_challenge

class FakeResponse:
    def __init__(self, text, content_type="text/html; charset=utf-8"):
        self.text = text
        self.headers = {"Content-Type": content_type}

    def raise_for_status(self):
        pass

CHALLENGE_HTML = (
    "<html><head><title>Just a moment...</title></head>"
    "<body>Performing security verification</body></html>"
)

REAL_HTML = '<html><body><a href="/Details/353711/permenaker-no-12-tahun-2026">x</a></body></html>'

def test_detects_cloudflare_interstitial():
    assert _looks_like_challenge(FakeResponse(CHALLENGE_HTML))

def test_real_page_is_not_flagged():
    assert not _looks_like_challenge(FakeResponse(REAL_HTML))

def test_pdf_bytes_are_never_flagged():
    # A PDF body can contain arbitrary bytes; only HTML responses are inspected.
    assert not _looks_like_challenge(
        FakeResponse("Just a moment...", content_type="application/pdf")
    )

def test_get_raises_immediately_without_retrying(monkeypatch):
    session = PoliteSession(min_delay=0)
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return FakeResponse(CHALLENGE_HTML)

    monkeypatch.setattr(session._session, "get", fake_get)

    with pytest.raises(BlockedByChallenge):
        session.get("https://peraturan.bpk.go.id/Search?jenis=105&p=1")

    assert len(calls) == 1, "blokir per-IP tidak boleh di-retry"
