import sys
from pathlib import Path
import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Ensure backend package is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.app.main import app

class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Verify that GET /api/health returns 200 and valid JSON data."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        self.assertEqual(data["llm_provider"], "Groq")

    def test_chat_empty_query_rejected(self):
        """Verify that an empty query or missing field returns 422 validation error."""
        # Empty string query
        response = self.client.post("/api/chat", json={"query": ""})
        self.assertEqual(response.status_code, 422)

        # Missing query field entirely
        response = self.client.post("/api/chat", json={"session_id": "123"})
        self.assertEqual(response.status_code, 422)

    def test_chat_query_too_long_rejected(self):
        """Verify that queries exceeding 500 characters are rejected with 422 validation error."""
        long_query = "a" * 501
        response = self.client.post("/api/chat", json={"query": long_query})
        self.assertEqual(response.status_code, 422)

    def test_cors_headers_present(self):
        """Verify CORS headers are returned in responses."""
        response = self.client.get("/api/health", headers={"Origin": "http://localhost:3000"})
        self.assertIn("access-control-allow-origin", response.headers)

        self.assertEqual(response.headers["access-control-allow-origin"], "*")

    def test_chat_non_factual_routing(self):
        """Verify that non-factual inputs (like advisory) return a refusal response without calling Groq."""
        # Advisory check should trigger directly in generator without mock completions needed
        response = self.client.post("/api/chat", json={"query": "Should I invest in small cap funds?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "refused")
        self.assertEqual(data["type"], "advisory")
        self.assertIn("cannot provide investment advice", data["answer"])

    @patch('backend.rag.generator.Groq')
    def test_chat_factual_mocked(self, mock_groq_class):
        """Verify that factual queries return 200 and follow ChatResponse structure when mocked."""
        # Setup mock Groq response
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        
        mock_choice = MagicMock()
        mock_choice.message.content = "ICICI Prudential Small Cap Fund is a high-risk equity scheme. Source: https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588"
        mock_completion.choices = [mock_choice]

        # Trigger RAG pipeline call
        # Since TestClient runs in process, patching RAGPipeline's Groq instance is handled by the mock patch
        with patch('backend.app.routes.chat.pipeline.groq_client', mock_client):
            response = self.client.post("/api/chat", json={"query": "What is the exit load of ICICI Smallcap?"})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["type"], "factual")
            self.assertIn("Source: https://www.indmoney.com", data["answer"])
            self.assertEqual(data["citation"]["url"], "https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588")

if __name__ == "__main__":
    unittest.main()
