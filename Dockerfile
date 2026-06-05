FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Pre-download the Hugging Face embedding model during build time to avoid startup timeout
RUN python3 -c "from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction; SentenceTransformerEmbeddingFunction(model_name='BAAI/bge-large-en-v1.5')"

# Copy all codebase files
COPY . .

# Run FastAPI using Uvicorn with dynamic port routing
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
