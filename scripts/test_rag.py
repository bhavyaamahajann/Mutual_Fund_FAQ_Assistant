import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

# Ensure backend package is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.app.config import settings
from backend.rag.classifier import QueryClassifier
from backend.rag.retriever import VectorRetriever
from backend.rag.validator import ResponseValidator
from backend.rag.generator import RAGPipeline
from backend.rag.prompts import (
    REFUSAL_PII,
    REFUSAL_ADVISORY,
    REFUSAL_COMPARISON,
    REFUSAL_OUT_OF_SCOPE,
    REFUSAL_GREETING
)

class TestRAGPipeline(unittest.TestCase):

    def setUp(self):
        self.classifier = QueryClassifier()
        self.validator = ResponseValidator()
        
        # We try to load retriever, but skip assertions if DB is empty
        try:
            self.retriever = VectorRetriever()
        except Exception:
            self.retriever = None

    def test_classifier_pii(self):
        """Verify that PAN, Aadhaar, Phone, Email, and OTP inputs are classified as PII."""
        # PAN Card
        self.assertEqual(self.classifier.classify("My PAN card is ABCDE1234F")["type"], "pii")
        # Aadhaar Card
        self.assertEqual(self.classifier.classify("Aadhaar: 1234 5678 9012")["type"], "pii")
        # Email
        self.assertEqual(self.classifier.classify("Contact me at test@example.com")["type"], "pii")
        # Phone
        self.assertEqual(self.classifier.classify("My phone is +919876543210")["type"], "pii")
        # OTP context
        self.assertEqual(self.classifier.classify("My verification code is 4829")["type"], "pii")
        self.assertEqual(self.classifier.classify("enter otp 123456")["type"], "pii")

    def test_classifier_advisory(self):
        """Verify that advisory queries are detected."""
        self.assertEqual(self.classifier.classify("Should I buy ICICI Prudential Small Cap Fund?")["type"], "advisory")
        self.assertEqual(self.classifier.classify("Which is the best fund for long term investment?")["type"], "advisory")
        self.assertEqual(self.classifier.classify("Please suggest a good mutual fund to invest in")["type"], "advisory")

    def test_classifier_comparison(self):
        """Verify that comparison and returns speculation queries are detected."""
        self.assertEqual(self.classifier.classify("Compare ICICI Prudential Small Cap vs Large Cap Fund")["type"], "comparison")
        self.assertEqual(self.classifier.classify("which is better: flexicap or focused fund?")["type"], "comparison")
        self.assertEqual(self.classifier.classify("will this fund give 25% future returns?")["type"], "comparison")

    def test_classifier_greeting(self):
        """Verify that greetings are parsed."""
        self.assertEqual(self.classifier.classify("Hello!")["type"], "greeting")
        self.assertEqual(self.classifier.classify("hi there")["type"], "greeting")

    def test_classifier_out_of_scope(self):
        """Verify that queries with no mutual fund context are marked out of scope."""
        self.assertEqual(self.classifier.classify("What is the weather today in Mumbai?")["type"], "out_of_scope")
        self.assertEqual(self.classifier.classify("How do you bake a sourdough bread?")["type"], "out_of_scope")

    def test_classifier_factual(self):
        """Verify that valid factual questions are marked factual."""
        self.assertEqual(self.classifier.classify("What is the expense ratio of ICICI Prudential Smallcap Fund?")["type"], "factual")
        self.assertEqual(self.classifier.classify("Who is the fund manager of ICICI Prudential Flexicap Fund?")["type"], "factual")

    def test_validator_sentence_truncation(self):
        """Verify that answers with more than 3 sentences are truncated."""
        long_answer = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."
        source_url = "https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund"
        
        result = self.validator.validate_and_fix(long_answer, source_url, "2026-06-04T17:00:00")
        
        sentences = self.validator.split_sentences(result["answer"])
        # We expect 3 sentences, plus the citation if appended, and the footer is appended at the end of the text.
        # Since footer is appended with double newlines, split_sentences will split on footer's period.
        # Let's clean the footer for checking.
        clean_ans = result["answer"].split("\n\n")[0]
        # Remove citation URL and "Source: " prefix for sentence counting check
        clean_ans_no_url = clean_ans.replace(f"Source: {source_url}", "").replace(source_url, "").replace("Source:", "").strip()
        clean_sentences = self.validator.split_sentences(clean_ans_no_url)
        self.assertLessEqual(len(clean_sentences), 3)
        self.assertTrue(result["truncated"])



    def test_validator_citation_injection(self):
        """Verify that citation is added if missing."""
        no_citation_answer = "The exit load of the fund is 1.0% if redeemed within 1 year."
        source_url = "https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund"
        
        result = self.validator.validate_and_fix(no_citation_answer, source_url, "2026-06-04T17:00:00")
        
        self.assertTrue(result["citations_fixed"])
        self.assertIn(source_url, result["answer"])

    def test_validator_footer_injection(self):
        """Verify that the footer with correct date format is appended."""
        answer = "The NAV of the fund is ₹96.44. Source: https://www.indmoney.com/mutual-funds/icici"
        source_url = "https://www.indmoney.com/mutual-funds/icici"
        iso_date = "2026-06-03T17:24:02.430604"
        
        result = self.validator.validate_and_fix(answer, source_url, iso_date)
        
        self.assertTrue(result["footer_added"])
        self.assertIn("Last updated from sources: 03 Jun 2026", result["answer"])

    def test_retriever_execution(self):
        """Verify that the retriever returns chunks when DB is populated."""
        if not self.retriever:
            self.skipTest("Retriever DB not initialized.")
            
        chunks = self.retriever.retrieve("What is the NAV of ICICI Prudential Smallcap Fund?", top_k=1)
        if not chunks:
            self.skipTest("ChromaDB is empty. Run ingestion first.")
            
        self.assertGreater(len(chunks), 0)
        self.assertIn("icici", chunks[0]["metadata"]["fund_id"])
        self.assertIsNotNone(chunks[0]["text"])

    def test_retriever_filtering(self):
        """Verify that retriever restricts results when selected_funds is provided."""
        if not self.retriever:
            self.skipTest("Retriever DB not initialized.")
            
        # Retrieve with filter for smallcap
        chunks_smallcap = self.retriever.retrieve(
            "What is the NAV or expense ratio?",
            top_k=5,
            selected_funds=["icici-pru-smallcap-direct-growth"]
        )
        for chunk in chunks_smallcap:
            self.assertEqual(chunk["metadata"]["fund_id"], "icici-pru-smallcap-direct-growth")

        # Retrieve with filter for index fund
        chunks_index = self.retriever.retrieve(
            "What is the NAV or expense ratio?",
            top_k=5,
            selected_funds=["icici-pru-nifty50-index-direct-growth"]
        )
        for chunk in chunks_index:
            self.assertEqual(chunk["metadata"]["fund_id"], "icici-pru-nifty50-index-direct-growth")


    @patch('backend.rag.generator.Groq')
    def test_pipeline_factual_mocked(self, mock_groq_class):
        """Verify the full RAG pipeline flow with a mocked Groq API client."""
        # Setup mock Groq response
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        
        mock_choice = MagicMock()
        mock_choice.message.content = "The expense ratio is 0.66%. Source: https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588"
        mock_completion.choices = [mock_choice]
        
        # Test pipeline
        pipeline = RAGPipeline()
        # Force set groq_client to our mock client
        pipeline.groq_client = mock_client
        
        if not pipeline.retriever:
            self.skipTest("Retriever database not populated.")
            
        res = pipeline.generate_response("What is the expense ratio of ICICI Prudential Smallcap Fund?")
        
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["type"], "factual")
        self.assertIn("0.66%", res["answer"])
        self.assertIn("Last updated from sources:", res["answer"])
        self.assertEqual(res["citation"]["url"], "https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588")

    def test_pipeline_refusal_advisory(self):
        """Verify that advisory queries are intercepted and return predefined refusal responses."""
        pipeline = RAGPipeline()
        res = pipeline.generate_response("Should I invest in ICICI Prudential Smallcap Fund?")
        
        self.assertEqual(res["status"], "refused")
        self.assertEqual(res["type"], "advisory")
        self.assertEqual(res["answer"], REFUSAL_ADVISORY)
        self.assertIsNone(res["citation"])

    def test_pipeline_refusal_pii(self):
        """Verify that queries containing PII are intercepted and return privacy refusals."""
        pipeline = RAGPipeline()
        res = pipeline.generate_response("My email is fraud@gmail.com, find my account.")
        
        self.assertEqual(res["status"], "refused")
        self.assertEqual(res["type"], "pii")
        self.assertEqual(res["answer"], REFUSAL_PII)
        self.assertIsNone(res["citation"])

if __name__ == "__main__":
    unittest.main()
