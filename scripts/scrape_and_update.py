"""
scripts/scrape_and_update.py
────────────────────────────
Scrapes fresh fund data from each IndMoney URL in corpus_urls.json,
extracts structured metadata via parser.py, and overwrites
backend/data/fund_metadata.json with the latest values.

This script is called by the GitHub Actions daily workflow BEFORE
ingest.py so that ingest.py always reads up-to-date metadata.

Usage:
    python scripts/scrape_and_update.py
"""

import sys
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# Ensure backend package is importable
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.app.config import settings
from backend.ingestion.scraper import IndMoneyScraper
from backend.ingestion.parser import HtmlParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def compute_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def run_scrape_and_update():
    logger.info("Starting scrape-and-update pipeline (10:00 AM IST daily refresh)...")

    # 1. Load corpus URL list
    with open(settings.corpus_urls_path, "r") as f:
        corpus = json.load(f)

    funds = corpus.get("funds", [])
    logger.info(f"Loaded {len(funds)} fund URLs from corpus.")

    # 2. Load existing metadata (for hash-based change detection)
    existing_metadata: dict[str, dict] = {}
    if settings.fund_metadata_path.exists():
        try:
            with open(settings.fund_metadata_path, "r") as f:
                existing_list = json.load(f)
            existing_metadata = {item["source_url"]: item for item in existing_list if "source_url" in item}
        except Exception as e:
            logger.warning(f"Could not load existing fund_metadata.json: {e}")

    scraper = IndMoneyScraper(
        max_retries=3,
        delay_between_requests=1.5,
        use_playwright_fallback=False,   # CI runner has no display; skip Playwright
    )
    parser = HtmlParser()

    updated_metadata = []
    success_count = 0
    fail_count = 0

    # 3. Scrape each URL
    for fund_info in funds:
        url = fund_info["url"]
        logger.info(f"Scraping: {fund_info['name']}")

        _, html, success = scraper.fetch_url(url)

        if not success:
            logger.error(f"Failed to fetch {url}. Keeping previous metadata if available.")
            # Fall back to the last good metadata so we don't lose data
            if url in existing_metadata:
                updated_metadata.append(existing_metadata[url])
            fail_count += 1
            continue

        content_hash = compute_hash(html)

        # Build base metadata from corpus definition
        base_meta = {
            "fund_id": fund_info["id"],
            "fund_name": fund_info["name"],
            "fund_category": fund_info["category"],
            "fund_group": fund_info["group"],
            "fund_plan": fund_info["plan"],
        }

        _, parsed_metadata = parser.parse(html, url, base_meta)
        parsed_metadata["content_hash"] = content_hash
        parsed_metadata["last_scraped"] = datetime.now(timezone.utc).isoformat()

        # Log whether content changed
        prev_hash = existing_metadata.get(url, {}).get("content_hash")
        if prev_hash == content_hash:
            logger.info(f"  → No content change detected for {fund_info['name']}.")
        else:
            logger.info(f"  → Content updated for {fund_info['name']}.")

        updated_metadata.append(parsed_metadata)
        success_count += 1

    # 4. Write refreshed metadata to file
    with open(settings.fund_metadata_path, "w") as f:
        json.dump(updated_metadata, f, indent=2, ensure_ascii=False)

    logger.info(
        f"Scrape-and-update complete. "
        f"Success: {success_count}, Failed: {fail_count}. "
        f"Metadata written to {settings.fund_metadata_path}"
    )


if __name__ == "__main__":
    run_scrape_and_update()
