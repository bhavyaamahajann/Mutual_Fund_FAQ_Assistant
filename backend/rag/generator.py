from groq import Groq
import logging
from backend.app.config import settings
from backend.rag.classifier import QueryClassifier
from backend.rag.retriever import VectorRetriever
from backend.rag.validator import ResponseValidator
from backend.rag.prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    REFUSAL_ADVISORY,
    REFUSAL_PII,
    REFUSAL_COMPARISON,
    REFUSAL_OUT_OF_SCOPE,
    REFUSAL_GREETING
)

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.classifier = QueryClassifier()
        
        # Initialize retriever (errors handled internally if DB not set up yet)
        try:
            self.retriever = VectorRetriever()
        except Exception as e:
            logger.error(f"Failed to initialize VectorRetriever: {e}")
            self.retriever = None
            
        self.validator = ResponseValidator()
        
        # Initialize Groq client
        # Read API key from settings
        api_key = settings.groq_api_key
        if not api_key:
            logger.warning("GROQ_API_KEY is not configured in settings!")
        self.groq_client = Groq(api_key=api_key) if api_key else None

    def generate_response(self, query: str, selected_funds: list[str] = None) -> dict:
        """
        Processes a user query through the RAG pipeline.
        Returns a dict: {
            "status": "success" | "refused",
            "type": str,
            "answer": str,
            "citation": {"label": str, "url": str} | None,
            "last_updated": str | None
        }
        """
        # 1. Classify query
        classification = self.classifier.classify(query)
        q_type = classification["type"]
        
        logger.info(f"Query: '{query[:50]}...' classified as: {q_type}")

        # 2. Handle Refusals and Non-Factual routes directly (bypassing LLM / Retrieve)
        if q_type == "pii":
            return {
                "status": "refused",
                "type": "pii",
                "answer": REFUSAL_PII,
                "citation": None,
                "last_updated": None
            }
            
        if q_type == "advisory":
            return {
                "status": "refused",
                "type": "advisory",
                "answer": REFUSAL_ADVISORY,
                "citation": None,
                "last_updated": None
            }
            
        if q_type == "comparison":
            return {
                "status": "refused",
                "type": "comparison",
                "answer": REFUSAL_COMPARISON,
                "citation": None,
                "last_updated": None
            }
            
        if q_type == "greeting":
            return {
                "status": "refused",
                "type": "greeting",
                "answer": REFUSAL_GREETING,
                "citation": None,
                "last_updated": None
            }
            
        if q_type == "out_of_scope":
            return {
                "status": "refused",
                "type": "out_of_scope",
                "answer": REFUSAL_OUT_OF_SCOPE,
                "citation": None,
                "last_updated": None
            }

        # 3. Factual Query Processing
        if not self.retriever:
            # Fallback if DB client is uninitialized
            return {
                "status": "refused",
                "type": "out_of_scope",
                "answer": "Vector database is not initialized. Please run ingestion.",
                "citation": None,
                "last_updated": None
            }
            
        # Retrieve chunks
        # Use a distance threshold of 1.3 to filter out unrelated chunks
        chunks = self.retriever.retrieve(query, distance_threshold=1.3, selected_funds=selected_funds)
        
        if not chunks:
            # Fallback if no relevant documents match the query in the DB
            return {
                "status": "refused",
                "type": "out_of_scope",
                "answer": "I am sorry, but that information is not available in the official source documents.",
                "citation": None,
                "last_updated": None
            }

        # Build context
        context_parts = []
        for chunk in chunks:
            context_parts.append(chunk["text"])
        context_str = "\n---\n".join(context_parts)
        
        # Extract source details from top chunk
        top_meta = chunks[0]["metadata"]
        source_url = top_meta.get("source_url", "https://www.indmoney.com")
        last_scraped = top_meta.get("last_scraped", "Not available")
        fund_name = top_meta.get("fund_name", "the mutual fund")

        # Check Groq client configuration
        if not self.groq_client:
            return {
                "status": "refused",
                "type": "out_of_scope",
                "answer": "Groq client is not configured. Please supply a valid GROQ_API_KEY.",
                "citation": None,
                "last_updated": None
            }

        # Call Groq Chat Completions API
        user_prompt = USER_PROMPT_TEMPLATE.format(context=context_str, question=query)
        try:
            logger.info(f"Calling Groq LLM API with model: {settings.llm_model}")
            completion = self.groq_client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,  # Zero temperature for factual/deterministic response
                max_tokens=250
            )
            
            llm_answer = completion.choices[0].message.content
            logger.info("Groq LLM call succeeded.")
            
        except Exception as e:
            logger.error(f"Failed to fetch completion from Groq: {e}")
            return {
                "status": "refused",
                "type": "out_of_scope",
                "answer": "Failed to generate a response from the language model service.",
                "citation": None,
                "last_updated": None
            }

        # 4. Post-generation Output Validation & Formatting
        validation = self.validator.validate_and_fix(
            answer=llm_answer,
            source_url=source_url,
            last_scraped=last_scraped
        )
        
        return {
            "status": "success",
            "type": "factual",
            "answer": validation["answer"],
            "citation": {
                "label": fund_name,
                "url": source_url
            },
            "last_updated": last_scraped
        }
