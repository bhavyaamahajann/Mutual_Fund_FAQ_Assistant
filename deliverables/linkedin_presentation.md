# Building a Facts-Only GenAI Mutual Fund Assistant

**Slide 1: The Problem**
General-purpose LLMs are great, but in fintech, hallucination isn't just an annoyance—it's a regulatory risk. If you ask an AI for mutual fund metrics, it might invent numbers or accidentally give illegal investment advice.

**Slide 2: The Solution**
I built a specialized **Retrieval-Augmented Generation (RAG)** Assistant strictly bound to 15 ICICI Prudential Mutual Fund schemes. 
It operates under a "Facts-Only, No Advice" mandate, ensuring every answer is backed by verifiable, up-to-date data.

**Slide 3: How It Works**
⚙️ **Data Ingestion:** A custom scraper pulls daily, fresh data from INDMoney using GitHub Actions.
🧠 **Embeddings & Vector Store:** The text is chunked and embedded using BAAI/bge-large-en-v1.5 and stored locally in ChromaDB.
🤖 **LLM Guardrails:** A Groq-powered LLaMA 3.3 model answers the queries.
🛡️ **Validator Pipeline:** Strict regex validation blocks PII (like PAN/Aadhaar) and refuses predictive or advisory questions.

**Slide 4: Key Features**
✅ **100% Verifiable:** Every factual response includes a direct hyperlink to the source page.
✅ **Context-Aware Sidebar:** Users can check/uncheck specific funds in the UI to instantly filter the AI's knowledge base.
✅ **Conversational Memory:** It remembers what you just asked! If you say "What about the exit load?", it knows exactly which fund you were talking about.

**Slide 5: Tech Stack**
- **Frontend:** React + Vite (Custom warm-cafe design)
- **Backend:** Python + FastAPI
- **AI/Vector DB:** ChromaDB + HuggingFace Sentence Transformers + Groq
- **DevOps:** Render (Backend), Vercel (Frontend), GitHub Actions (Cron Scheduler)

**Slide 6: Check it out!**
I'm incredibly proud of how this blends modern GenAI with strict regulatory and factual constraints. 
🔗 **Live Demo:** [https://mutual-fund-faq-assistant.vercel.app/](https://mutual-fund-faq-assistant.vercel.app/)
💻 **GitHub Repo:** [https://github.com/bhavyaamahajann/Mutual_Fund_FAQ_Assistant](https://github.com/bhavyaamahajann/Mutual_Fund_FAQ_Assistant)

#GenAI #RAG #Fintech #Python #React #OpenSource #MachineLearning
