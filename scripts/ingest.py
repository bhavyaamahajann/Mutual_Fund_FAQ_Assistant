import sys
from pathlib import Path
import json
import logging
import hashlib
from datetime import datetime

# Ensure backend package is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.app.config import settings
from backend.ingestion.chunker import TextChunker
from backend.ingestion.embedder import VectorEmbedder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_text_from_metadata(fund: dict) -> str:
    """
    Builds a structured text document from pre-scraped fund metadata JSON.
    This is used instead of live scraping to avoid 403 errors from IndMoney
    when running inside Docker/CI environments.
    """
    managers_str = (
        ", ".join(fund.get("fund_managers", []))
        if isinstance(fund.get("fund_managers"), list)
        else str(fund.get("fund_managers", "Not available"))
    )

    text = (
        f"Mutual Fund Name: {fund.get('fund_name', 'Not available')}\n"
        f"Category: {fund.get('fund_category', 'Not available')}\n"
        f"Plan Type: {fund.get('fund_plan', 'Not available')}\n"
        f"NAV: {fund.get('nav', 'Not available')} (as of {fund.get('nav_date', 'Not available')})\n"
        f"Expense Ratio: {fund.get('expense_ratio', 'Not available')}\n"
        f"Exit Load: {fund.get('exit_load', 'Not available')}\n"
        f"Minimum Lumpsum Investment: {fund.get('min_lumpsum', 'Not available')}\n"
        f"Minimum SIP Investment: {fund.get('min_sip', 'Not available')}\n"
        f"Benchmark Index: {fund.get('benchmark_index', 'Not available')}\n"
        f"Riskometer: {fund.get('riskometer', 'Not available')}\n"
        f"Lock-in Period: {fund.get('lock_in', 'Not available')}\n"
        f"Fund Managers: {managers_str}\n"
        f"AUM (Assets Under Management): {fund.get('aum', 'Not available')}\n"
        f"Fund House: {fund.get('fund_house', 'Not available')}\n"
        f"Source URL: {fund.get('source_url', 'Not available')}\n"
    )
    return text


def run_ingestion():
    logger.info("Starting ingestion pipeline (metadata-only mode – no live scraping)...")

    # 1. Load pre-scraped fund metadata
    if not settings.fund_metadata_path.exists():
        logger.error(f"fund_metadata.json not found at {settings.fund_metadata_path}. Aborting.")
        sys.exit(1)

    with open(settings.fund_metadata_path, "r") as f:
        funds = json.load(f)

    logger.info(f"Loaded {len(funds)} funds from pre-scraped metadata.")

    # 2. Initialize Pipeline Components
    chunker = TextChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    embedder = VectorEmbedder(
        chroma_db_path=settings.chroma_db_path,
        collection_name=settings.chroma_collection_name,
        model_name=settings.embedding_model
    )

    # Reset collection so we start fresh each build
    embedder.reset_collection()

    all_chunks = []

    # 3. Process each fund from metadata
    for fund in funds:
        fund_name = fund.get("fund_name", fund.get("fund_id", "Unknown"))
        logger.info(f"Processing: {fund_name}")

        # Build structured text document from stored metadata
        text = build_text_from_metadata(fund)

        # Prepare metadata for vector store (all values must be str/int/float/bool)
        chunk_metadata = {
            "fund_id": fund.get("fund_id", ""),
            "fund_name": fund.get("fund_name", ""),
            "fund_category": fund.get("fund_category", ""),
            "fund_group": fund.get("fund_group", ""),
            "fund_plan": fund.get("fund_plan", ""),
            "nav": str(fund.get("nav", "")),
            "nav_date": str(fund.get("nav_date", "")),
            "expense_ratio": str(fund.get("expense_ratio", "")),
            "exit_load": str(fund.get("exit_load", "")),
            "min_sip": str(fund.get("min_sip", "")),
            "min_lumpsum": str(fund.get("min_lumpsum", "")),
            "benchmark_index": str(fund.get("benchmark_index", "")),
            "riskometer": str(fund.get("riskometer", "")),
            "lock_in": str(fund.get("lock_in", "")),
            "fund_managers": ", ".join(fund.get("fund_managers", [])) if isinstance(fund.get("fund_managers"), list) else str(fund.get("fund_managers", "")),
            "aum": str(fund.get("aum", "")),
            "fund_house": str(fund.get("fund_house", "")),
            "source_url": str(fund.get("source_url", "")),
        }

        # 4. Chunk the text document
        chunks = chunker.chunk_document(text, chunk_metadata)
        all_chunks.extend(chunks)

    # 5. Embed and store all chunks
    if all_chunks:
        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
        embedder.embed_and_store(all_chunks)
    else:
        logger.warning("No chunks were generated!")

    logger.info("Ingestion pipeline completed successfully.")
    logger.info(f"Summary: {len(funds)} funds processed, {len(all_chunks)} chunks embedded.")


if __name__ == "__main__":
    run_ingestion()
