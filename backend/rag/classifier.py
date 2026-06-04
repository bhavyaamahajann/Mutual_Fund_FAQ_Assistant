import re
import logging

logger = logging.getLogger(__name__)

# PII Regex Patterns
PAN_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', re.IGNORECASE)
AADHAAR_PATTERN = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+91|0)?[6-9]\d{9}\b')
EMAIL_PATTERN = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.IGNORECASE)
OTP_PATTERN = re.compile(r'\b\d{4,6}\b')  # Combined with OTP context keywords

# Context words for OTP classification
OTP_KEYWORDS = {"otp", "one-time password", "one time password", "verification code", "pin", "verify"}

# Advisory Intent Keywords
ADVISORY_KEYWORDS = [
    "should i", "recommend", "suggest", "worth investing", "good investment",
    "is it good", "is it safe", "how to invest", "where to invest", "best fund",
    "which fund is good", "help me choose", "financial advice", "advice",
    "give me a recommendation", "advise", "which one to buy", "should i buy"
]

# Comparison / Speculative Performance Keywords
COMPARISON_KEYWORDS = [
    "compare", "comparison", "vs", "versus", "which is better", "which one is better",
    "which fund is better", "returns comparison", "outperform", "cagr comparison", "better returns",
    "highest returns", "best performing", "will give 20%", "give 20%", "will give", "future returns", "guaranteed"
]

# Mutual Fund Scope Keywords (to check if the query is in-scope)
IN_SCOPE_KEYWORDS = [
    "fund", "nav", "expense", "exit load", "sip", "lumpsum", "benchmark", "riskometer",
    "lock-in", "manager", "aum", "house", "icici", "prudential", "smallcap", "largecap",
    "midcap", "flexicap", "focused", "multicap", "elss", "savings", "debt", "index", "gold", "silver"
]

# Greetings to handle gracefully
GREETINGS = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "namaste"}

class QueryClassifier:
    def classify(self, query: str) -> dict:
        """
        Classifies the incoming user query.
        Returns a dict: {"type": "factual" | "advisory" | "pii" | "comparison" | "out_of_scope" | "greeting"}
        """
        query_clean = query.strip()
        if not query_clean:
            return {"type": "out_of_scope"}
            
        # 1. PII Detection (PAN, Aadhaar, Phone, Email, OTP)
        if PAN_PATTERN.search(query_clean):
            logger.info("PII check triggered: PAN detected.")
            return {"type": "pii"}
            
        if AADHAAR_PATTERN.search(query_clean):
            logger.info("PII check triggered: Aadhaar detected.")
            return {"type": "pii"}
            
        if EMAIL_PATTERN.search(query_clean):
            logger.info("PII check triggered: Email detected.")
            return {"type": "pii"}
            
        if PHONE_PATTERN.search(query_clean):
            logger.info("PII check triggered: Phone number detected.")
            return {"type": "pii"}
            
        # Check OTP pattern with contextual keywords
        if OTP_PATTERN.search(query_clean):
            query_lower = query_clean.lower()
            if any(kw in query_lower for kw in OTP_KEYWORDS):
                logger.info("PII check triggered: OTP pattern in OTP context detected.")
                return {"type": "pii"}

        query_lower = query_clean.lower()

        # 2. Greetings check
        # Remove punctuation for greeting check
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        if len(query_words) <= 3 and not query_words.isdisjoint(GREETINGS):
            return {"type": "greeting"}

        # 3. Advisory Intent Detection
        if any(kw in query_lower for kw in ADVISORY_KEYWORDS):
            logger.info("Advisory intent check triggered.")
            return {"type": "advisory"}

        # 4. Comparison / Speculation Intent Detection
        if any(kw in query_lower for kw in COMPARISON_KEYWORDS):
            logger.info("Comparison/speculative returns intent check triggered.")
            return {"type": "comparison"}

        # 5. Out-of-scope Detection
        # If the query does not contain any of our key mutual fund vocabulary, mark as out-of-scope
        if not any(kw in query_lower for kw in IN_SCOPE_KEYWORDS):
            logger.info("Out of scope check triggered (no mutual fund terminology detected).")
            return {"type": "out_of_scope"}

        # Default classification
        return {"type": "factual"}
