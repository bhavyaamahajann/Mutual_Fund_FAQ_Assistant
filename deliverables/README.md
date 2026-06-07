# Mutual Fund FAQ Assistant

> **Facts-only. No investment advice.**

A lightweight RAG-based FAQ assistant for ICICI Prudential Mutual Fund schemes, built with INDMoney as the reference product context.

## 1. Scope (AMC + Schemes)

- **AMC:** ICICI Prudential Mutual Fund
- **Reference Brand UI:** INDMoney
- **Supported Schemes (15):**
  1. ICICI Prudential Small Cap Fund
  2. ICICI Prudential Large & Mid Cap Fund
  3. ICICI Prudential Flexi Cap Fund
  4. ICICI Prudential Focused Equity Fund
  5. ICICI Prudential Mid Cap Fund
  6. ICICI Prudential Multi Cap Fund
  7. ICICI Prudential Large Cap Fund
  8. ICICI Prudential Equity Savings Fund
  9. ICICI Prudential Equity & Debt Fund
  10. ICICI Prudential Regular Savings Fund
  11. ICICI Prudential Multi Asset Fund
  12. ICICI Prudential ELSS Tax Saver Fund
  13. ICICI Prudential Nifty 50 Index Fund
  14. ICICI Prudential Gold ETF FoF
  15. ICICI Prudential Silver ETF FoF

## 2. Setup Steps

If you are running the project locally:

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key

### Installation

```bash
git clone https://github.com/bhavyaamahajann/Mutual_Fund_FAQ_Assistant.git
cd "Mutual Fund FAQ Assistant"

# 1. Backend Setup
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 2. Add API Key
cp .env.example .env
# Edit .env and insert your GROQ_API_KEY

# 3. Build Frontend
cd frontend
npm install
npm run build
cd ..

# 4. Start Server
uvicorn backend.app.main:app --reload
```
The application will be running at `http://localhost:8000`.

## 3. Known Limitations

- **Source Limitations:** The assistant strictly answers from the parsed text of the 15 selected INDMoney pages. If the specific fact (e.g., tracking error, alpha) is not on the source page, it cannot provide an answer.
- **LLM Hallucination Safeguards:** While the LLM is prompted strictly to stick to context, highly complex multi-fund analytical queries might occasionally trigger default model reasoning.
- **Web Scraping Stability:** If INDMoney changes their DOM structure or Cloudflare blocks the request, the ingestion scraper may fail and require updates to the parser. (Currently handled via robust headers and daily GitHub Actions cron).
- **Latency on Cold Starts:** The free-tier backend on Render spins down after 15 minutes of inactivity. The first query after a cold start may take up to 45 seconds to process.
