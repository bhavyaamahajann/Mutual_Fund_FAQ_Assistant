from fastapi import APIRouter, HTTPException, Depends
import re
import logging
from backend.app.models import ChatRequest, ChatResponse
from backend.rag.generator import RAGPipeline

logger = logging.getLogger(__name__)

router = APIRouter()

# Instantiate the pipeline once
try:
    pipeline = RAGPipeline()
except Exception as e:
    logger.error(f"Failed to instantiate RAGPipeline on router import: {e}")
    pipeline = None

def sanitize_input(text: str) -> str:
    """
    Strips HTML and script tags to prevent XSS payloads.
    """
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]*>', '', text)
    # Remove script references
    clean = re.sub(r'javascript:', '', clean, flags=re.IGNORECASE)
    return clean.strip()

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Exposes the RAG query pipeline as a REST endpoint.
    Accepts ChatRequest and returns ChatResponse.
    """
    if pipeline is None:
        raise HTTPException(
            status_code=500,
            detail="The RAG pipeline is currently unavailable. Please verify that ingestion has completed successfully."
        )

    # Sanitize user query
    sanitized_query = sanitize_input(request.query)
    if not sanitized_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty or solely HTML tags.")

    try:
        logger.info(f"Processing query: '{sanitized_query[:60]}' with selected_funds: {request.selected_funds}")
        response_dict = pipeline.generate_response(sanitized_query, request.selected_funds, request.history)
        return response_dict
        
    except Exception as e:
        logger.error(f"Unhandled error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing your request.")
