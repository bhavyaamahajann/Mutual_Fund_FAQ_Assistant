import sys
import re
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package is in python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.app.main import app

# Terminal Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# URL Regex Pattern
URL_PATTERN = re.compile(r'https?://[^\s()<>]+')

def split_sentences(text: str) -> list[str]:
    """Splits text into sentences, ignoring decimal points in numbers."""
    raw_sentences = re.split(r'(?<!\d)\.(?!\d)|[!?]', text)
    return [s.strip() for s in raw_sentences if s.strip()]

def run_tests():
    from unittest.mock import MagicMock
    from backend.app.routes.chat import pipeline
    
    # Setup mock Groq API client
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    
    def mock_chat_create(*args, **kwargs):
        messages = kwargs.get("messages", [])
        user_msg = messages[-1]["content"] if messages else ""
        
        # Simulating factual outputs corresponding to each query.
        # We deliberately omit the source citation text and the footer
        # to verify that the pipeline's ResponseValidator successfully appends them.
        ans_text = "Factual answer from the retrieved source context."
        if "expense ratio" in user_msg.lower():
            ans_text = "The expense ratio of the ICICI Prudential Small Cap Fund is 0.66%."
        elif "exit load" in user_msg.lower():
            ans_text = "The exit load for ICICI Prudential ELSS Tax Saver Fund is Nil."
        elif "minimum sip" in user_msg.lower():
            ans_text = "The minimum SIP investment amount is Rs 100 for this fund."
        elif "fund manager" in user_msg.lower():
            ans_text = "The fund is managed by Rajat Chandak and Anish Tawakley."
        elif "benchmark" in user_msg.lower():
            ans_text = "The fund is benchmarked against Nifty 50 TRI."
        elif "riskometer" in user_msg.lower():
            ans_text = "The riskometer category for this fund is Very High."
            
        mock_choice = MagicMock()
        mock_choice.message.content = ans_text
        mock_completion.choices = [mock_choice]
        return mock_completion

    mock_client.chat.completions.create = mock_chat_create
    
    # Temporarily override live Groq client with our local mock
    original_client = pipeline.groq_client
    pipeline.groq_client = mock_client
    
    client = TestClient(app)
    
    print(f"\n{BOLD}{CYAN}=== Starting Mutual Fund FAQ Assistant End-to-End Test Suite ==={RESET}\n")

    # Define test cases
    factual_cases = [
        {
            "name": "Small Cap Fund Expense Ratio",
            "query": "What is the expense ratio of ICICI Prudential Small Cap Fund?"
        },
        {
            "name": "ELSS Tax Saver Fund Exit Load",
            "query": "What is the exit load for ICICI Prudential ELSS Tax Saver Fund?"
        },
        {
            "name": "Flexi Cap Fund Minimum SIP",
            "query": "What is the minimum SIP amount for ICICI Prudential Flexi Cap Fund?"
        },
        {
            "name": "Mid Cap Fund Manager",
            "query": "Who is the fund manager of ICICI Prudential Mid Cap Fund?"
        },
        {
            "name": "Nifty 50 Index Fund Benchmark",
            "query": "What is the benchmark index for ICICI Prudential Nifty 50 Index Fund?"
        },
        {
            "name": "Gold ETF FoF Riskometer",
            "query": "What is the riskometer category of ICICI Prudential Gold ETF FoF?"
        }
    ]

    refusal_cases = [
        {
            "name": "Advisory Intent Check",
            "query": "Should I invest in ICICI Prudential Small Cap Fund?",
            "expected_type": "advisory"
        },
        {
            "name": "Speculative Comparison Check",
            "query": "Which fund is better — Flexi Cap or Multi Cap?",
            "expected_type": "comparison"
        },
        {
            "name": "Future Returns Speculation",
            "query": "Will this fund give 20% returns?",
            "expected_type": "comparison"
        },
        {
            "name": "PII Detection (PAN)",
            "query": "My PAN is ABCDE1234F, check my portfolio.",
            "expected_type": "pii"
        }
    ]

    edge_cases = [
        {
            "name": "Empty Query Check",
            "query": "",
            "is_validation_error": True
        },
        {
            "name": "Gibberish Input Routing",
            "query": "asdfghjkl",
            "expected_status": "refused",
            "expected_type": "out_of_scope"
        },
        {
            "name": "Out of Scope Query Routing",
            "query": "What is the weather today?",
            "expected_status": "refused",
            "expected_type": "out_of_scope"
        }
    ]

    total_tests = len(factual_cases) + len(refusal_cases) + len(edge_cases)
    passed_tests = 0

    # 1. Run Factual Query Tests
    print(f"{BOLD}{YELLOW}--- 1. Running Factual Query Tests (Expecting Success) ---{RESET}")
    for tc in factual_cases:
        print(f"Test: '{tc['name']}'...")
        try:
            response = client.post("/api/chat", json={"query": tc["query"]})
            if response.status_code != 200:
                print(f"  {RED}[FAIL] Status code is {response.status_code}{RESET}")
                continue
                
            data = response.json()
            if data.get("status") != "success" or data.get("type") != "factual":
                print(f"  {RED}[FAIL] Unexpected status or type in response: {data}{RESET}")
                continue
            
            # Format validation
            answer = data.get("answer", "")
            citation = data.get("citation", {})
            last_updated = data.get("last_updated", "")
            
            # Verify footer presence
            parts = [p.strip() for p in answer.split("\n\n") if p.strip()]
            if len(parts) < 2 or "Last updated from sources:" not in parts[-1]:
                print(f"  {RED}[FAIL] Answer missing mandatory updated timestamp footer: '{answer}'{RESET}")
                continue
            
            body = "\n\n".join(parts[:-1])
            # Verify URL citation presence
            body_parts = body.split("Source:")
            if len(body_parts) < 2:
                print(f"  {RED}[FAIL] Answer missing 'Source: <url>' pattern: '{body}'{RESET}")
                continue
                
            text = body_parts[0].strip()
            source_url = body_parts[1].strip()
            
            # Check citation URL match
            if not URL_PATTERN.match(source_url):
                print(f"  {RED}[FAIL] Citation is not a valid URL: '{source_url}'{RESET}")
                continue
                
            if not citation.get("url") or citation["url"] != source_url:
                print(f"  {RED}[FAIL] Citation dictionary URL does not match response: {citation}{RESET}")
                continue
                
            # Verify sentence count (max 3 sentences)
            sentences = split_sentences(text)
            if len(sentences) > 3:
                print(f"  {RED}[FAIL] Answer exceeds 3 sentences: {len(sentences)} sentences found.{RESET}")
                continue
                
            print(f"  {GREEN}[PASS] Received sourced answer. Sentences count: {len(sentences)}. Source: {source_url}{RESET}")
            passed_tests += 1
            
        except Exception as e:
            print(f"  {RED}[FAIL] Exception: {e}{RESET}")

    # 2. Run Refusal Query Tests
    print(f"\n{BOLD}{YELLOW}--- 2. Running Refusal Intent Tests (Expecting Refusal) ---{RESET}")
    for tc in refusal_cases:
        print(f"Test: '{tc['name']}'...")
        try:
            response = client.post("/api/chat", json={"query": tc["query"]})
            if response.status_code != 200:
                print(f"  {RED}[FAIL] Status code is {response.status_code}{RESET}")
                continue
                
            data = response.json()
            if data.get("status") != "refused" or data.get("type") != tc["expected_type"]:
                print(f"  {RED}[FAIL] Expected 'refused' with type '{tc['expected_type']}'. Got status '{data.get('status')}', type '{data.get('type')}'{RESET}")
                continue
                
            print(f"  {GREEN}[PASS] Correctly intercepted: status={data['status']}, type={data['type']}. Refusal answer: '{data['answer'][:60]}...'{RESET}")
            passed_tests += 1
            
        except Exception as e:
            print(f"  {RED}[FAIL] Exception: {e}{RESET}")

    # 3. Run Edge Case Tests
    print(f"\n{BOLD}{YELLOW}--- 3. Running Edge & Out-of-Scope Tests ---{RESET}")
    for tc in edge_cases:
        print(f"Test: '{tc['name']}'...")
        try:
            response = client.post("/api/chat", json={"query": tc["query"]})
            
            if tc.get("is_validation_error"):
                if response.status_code == 422:
                    print(f"  {GREEN}[PASS] Correctly rejected empty query with 422 Validation Error.{RESET}")
                    passed_tests += 1
                else:
                    print(f"  {RED}[FAIL] Expected 422 validation error, got status code {response.status_code}{RESET}")
                continue
                
            if response.status_code != 200:
                print(f"  {RED}[FAIL] Status code is {response.status_code}{RESET}")
                continue
                
            data = response.json()
            if data.get("status") != tc["expected_status"] or data.get("type") != tc["expected_type"]:
                print(f"  {RED}[FAIL] Expected status '{tc['expected_status']}', type '{tc['expected_type']}'. Got status '{data.get('status')}', type '{data.get('type')}'{RESET}")
                continue
                
            print(f"  {GREEN}[PASS] Handled out-of-scope query: status={data['status']}, type={data['type']}. Answer: '{data['answer'][:60]}...'{RESET}")
            passed_tests += 1
            
        except Exception as e:
            print(f"  {RED}[FAIL] Exception: {e}{RESET}")

    # Restore original client
    pipeline.groq_client = original_client

    # Print Summary
    print(f"\n{BOLD}{CYAN}=== Test Summary ==={RESET}")
    success_rate = (passed_tests / total_tests) * 100
    color = GREEN if passed_tests == total_tests else RED
    print(f"{BOLD}{color}Passed: {passed_tests} / {total_tests} ({success_rate:.1f}%){RESET}\n")

    if passed_tests == total_tests:
        print(f"{GREEN}{BOLD}ALL TEST CASES COMPLETED SUCCESSFULLY!{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}SOME TEST CASES FAILED.{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
