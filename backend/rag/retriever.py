import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import logging
from pathlib import Path
from backend.app.config import settings

logger = logging.getLogger(__name__)

class VectorRetriever:
    def __init__(self, chroma_db_path: Path = None, collection_name: str = None, model_name: str = None):
        self.chroma_db_path = str(chroma_db_path) if chroma_db_path else str(settings.chroma_db_path)
        self.collection_name = collection_name if collection_name else settings.chroma_collection_name
        self.model_name = model_name if model_name else settings.embedding_model
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=self.chroma_db_path)
        
        # Setup SentenceTransformer embedding function (same as ingestion)
        logger.info(f"Retriever: Initializing SentenceTransformerEmbeddingFunction with model: {self.model_name}")
        self.embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=self.model_name
        )
        
        # Get existing collection
        self.collection = self.client.get_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def retrieve(self, query: str, top_k: int = None, distance_threshold: float = 1.3, selected_funds: list[str] = None) -> list[dict]:
        """
        Retrieves top_k chunks relevant to the query from ChromaDB.
        Filters out chunks that exceed the distance_threshold (higher distance = less similar).
        Returns a list of dicts: [{"text": str, "metadata": dict, "distance": float}]
        """
        k = top_k if top_k is not None else settings.top_k
        
        try:
            query_kwargs = {
                "query_texts": [query],
                "n_results": k
            }
            if selected_funds:
                query_kwargs["where"] = {"fund_id": {"$in": selected_funds}}
                logger.info(f"Retriever: Filtering query using metadata where: {query_kwargs['where']}")
                
            results = self.collection.query(**query_kwargs)
            
            if not results or not results["documents"] or not results["documents"][0]:
                logger.warning("No retrieval results returned from ChromaDB.")
                return []
                
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            ids = results["ids"][0]
            
            retrieved_chunks = []
            for doc, meta, dist, chunk_id in zip(documents, metadatas, distances, ids):
                # Filter out chunks that are too far (low similarity)
                if dist > distance_threshold:
                    logger.info(f"Chunk {chunk_id} filtered out. Distance {dist:.4f} > threshold {distance_threshold}")
                    continue
                    
                retrieved_chunks.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": dist,
                    "id": chunk_id
                })
                
            logger.info(f"Retrieved {len(retrieved_chunks)}/ {len(documents)} chunks under threshold.")
            return retrieved_chunks
            
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []
