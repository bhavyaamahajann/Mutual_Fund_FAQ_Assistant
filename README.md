# Mutual Fund FAQ Assistant

> **Facts-only. No investment advice.**

A lightweight RAG-based FAQ assistant for ICICI Prudential Mutual Fund schemes, built with INDMoney as the reference product context.

## Overview

This assistant answers **factual, verifiable queries** about mutual fund schemes using a curated corpus of 15 official public URLs. Every response is limited to 3 sentences, includes a single source citation, and never provides investment advice.

## Selected AMC & 15 Schemes

- **AMC:** ICICI Prudential Mutual Fund
- **Reference Brand UI:** INDMoney
- **Supported Schemes:**
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

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Vanilla CSS (Warm Cafe Light Theme) |
| Backend | Python (FastAPI) |
| Embeddings | `BAAI/bge-large-en-v1.5` (Local HuggingFace Transformers) |
| Vector Store | ChromaDB (local persistence) |
| LLM | Groq LLaMA-3.3-70b-versatile |
| Scheduler | GitHub Actions (daily cron) |

## Setup

### 1. Clone & Install

```bash
git clone https://github.com/bhavyaamahajann/Mutual_Fund_FAQ_Assistant.git
cd "Mutual Fund FAQ Assistant"
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Run Ingestion

```bash
python scripts/ingest.py
```

### 4. Build Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. Start Server (FastAPI + React UI)

```bash
uvicorn backend.app.main:app --reload
```
Navigate to `http://localhost:8000` to interact with the React web assistant.

### 6. Run via Streamlit (Alternative UI)

You can run the assistant in a single command using Streamlit:

```bash
streamlit run app_streamlit.py
```
This will open the Streamlit interface in your browser at `http://localhost:8501`.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system design.

## Disclaimer

> **This assistant provides factual information only.** It does not offer investment advice, opinions, or recommendations. All responses are sourced from official public documents. For personalised advice, consult a SEBI-registered financial advisor.

## License

MIT
