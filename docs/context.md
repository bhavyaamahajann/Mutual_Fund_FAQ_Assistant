# Mutual Fund FAQ Assistant — Project Context

## 1. Overview

Build a **facts-only FAQ assistant** for mutual fund schemes using **INDMoney** as the reference product context. The assistant answers objective, verifiable queries via a **Retrieval-Augmented Generation (RAG)** pipeline, ingesting only official public documents.

> **Disclaimer:** "Facts-only. No investment advice."

---

## 2. Selected Product & AMC

| Field | Value |
|---|---|
| **Product** | INDMoney |
| **AMC** | ICICI Prudential Mutual Fund |
| **Total Corpus Size** | 15 URLs |

---

## 3. Data Sources

The RAG corpus is built exclusively from official public sources:

- Scheme Factsheets
- Key Information Memorandums (KIMs)
- Scheme Information Documents (SIDs)
- ICICI Prudential FAQs and Help Pages
- AMFI Investor Education Resources
- SEBI Investor Education Resources

---

## 4. Corpus URLs

### Equity Funds (7)

| # | Fund Name | URL |
|---|---|---|
| 1 | ICICI Prudential Small Cap Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588) |
| 2 | ICICI Prudential Large & Mid Cap Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-large-mid-cap-fund-direct-plan-growth-2878) |
| 3 | ICICI Prudential Flexi Cap Fund – Direct Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-flexicap-fund-direct-growth-1006609) |
| 4 | ICICI Prudential Focused Equity Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-focused-equity-fund-direct-plan-growth-2797) |
| 5 | ICICI Prudential Mid Cap Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-midcap-fund-direct-plan-growth-3190) |
| 6 | ICICI Prudential Multi Cap Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-multicap-fund-direct-plan-growth-3194) |
| 7 | ICICI Prudential Large Cap Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-large-cap-fund-direct-plan-growth-2995) |

### Tax Saving Fund (1)

| # | Fund Name | URL |
|---|---|---|
| 8 | ICICI Prudential ELSS Tax Saver Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-elss-tax-saver-fund-direct-plan-growth-2693) |

### Hybrid Funds (4)

| # | Fund Name | URL |
|---|---|---|
| 9 | ICICI Prudential Equity Savings Fund – Direct Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-equity-savings-fund-direct-growth-4572) |
| 10 | ICICI Prudential Equity & Debt Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-equity-debt-fund-direct-plan-growth-4108) |
| 11 | ICICI Prudential Regular Savings Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-regular-savings-fund-direct-plan-growth-4394) |
| 12 | ICICI Prudential Multi Asset Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-multi-asset-fund-direct-plan-growth-4646) |

### Index Fund (1)

| # | Fund Name | URL |
|---|---|---|
| 13 | ICICI Prudential Nifty 50 Index Fund – Direct Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-nifty-50-index-plan-direct-growth-5536) |

### ETF Fund of Funds (2)

| # | Fund Name | URL |
|---|---|---|
| 14 | ICICI Prudential Gold ETF Fund of Fund – Direct Plan Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-gold-etf-fof-direct-plan-growth-5382) |
| 15 | ICICI Prudential Silver ETF Fund of Fund – Direct Growth | [Link](https://www.indmoney.com/mutual-funds/icici-prudential-silver-etf-fof-direct-growth-1040428) |

---

## 5. Target Users

- Retail investors comparing mutual fund schemes
- Customer support and content teams handling repetitive mutual fund queries

---

## 6. FAQ Assistant Requirements

### Supported Query Types

- Fund manager name(s)
- Expense ratio of a scheme
- Exit load details
- Minimum SIP amount
- ELSS lock-in period
- Riskometer classification
- Benchmark index
- Process to download statements or capital gains reports

> [!NOTE]
> **Fund manager details are auto-extracted** from each corpus URL during ingestion. Users can ask "Who manages the ICICI Prudential Small Cap Fund?" and receive the current fund manager name(s) with a source citation.

### Response Rules

- **Max 3 sentences** per response
- **Exactly 1 citation link** per response
- Footer: `"Last updated from sources: <date>"`

---

## 7. Refusal Handling

The assistant **must refuse** non-factual or advisory queries such as:
- *"Should I invest in this fund?"*
- *"Which fund is better?"*

Refusal responses must:
- Be polite and clearly worded
- Reinforce the facts-only limitation
- Provide a relevant educational link (e.g., AMFI or SEBI resource)

---

## 8. User Interface

- 3-column desktop dashboard (sidebar left → chat area → sidebar right)
- Landing screen with 6 suggestive question cards (collapsed fund filter on load)
- Visible disclaimer: **"Facts-only. No investment advice."**
- Chat sessions created only when the user starts a conversation

---

## 9. Constraints

### Data & Sources
- Use **only** official public sources (AMC, AMFI, SEBI)
- **No** third-party blogs or aggregator websites

### Privacy & Security
Do **not** collect, store, or process:
- PAN or Aadhaar numbers
- Account numbers
- OTPs
- Email addresses or phone numbers

### Content Restrictions
- No investment advice or recommendations
- No performance comparisons or return calculations
- For performance queries → link to official factsheet only

### Transparency
- Responses must be short, factual, and verifiable
- Every answer must include a source link and last updated date

---

## 10. Deployment Architecture (Current — as of June 2026)

| Layer | Platform | URL |
|---|---|---|
| **Frontend** | Vercel (React + Vite) | Vercel-assigned domain |
| **Backend API** | Render (Docker container) | https://mutual-fund-faq-assistant.onrender.com |
| **Vector Store** | ChromaDB (baked into Docker image at build time) | — |
| **Data Refresh** | GitHub Actions (daily 10:00 AM IST) | Commits updated `fund_metadata.json` to repo |

### Data Flow
1. **GitHub Actions** runs daily at 10:00 AM IST → scrapes IndMoney URLs → updates `fund_metadata.json` → commits to repo
2. **Render** auto-deploys on every commit → rebuilds Docker image → re-embeds metadata into ChromaDB
3. **Frontend** on Vercel calls `https://mutual-fund-faq-assistant.onrender.com/api/chat` via `VITE_API_URL` env var

---

## 11. Expected Deliverables

- **README** — Setup instructions, selected AMC & schemes, architecture overview (RAG approach), known limitations
- **Disclaimer Snippet** — `"Facts-only. No investment advice."`

---

## 12. Success Criteria

| Criterion | Description |
|---|---|
| Accuracy | Correct retrieval of factual mutual fund information |
| Facts-Only | Strict adherence to facts-only responses |
| Citations | Consistent inclusion of valid source citations |
| Refusal | Proper refusal of advisory queries |
| UI/UX | Clean, minimal, and user-friendly interface |
| Data Freshness | Fund data refreshed automatically every day at 10:00 AM IST |

---

## 13. Summary

> The goal is to build a **trustworthy, transparent, and compliant** mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. The system ensures users receive only verified, source-backed financial information — without any advisory bias or speculative content.

---

## 14. Technical Implementation Details

### API Usage
- **Groq API**: The system uses exactly **one** external API (Groq API) at runtime for LLM response generation.
- **Local Components**: Embedding generation (`BAAI/bge-small-en-v1.5`) and vector search (ChromaDB) run completely locally inside the Docker container, requiring no external APIs.

### Data Ingestion & Sourcing
- **Scraper** (`scraper.py`): A custom Python script scrapes mutual fund web pages using `curl_cffi` browser impersonation to fetch data. No external scraping APIs are used.
- **Anti-403 Strategy**: IndMoney blocks requests from cloud/Docker IPs. The daily refresh (`scrape_and_update.py`) runs on GitHub Actions (residential/GitHub IPs) which can reach IndMoney. The Docker image build uses pre-scraped `fund_metadata.json` from the repo — **no live scraping at Docker build time**.
- **Daily Scheduler** (`scrape_and_update.py`): Runs at 10:00 AM IST via GitHub Actions, fetches fresh data, updates `fund_metadata.json`, and commits back to the repo. Render auto-deploys the new commit.

### Chunking Strategy
- **Recursive Chunking**: Text is split using LangChain's `RecursiveCharacterTextSplitter` with a `chunk_size` of 500 characters and a `chunk_overlap` of 50 characters.
- **Why Recursive Chunking is Used**:
  - **Structure & Coherence**: Preserves paragraph and sentence structures.
  - **Improved Retrieval (RAG)**: Keeping semantic units whole guarantees that retrieved chunks contain complete information.
  - **Strict Size Guardrails**: Enforces size limits gracefully.
