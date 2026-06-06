from groq import Groq
import logging
import json
import re
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

    def get_default_metadata(self) -> dict:
        """Helper to get default metadata from fund_metadata.json."""
        try:
            with open(settings.fund_metadata_path, "r") as f:
                metadata_list = json.load(f)
                if metadata_list:
                    return {
                        "source_url": metadata_list[0].get("source_url", "https://www.indmoney.com"),
                        "last_scraped": metadata_list[0].get("last_scraped", "2026-06-04T18:07:02.871469"),
                        "fund_name": metadata_list[0].get("fund_name", "Factsheet Source")
                    }
        except Exception as e:
            logger.warning(f"Could not load default metadata from JSON: {e}")
        return {
            "source_url": "https://www.indmoney.com",
            "last_scraped": "2026-06-04T18:07:02.871469",
            "fund_name": "Factsheet Source"
        }

    def detect_funds(self, query: str) -> list[str]:
        """Matches a query against all 15 fund IDs using synonym lists."""
        query_lower = query.lower()
        patterns = {
            "icici-pru-smallcap-direct-growth": ["smallcap", "small cap"],
            "icici-pru-large-midcap-direct-growth": ["large & mid", "large and mid", "large & midcap", "large and midcap", "large & mid cap", "large and mid cap"],
            "icici-pru-flexicap-direct-growth": ["flexicap", "flexi cap", "flexi-cap"],
            "icici-pru-focused-equity-direct-growth": ["focused equity", "focused fund", "focused"],
            "icici-pru-midcap-direct-growth": ["midcap", "mid cap"],
            "icici-pru-multicap-direct-growth": ["multicap", "multi cap"],
            "icici-pru-largecap-direct-growth": ["largecap", "large cap"],
            "icici-pru-elss-direct-growth": ["elss", "tax saver", "tax saving"],
            "icici-pru-equity-savings-direct-growth": ["equity savings"],
            "icici-pru-equity-debt-direct-growth": ["equity & debt", "equity and debt"],
            "icici-pru-regular-savings-direct-growth": ["regular savings", "savings fund", "prudential savings"],
            "icici-pru-multi-asset-direct-growth": ["multi asset", "multi-asset", "multiasset"],
            "icici-pru-nifty50-index-direct-growth": ["nifty 50", "nifty50", "nifty index", "nifty 50 index", "nifty-50"],
            "icici-pru-gold-etf-fof-direct-growth": ["gold"],
            "icici-pru-silver-etf-fof-direct-growth": ["silver"]
        }
        
        matched = []
        for fund_id, synonyms in patterns.items():
            for syn in synonyms:
                if syn in query_lower:
                    # Avoid false positives:
                    if fund_id == "icici-pru-midcap-direct-growth":
                        if any(x in query_lower for x in ["large & mid", "large and mid", "large & midcap", "large and midcap", "large & mid cap", "large and mid cap"]):
                            continue
                    if fund_id == "icici-pru-largecap-direct-growth":
                        if any(x in query_lower for x in ["large & mid", "large and mid", "large & midcap", "large and midcap", "large & mid cap", "large and mid cap"]):
                            continue
                    if fund_id == "icici-pru-regular-savings-direct-growth":
                        if "equity savings" in query_lower:
                            continue
                    
                    matched.append(fund_id)
                    break
        return matched

    def check_requires_scheme_name(self, query: str) -> tuple[bool, str]:
        """Checks if the query asks about a metric requiring a specific scheme."""
        query_lower = query.lower()
        if "expense ratio" in query_lower or "expense" in query_lower:
            return True, "expense_ratio"
        if "cagr" in query_lower or "returns" in query_lower or "performance" in query_lower:
            return True, "cagr"
        if "sector" in query_lower or "allocation" in query_lower:
            return True, "sector_allocation"
        if "benchmark" in query_lower:
            return True, "benchmark"
        if "nav" in query_lower:
            return True, "nav"
        if "exit load" in query_lower or "exit" in query_lower:
            return True, "exit_load"
        if "manager" in query_lower or "managed by" in query_lower:
            return True, "fund_manager"
        if "sip" in query_lower:
            return True, "sip"
        if "lumpsum" in query_lower or "lump sum" in query_lower:
            return True, "lumpsum"
        if "riskometer" in query_lower or "risk profile" in query_lower or "risk" in query_lower:
            return True, "riskometer"
        return False, ""

    def format_aum_value(self, aum_str: str) -> str:
        """Formats AUM string like '₹8741 Cr' into a clean numeric string with commas."""
        clean = aum_str.replace("₹", "").replace("Cr", "").replace("cr", "").replace(",", "").strip()
        try:
            if "." in clean:
                val = float(clean)
                return f"{val:,.1f}"
            else:
                val = int(clean)
                return f"{val:,}"
        except ValueError:
            return clean

    def format_as_of_date(self, date_str: str) -> str:
        """Formats dates to 'MMM DD, YYYY' format."""
        from datetime import datetime
        for fmt in ("%d %b %Y", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%b %d, %Y")
            except ValueError:
                continue
        return date_str

    def handle_multi_fund_aum(self, query: str, matched_funds: list[str]) -> dict:
        """Handles multi-fund AUM queries, formatting results into a markdown table."""
        try:
            with open(settings.fund_metadata_path, "r") as f:
                metadata_list = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load fund metadata: {e}")
            metadata_list = []
            
        if matched_funds:
            target_funds = [f for f in metadata_list if f["fund_id"] in matched_funds]
        else:
            target_funds = metadata_list
            
        verified_funds = []
        unverified_count = 0
        for fund in target_funds:
            aum = fund.get("aum")
            if aum and aum != "Not available":
                verified_funds.append(fund)
            else:
                unverified_count += 1
                
        total_target = len(target_funds)
        
        # Build objective intro text
        if "highest" in query.lower():
            highest_fund = None
            highest_val = -1.0
            for fund in verified_funds:
                try:
                    clean_val = fund["aum"].replace("₹", "").replace("Cr", "").replace("cr", "").replace(",", "").strip()
                    val = float(clean_val)
                    if val > highest_val:
                      highest_val = val
                      highest_fund = fund
                except ValueError:
                    continue
            if highest_fund:
                intro = f"{highest_fund['fund_name']} has the highest AUM of {highest_fund['aum']}."
            else:
                intro = "I could verify the Assets Under Management (AUM) for the schemes."
        else:
            intro = f"I could verify AUM information for {len(verified_funds)} out of {total_target} schemes in the retrieved sources."
            if unverified_count > 0:
                intro += " The remaining schemes did not contain verifiable AUM information."
                
        # Generate table markdown
        table_lines = [
            "| Scheme | AUM (₹ Crore) | As Of |",
            "| :--- | ------------: | :--- |"
        ]
        for fund in verified_funds:
            name = fund["fund_name"]
            aum_formatted = self.format_aum_value(fund["aum"])
            as_of = self.format_as_of_date(fund.get("nav_date", "Not available"))
            table_lines.append(f"| {name} | {aum_formatted} | {as_of} |")
            
        table_markdown = "\n".join(table_lines)
        
        if verified_funds:
            source_url = verified_funds[0].get("source_url", "https://www.indmoney.com")
            last_scraped = verified_funds[0].get("last_scraped", "Not available")
            fund_name_label = verified_funds[0].get("fund_name", "Factsheet Source")
        else:
            source_url = "https://www.indmoney.com"
            last_scraped = "Not available"
            fund_name_label = "Factsheet Source"
            
        full_answer = f"{intro}\n\n{table_markdown}"
        
        validation = self.validator.validate_and_fix(
            answer=full_answer,
            source_url=source_url,
            last_scraped=last_scraped
        )
        
        return {
            "status": "success",
            "type": "factual",
            "answer": validation["answer"],
            "citation": {
                "label": fund_name_label,
                "url": source_url
            },
            "last_updated": last_scraped
        }

    def _rewrite_query(self, query: str, history: list[dict]) -> str:
        if not self.groq_client or not history:
            return query
        try:
            # Filter history to last 4 messages to avoid excessive context
            recent_history = history[-4:]
            messages = [{"role": "system", "content": "You are a helpful assistant. Given the following conversation history and a new user query, rewrite the user query into a fully standalone, self-contained factual query that can be used for semantic search. Do not answer the question. Only output the rewritten query. If the query is already standalone, just output it as is."}]
            for msg in recent_history:
                role = "assistant" if msg.get("role") == "assistant" else "user"
                messages.append({"role": role, "content": str(msg.get("content", ""))})
            messages.append({"role": "user", "content": f"Rewrite this query: {query}"})
            
            completion = self.groq_client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.0,
                max_tokens=100
            )
            rewritten = completion.choices[0].message.content.strip()
            # Strip quotes if any
            if rewritten.startswith('"') and rewritten.endswith('"'):
                rewritten = rewritten[1:-1]
            logger.info(f"Query rewritten from '{query}' to '{rewritten}'")
            return rewritten
        except Exception as e:
            logger.warning(f"Failed to rewrite query: {e}")
            return query

    def generate_response(self, query: str, selected_funds: list[str] = None, history: list[dict] = None) -> dict:
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
        # 0. Rewrite query based on conversational history if provided
        if history and len(history) > 0:
            query = self._rewrite_query(query, history)

        # 1. Classify query
        classification = self.classifier.classify(query)
        q_type = classification["type"]
        
        logger.info(f"Query: '{query[:50]}...' classified as: {q_type}")

        # Retrieve default metadata for refusals/clarifications
        default_meta = self.get_default_metadata()

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
            validation = self.validator.validate_and_fix(
                answer=REFUSAL_ADVISORY,
                source_url=default_meta["source_url"],
                last_scraped=default_meta["last_scraped"]
            )
            return {
                "status": "refused",
                "type": "advisory",
                "answer": validation["answer"],
                "citation": {
                    "label": default_meta["fund_name"],
                    "url": default_meta["source_url"]
                },
                "last_updated": default_meta["last_scraped"]
            }
            
        if q_type == "comparison":
            validation = self.validator.validate_and_fix(
                answer=REFUSAL_COMPARISON,
                source_url=default_meta["source_url"],
                last_scraped=default_meta["last_scraped"]
            )
            return {
                "status": "refused",
                "type": "comparison",
                "answer": validation["answer"],
                "citation": {
                    "label": default_meta["fund_name"],
                    "url": default_meta["source_url"]
                },
                "last_updated": default_meta["last_scraped"]
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


        # 3. Factual Query Pre-processing
        # AUM Multi-fund Check
        query_lower = query.lower()
        is_aum = "aum" in query_lower or "assets under management" in query_lower
        matched_funds = self.detect_funds(query)
        
        if is_aum:
            is_multi_fund_aum = (
                len(matched_funds) != 1 or 
                "all" in query_lower or 
                "highest" in query_lower or 
                "compare" in query_lower or 
                "maximum" in query_lower or
                "show" in query_lower
            )
            if is_multi_fund_aum:
                return self.handle_multi_fund_aum(query, matched_funds)

        # Missing Scheme Check
        requires_scheme, metric = self.check_requires_scheme_name(query)
        # Bypass refusal if the user has checked funds in the UI, or explicitly says "all"
        has_context_or_intent = selected_funds or "all" in query_lower or "compare" in query_lower
        if requires_scheme and not matched_funds and not has_context_or_intent:
            if metric == "expense_ratio":
                ans = "Please specify the mutual fund scheme for which you would like the expense ratio."
            elif metric == "cagr":
                ans = "Which mutual fund scheme would you like the 5-year CAGR information for?"
            elif metric == "sector_allocation":
                ans = "Which mutual fund scheme would you like the sector-wise allocation for?"
            elif metric == "benchmark":
                ans = "Which mutual fund scheme would you like the benchmark information for?"
            elif metric == "nav":
                ans = "Which mutual fund scheme would you like the NAV information for?"
            elif metric == "exit_load":
                ans = "Which mutual fund scheme would you like the exit load information for?"
            elif metric == "fund_manager":
                ans = "Which mutual fund scheme would you like the fund manager information for?"
            elif metric == "sip":
                ans = "Which mutual fund scheme would you like the minimum SIP information for?"
            elif metric == "lumpsum":
                ans = "Which mutual fund scheme would you like the minimum lumpsum information for?"
            elif metric == "riskometer":
                ans = "Which mutual fund scheme would you like the riskometer information for?"
            else:
                ans = "Which mutual fund scheme would you like information for?"

            validation = self.validator.validate_and_fix(
                answer=ans,
                source_url=default_meta["source_url"],
                last_scraped=default_meta["last_scraped"]
            )
            return {
                "status": "success",
                "type": "factual",
                "answer": validation["answer"],
                "citation": {
                    "label": default_meta["fund_name"],
                    "url": default_meta["source_url"]
                },
                "last_updated": default_meta["last_scraped"]
            }

        # 4. Standard Factual Query Processing
        if not self.retriever:
            return {
                "status": "refused",
                "type": "out_of_scope",
                "answer": "Vector database is not initialized. Please run ingestion.",
                "citation": None,
                "last_updated": None
            }
            
        # Retrieve chunks (with selected_funds filter if specified)
        chunks = self.retriever.retrieve(query, distance_threshold=1.3, selected_funds=selected_funds)
        
        if not chunks:
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
                temperature=0.0,
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

        # 5. Post-generation Output Validation & Formatting
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

