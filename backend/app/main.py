from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os
from contextlib import asynccontextmanager
from backend.app.config import settings
from backend.app.routes.chat import router as chat_router
from backend.rag.retriever import VectorRetriever

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events to log startup/shutdown and check vector DB readiness.
    """
    logger.info("Starting up Mutual Fund FAQ Assistant API server...")
    try:
        retriever = VectorRetriever()
        count = retriever.collection.count()
        logger.info(f"Vector Database connected. Loaded collection '{settings.chroma_collection_name}' with {count} chunks.")
    except Exception as e:
        logger.error(f"Failed to verify Vector Database during startup: {e}")
        
    yield
    logger.info("Shutting down Mutual Fund FAQ Assistant API server...")

app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="Factual RAG-based API for mutual fund schemes using BAAI local embeddings and Groq LLM",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
# Allows all origins during local development and testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

@app.get("/api/health")
async def health_check():
    """
    FastAPI Health Check Endpoint.
    Returns status of the server and the vector store.
    """
    db_status = "connected"
    collection_count = 0
    
    try:
        retriever = VectorRetriever()
        collection_count = retriever.collection.count()
    except Exception as e:
        logger.error(f"Health Check: Vector Database check failed: {e}")
        db_status = "degraded/disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "collection_count": collection_count,
        "llm_provider": "Groq",
        "embedding_model": settings.embedding_model,
        "llm_model": settings.llm_model
    }

# Serve React Frontend Static Files from build directory
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.exists(frontend_dist):
    # Mount assets folder for JS and CSS files
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # Catch-all route to serve React's index.html
    @app.get("/{catchall:path}")
    async def serve_frontend(catchall: str):
        # Exclude API endpoints from catch-all
        if catchall.startswith("api/") or catchall.startswith("docs"):
            raise HTTPException(status_code=404, detail="Not Found")
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    logger.warning(f"React build output folder not found at: {frontend_dist}. Direct server view requires running 'npm run build' in frontend/.")
