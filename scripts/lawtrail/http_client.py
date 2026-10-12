"""Polite HTTP client shared by all scrapers: fixed User-Agent, minimum delay
between requests, and retries on transient failures.
"""

import time

import requests

USER_AGENT = "Lawtrail/0.1 (+hiramaulana@users.noreply.github.com)"
MIN_DELAY_SECONDS = 2.0
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5.0

# peraturan.bpk.go.id sits behind Cloudflare. From a datacenter IP (such as a
# GitHub-hosted Actions runner) it answers the interstitial challenge page
# instead of the real HTML, so parsing silently finds nothing. Detect that and
# say so, rather than letting it surface as an opaque parse failure.
CHALLENGE_MARKERS = (
    "Just a moment...",
    "Performing security verification",
    "cf-browser-verification",
    "challenge-platform",
)

class BlockedByChallenge(RuntimeError):
    pass

def _looks_like_challenge(response):
    content_type = response.headers.get("Content-Type", "")
    if "html" not in content_type.lower():
        return False
    head = response.text[:4000]
    return any(marker in head for marker in CHALLENGE_MARKERS)


class PoliteSession:
    def __init__(self, min_delay=MIN_DELAY_SECONDS):
        self._session = requests.Session()
        self._session.headers["User-Agent"] = USER_AGENT
        self._min_delay = min_delay
        self._last_request_at = None

    def _wait_for_slot(self):
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self._min_delay - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def get(self, url, **kwargs):
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            self._wait_for_slot()
            self._last_request_at = time.monotonic()
            try:
                response = self._session.get(url, timeout=30, **kwargs)
                response.raise_for_status()
                if _looks_like_challenge(response):
                    raise BlockedByChallenge(
                        f"Diblokir oleh verifikasi keamanan (Cloudflare) saat mengakses {url}. "
                        "Situs sumber menolak permintaan dari alamat IP ini -- umum terjadi pada "
                        "runner GitHub Actions. Jalankan scraper dari koneksi biasa, atau pakai "
                        "self-hosted runner. Lihat docs/PLAN.md bagian 'Kendala yang masih terbuka'."
                    )
                return response
            except BlockedByChallenge:
                # Retrying will not help: the block is per-IP, not transient.
                raise
            except requests.RequestException as exc:
                last_error = exc
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
        raise last_error
