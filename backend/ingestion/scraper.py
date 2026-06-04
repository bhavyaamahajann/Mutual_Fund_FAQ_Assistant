from curl_cffi import requests
import time
import logging

logger = logging.getLogger(__name__)

class IndMoneyScraper:
    def __init__(self, max_retries: int = 3, delay_between_requests: float = 1.0):
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def fetch_url(self, url: str) -> tuple[str, str, bool]:
        """
        Fetches the HTML content for a given URL with retry logic.
        Returns: (url, raw_html, success_status)
        """
        for attempt in range(self.max_retries):
            try:
                # Use impersonate='chrome' to bypass Cloudflare anti-bot checks
                response = requests.get(url, headers=self.headers, timeout=15, impersonate="chrome")
                response.raise_for_status()

                
                # Enforce rate limiting
                time.sleep(self.delay_between_requests)
                
                return url, response.text, True
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.delay_between_requests * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {url}")
                    
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
                "success": success
            })
        return results
