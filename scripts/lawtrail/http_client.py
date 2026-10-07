"""Polite HTTP client shared by all scrapers: fixed User-Agent, minimum delay
between requests, and retries on transient failures.
"""

import time

import requests

USER_AGENT = "Lawtrail/0.1 (+hiramaulana@users.noreply.github.com)"
MIN_DELAY_SECONDS = 2.0
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5.0


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
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
        raise last_error
