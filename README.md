# Mutual Fund FAQ Assistant

> **Facts-only. No investment advice.**

A lightweight RAG-based FAQ assistant for ICICI Prudential Mutual Fund schemes, built with INDMoney as the reference product context.

## Overview

This assistant answers **factual, verifiable queries** about mutual fund schemes using a curated corpus of 15 official public URLs. Every response is limited to 3 sentences, includes a single source citation, and never provides investment advice.

## Selected AMC & Schemes

- **AMC:** ICICI Prudential Mutual Fund
- **Product:** INDMoney
- **Corpus:** 15 fund URLs across Equity, Hybrid, Tax Saving, Index, and ETF FoF categories

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML + CSS + JavaScript |
| Backend | Python (FastAPI) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | ChromaDB (local) |
| LLM | OpenAI GPT-4o-mini |
| Scheduler | GitHub Actions (daily cron) |

## Setup

### 1. Clone & Install

```bash
git clone <repo-url>
cd "Mutual Fund FAQ Assistant"
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Ingestion

```bash
python scripts/ingest.py
```

### 4. Start Server

```bash
uvicorn backend.app.main:app --reload
```

### 5. Open UI

Open `frontend/index.html` in your browser, or navigate to `http://localhost:8000`.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system design.

## Disclaimer

> **This assistant provides factual information only.** It does not offer investment advice, opinions, or recommendations. All responses are sourced from official public documents. For personalised advice, consult a SEBI-registered financial advisor.

## License

MIT
