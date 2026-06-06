from curl_cffi import requests
import time
import logging
import random

logger = logging.getLogger(__name__)


class IndMoneyScraper:
    def __init__(
        self,
        max_retries: int = 3,
        delay_between_requests: float = 1.0,
        use_playwright_fallback: bool = True,
    ):
        """
        Parameters
        ----------
        max_retries: int
            Number of HTTP attempts before giving up.
        delay_between_requests: float
            Base delay (seconds) between successive requests.
        use_playwright_fallback: bool
            If True, a headless Playwright browser will be tried when all HTTP attempts fail.
        """
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.use_playwright_fallback = use_playwright_fallback

        # A small pool of realistic Chrome user‑agents (rotate per request)
        self.ua_pool = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]

        # Base headers – we add a dynamic Referer & Accept‑Encoding per request
        self.base_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
        }

    def _build_headers(self, url: str) -> dict:
        """Create request headers for a specific URL."""
        headers = self.base_headers.copy()
        headers["User-Agent"] = random.choice(self.ua_pool)
        # Some sites check the Referer – set it to the site root
        headers["Referer"] = "https://www.indmoney.com/"
        return headers

    def fetch_url(self, url: str) -> tuple[str, str, bool]:
        """
        Fetches the HTML content for a given URL with retry logic.
        Returns: (url, raw_html, success_status)
        """
        for attempt in range(self.max_retries):
            try:
                headers = self._build_headers(url)
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=15,
                    impersonate="chrome",
                )
                response.raise_for_status()

                # Slight jitter on the delay to look less bot‑like
                jitter = random.uniform(0.5, 1.5)
                time.sleep(self.delay_between_requests + jitter)

                return url, response.text, True
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    backoff = self.delay_between_requests * (2 ** attempt)
                    time.sleep(backoff)  # exponential backoff
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {url}")

        # ---- Playwright fallback -------------------------------------------------
        if self.use_playwright_fallback:
            try:
                from playwright.sync_api import sync_playwright

                logger.info(f"Falling back to Playwright for {url}")
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.set_extra_http_headers(self._build_headers(url))
                    page.goto(url, timeout=15000)
                    html = page.content()
                    browser.close()
                    return url, html, True
            except Exception as e:
                logger.error(f"Playwright fallback also failed for {url}: {e}")

        return url, "", False

    def fetch_all(self, urls: list[str]) -> list[dict]:
        """
        Fetches multiple URLs sequentially.
        """
        results = []
        for url in urls:
            logger.info(f"Fetching {url}...")
            fetched_url, html, success = self.fetch_url(url)
            results.append({
                "url": fetched_url,
                "html": html,
                "success": success,
            })
        return results
