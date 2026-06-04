import sys
from pathlib import Path
import json
import logging
import hashlib
from datetime import datetime

# Ensure backend package is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.app.config import settings
from backend.ingestion.scraper import IndMoneyScraper
from backend.ingestion.parser import HtmlParser
from backend.ingestion.chunker import TextChunker
from backend.ingestion.embedder import VectorEmbedder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def compute_hash(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def run_ingestion():
    logger.info("Starting ingestion pipeline...")
    
    # 1. Load Corpus
    with open(settings.corpus_urls_path, "r") as f:
        corpus = json.load(f)
    
    funds = corpus.get("funds", [])
    urls = [f["url"] for f in funds]
    logger.info(f"Loaded {len(urls)} URLs from corpus.")
    
    # Check for existing metadata to do hash comparison
    existing_hashes = {}
    if settings.fund_metadata_path.exists():
        try:
            with open(settings.fund_metadata_path, "r") as f:
                existing_meta = json.load(f)
                for fund in existing_meta:
                    existing_hashes[fund["url"]] = fund.get("content_hash")
        except Exception as e:
            logger.warning(f"Could not load existing metadata: {e}")

    # 2. Initialize Pipeline Components
    scraper = IndMoneyScraper()
    parser = HtmlParser()
    chunker = TextChunker(
        chunk_size=settings.chunk_size, 
        chunk_overlap=settings.chunk_overlap
    )
    embedder = VectorEmbedder(
        chroma_db_path=settings.chroma_db_path,
        collection_name=settings.chroma_collection_name,
        model_name=settings.embedding_model
    )
    
    # Force reset the collection so we don't have stale/duplicate chunks 
    # if we are re-ingesting fully. Alternatively, we could delete per-fund.
    # For simplicity, we'll reset on every run.
    embedder.reset_collection()

    all_chunks = []
    final_metadata = []
    skipped = 0

    # Process each fund
    for fund_info in funds:
        url = fund_info["url"]
        logger.info(f"Processing: {fund_info['name']}")
        
        _, html, success = scraper.fetch_url(url)
        if not success:
            logger.error(f"Failed to fetch {url}. Skipping.")
            continue
            
        content_hash = compute_hash(html)
        
        # 3. Parse HTML
        base_meta = {
            "fund_id": fund_info["id"],
            "fund_name": fund_info["name"],
            "fund_category": fund_info["category"],
            "fund_group": fund_info["group"],
            "fund_plan": fund_info["plan"]
        }
        
        clean_text, parsed_metadata = parser.parse(html, url, base_meta)
        parsed_metadata["content_hash"] = content_hash
        parsed_metadata["last_scraped"] = datetime.utcnow().isoformat()
        
        final_metadata.append(parsed_metadata)
        
        # Change detection log
        if existing_hashes.get(url) == content_hash:
            logger.info(f"No changes detected for {fund_info['name']}. Processing chunks anyway because of DB reset.")
            
        # 4. Chunking
        chunks = chunker.chunk_document(clean_text, parsed_metadata)
        all_chunks.extend(chunks)
        
    # 5. Embed and Store
    if all_chunks:
        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
        embedder.embed_and_store(all_chunks)
    else:
        logger.warning("No chunks were generated!")

    # 6. Update Metadata JSON
    with open(settings.fund_metadata_path, "w") as f:
        json.dump(final_metadata, f, indent=2)
        
    logger.info("Ingestion pipeline completed successfully.")
    logger.info(f"Summary: {len(final_metadata)} funds processed, {len(all_chunks)} chunks embedded.")

if __name__ == "__main__":
    run_ingestion()
