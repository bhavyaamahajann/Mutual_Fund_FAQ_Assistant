import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorEmbedder:
    def __init__(self, chroma_db_path: Path, collection_name: str, openai_api_key: str = None, model_name: str = "BAAI/bge-large-en-v1.5"):

        self.chroma_db_path = str(chroma_db_path)
        self.collection_name = collection_name
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=self.chroma_db_path)
        
        # Setup SentenceTransformer embedding function (local BAAI model)
        logger.info(f"Initializing local SentenceTransformerEmbeddingFunction with model: {model_name}")
        self.embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def reset_collection(self):
        """Deletes all existing documents in the collection to ensure a fresh ingest."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn
            )
            logger.info(f"Reset ChromaDB collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")

    def embed_and_store(self, chunks: list[dict]):
        """
        Takes a list of chunks [{"text": str, "metadata": dict}], generates embeddings, and stores them in ChromaDB.
        """
        if not chunks:
            logger.warning("No chunks to embed and store.")
            return

        documents = []
        metadatas = []
        ids = []

        for chunk in chunks:
            documents.append(chunk["text"])
            
            # ChromaDB requires metadata values to be str, int, float, or bool
            cleaned_metadata = {}
            for k, v in chunk["metadata"].items():
                if v is None:
                    continue
                if isinstance(v, (str, int, float, bool)):
                    cleaned_metadata[k] = v
                else:
                    cleaned_metadata[k] = str(v)
            
            metadatas.append(cleaned_metadata)
            
            # Generate a unique ID based on fund ID and chunk index
            fund_id = cleaned_metadata.get("fund_id", "unknown")
            chunk_idx = cleaned_metadata.get("chunk_index", 0)
            ids.append(f"{fund_id}_chunk_{chunk_idx}")

        # Upsert in batches to avoid payload limits
        batch_size = 100
        total_chunks = len(documents)
        
        for i in range(0, total_chunks, batch_size):
            end_idx = min(i + batch_size, total_chunks)
            try:
                self.collection.upsert(
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
                logger.info(f"Upserted chunks {i} to {end_idx-1} into ChromaDB.")
            except Exception as e:
                logger.error(f"Failed to upsert batch {i}-{end_idx-1}: {e}")
                
        logger.info(f"Successfully embedded and stored {total_chunks} chunks.")
