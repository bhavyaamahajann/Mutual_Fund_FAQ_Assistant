import sys
import re
from pathlib import Path
import streamlit as st
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add project root to python path to import backend modules
sys.path.append(str(Path(__file__).resolve().parent))

from backend.rag.generator import RAGPipeline

# Page Config
st.set_page_config(
    page_title="INDMoney AI — Mutual Fund FAQ Assistant",
    page_icon="https://www.indmoney.com/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load RAG Pipeline (Cached to avoid loading sentence-transformers model repeatedly)
@st.cache_resource
def load_pipeline():
    return RAGPipeline()

pipeline = load_pipeline()

# Mapping of checkbox keys to backend fund ID identifiers
FUND_ID_MAP = {
    'Small Cap Fund': 'icici-pru-smallcap-direct-growth',
    'Large & Mid Cap': 'icici-pru-large-midcap-direct-growth',
    'Flexi Cap Fund': 'icici-pru-flexicap-direct-growth',
    'Focused Equity': 'icici-pru-focused-equity-direct-growth',
    'Mid Cap Fund': 'icici-pru-midcap-direct-growth',
    'Multi Cap Fund': 'icici-pru-multicap-direct-growth',
    'Large Cap Fund': 'icici-pru-largecap-direct-growth',
    'Equity Savings': 'icici-pru-equity-savings-direct-growth',
    'Equity & Debt': 'icici-pru-equity-debt-direct-growth',
    'Regular Savings': 'icici-pru-regular-savings-direct-growth',
    'Multi Asset Fund': 'icici-pru-multi-asset-direct-growth',
    'ELSS Tax Saver': 'icici-pru-elss-direct-growth',
    'Nifty 50 Index': 'icici-pru-nifty50-index-direct-growth',
    'Gold ETF FoF': 'icici-pru-gold-etf-fof-direct-growth',
    'Silver ETF FoF': 'icici-pru-silver-etf-fof-direct-growth'
}

# Category mappings
EQUITY_FUNDS = ['Small Cap Fund', 'Large & Mid Cap', 'Flexi Cap Fund', 'Focused Equity', 'Mid Cap Fund', 'Multi Cap Fund', 'Large Cap Fund']
HYBRID_FUNDS = ['Equity Savings', 'Equity & Debt', 'Regular Savings', 'Multi Asset Fund']
INDEX_ETFS_TAX = ['ELSS Tax Saver', 'Nifty 50 Index', 'Gold ETF FoF', 'Silver ETF FoF']

# Dynamic suggestive questions
QUESTIONS_BY_FUND = {
    'Small Cap Fund': [
        {"query": "What is the expense ratio of ICICI Prudential Small Cap Fund?", "label": "Expense ratio of Small Cap?"},
        {"query": "Who manages the ICICI Prudential Small Cap Fund?", "label": "Fund Manager: Small Cap"}
    ],
    'Large & Mid Cap': [
        {"query": "What is the minimum investment amount for ICICI Prudential Large & Mid Cap Fund?", "label": "Min investment Large & Mid Cap"}
    ],
    'Flexi Cap Fund': [
        {"query": "What is the 3-year CAGR for ICICI Prudential Flexi Cap Fund?", "label": "3-year CAGR for Flexi Cap"}
    ],
    'Focused Equity': [
        {"query": "What is the exit load for ICICI Prudential Focused Equity Fund?", "label": "Exit load for Focused Equity"}
    ],
    'Mid Cap Fund': [
        {"query": "Who are the fund managers of ICICI Prudential Mid Cap Fund?", "label": "Fund Managers: Mid Cap"}
    ],
    'Multi Cap Fund': [
        {"query": "What is the expense ratio of ICICI Prudential Multi Cap Fund?", "label": "Expense ratio: Multi Cap"}
    ],
    'Large Cap Fund': [
        {"query": "What is the AUM of ICICI Prudential Large Cap Fund?", "label": "AUM of Large Cap Fund"}
    ],
    'Equity Savings': [
        {"query": "What is the exit load of ICICI Prudential Equity Savings Fund?", "label": "Exit load: Equity Savings"}
    ],
    'Equity & Debt': [
        {"query": "What is the AUM of ICICI Prudential Equity & Debt Fund?", "label": "AUM of Equity & Debt"}
    ],
    'Regular Savings': [
        {"query": "Who manages the ICICI Prudential Regular Savings Fund?", "label": "Fund Manager: Regular Savings"}
    ],
    'Multi Asset Fund': [
        {"query": "What is the risk profile of ICICI Prudential Multi Asset Fund?", "label": "Risk profile: Multi Asset"}
    ],
    'ELSS Tax Saver': [
        {"query": "What are the tax implications for ICICI Prudential ELSS Tax Saver Fund?", "label": "Tax implications for ELSS?"},
        {"query": "What is the lock-in period for ICICI Prudential ELSS Tax Saver Fund?", "label": "Lock-in period: ELSS"}
    ],
    'Nifty 50 Index': [
        {"query": "What is the tracking error of ICICI Prudential Nifty 50 Index Fund?", "label": "Tracking error: Nifty 50 Index"}
    ],
    'Gold ETF FoF': [
        {"query": "What is the exit load of ICICI Prudential Gold ETF Fund of Fund?", "label": "Exit load: Gold ETF FoF"}
    ],
    'Silver ETF FoF': [
        {"query": "What is the minimum investment for ICICI Prudential Silver ETF Fund of Fund?", "label": "Min investment: Silver ETF FoF"}
    ]
}

DEFAULT_QUESTIONS = [
    {"query": "What is the expense ratio of ICICI Prudential Small Cap Fund?", "label": "Expense ratio of Small Cap?"},
    {"query": "What is the 3-year CAGR for ICICI Prudential Flexi Cap Fund?", "label": "3-year CAGR for Flexi Cap"},
    {"query": "What are the tax implications for ICICI Prudential ELSS Tax Saver Fund?", "label": "Tax implications for ELSS?"},
    {"query": "What is the risk profile of ICICI Prudential Multi Asset Fund?", "label": "Risk profile: Multi Asset"}
]

# Custom CSS styling for Cafe Light theme and spacing
st.markdown("""
<style>
    /* Warm Cafe Theme styling */
    .stApp {
        background-color: #f5f2eb !important;
        color: #1f2937 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header area styling */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #faf9f6 !important;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Heading typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        color: #111827 !important;
    }
    
    /* Compliance warning badge */
    .warning-badge {
        background-color: #fff7e6;
        border: 1.5px solid #ffe8cc;
        color: #92400e;
        border-radius: 9999px;
        padding: 5px 14px;
        font-size: 0.725rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 20px;
    }
    
    /* Suggestive Prompt Cards */
    .suggestive-btn {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 14px;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .suggestive-btn:hover {
        border-color: #cbd5e1;
        transform: translateY(-1.5px);
    }
    
    /* Citation pill */
    .citation-pill {
        background-color: #e0e7ff;
        color: #1d4ed8;
        border-radius: 9999px;
        padding: 3px 10px;
        font-size: 0.7rem;
        font-weight: 600;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: 8px;
    }
    .citation-pill:hover {
        background-color: #1d4ed8;
        color: #ffffff !important;
    }
    
    /* Last Scraped Date */
    .last-updated-date {
        color: #6b7280;
        font-size: 0.65rem;
        margin-top: 4px;
    }
    
    /* Refusal warning block */
    .refusal-block {
        background-color: #fff7e6;
        border: 1px solid #ffe8cc;
        color: #92400e;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
    }
    
    /* Refusal error block (PII) */
    .refusal-error {
        background-color: #fef2f2;
        border: 1px solid #fca5a5;
        color: #991b1b;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
    }
    
    /* Clean chat input styles */
    [data-testid="stChatInput"] {
        border-radius: 9999px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "session-1": [
            {"sender": "user", "text": "Hi, what can this assistant help me with?"},
            {
                "sender": "assistant",
                "text": "I am a facts-only assistant for ICICI Prudential Mutual Funds. I can provide verified details like NAV, expense ratios, exit loads, fund managers, and minimum SIP amounts based on official sources. I do not provide investment recommendations or comparisons.",
                "status": "success",
                "type": "greeting"
            }
        ]
    }
if "session_names" not in st.session_state:
    st.session_state.session_names = {
        "session-1": "Chat 1"
    }
if "active_session" not in st.session_state:
    st.session_state.active_session = "session-1"

# Sidebar Branding Logo (matching request exactly: royal blue text, light blue/lavender AI badge, no SVG)
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; padding-bottom: 10px; margin-bottom: 15px; border-bottom: 1px solid #e5e7eb;">
  <span style="font-size: 1.5rem; color: #1d4ed8; font-weight: 750; font-family: 'Outfit', sans-serif; letter-spacing: -0.02em;">
    INDMoney
  </span>
  <span style="background-color: #e0e7ff; color: #1d4ed8; font-size: 0.95rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-family: 'Outfit', sans-serif; display: inline-block;">
    AI
  </span>
</div>
""", unsafe_allow_html=True)

# New Chat Button
if st.sidebar.button("➕ New Chat", use_container_width=True):
    new_id = f"session-{int(datetime.now().timestamp() * 1000)}"
    st.session_state.sessions[new_id] = []
    st.session_state.session_names[new_id] = f"Chat {len(st.session_state.sessions)}"
    st.session_state.active_session = new_id
    st.rerun()

# Recent Conversations Thread List
st.sidebar.subheader("Recent Conversations")
for sess_id in list(st.session_state.sessions.keys()):
    col1, col2, col3 = st.sidebar.columns([6, 2, 2])
    
    # Session Selection
    current_name = st.session_state.session_names.get(sess_id, sess_id)
    is_active = (st.session_state.active_session == sess_id)
    
    with col1:
        if is_active:
            st.markdown(f"**💬 {current_name}**")
        else:
            if st.button(f"💬 {current_name}", key=f"btn-select-{sess_id}", help="Switch to chat"):
                st.session_state.active_session = sess_id
                st.rerun()
                
    # Rename & Delete
    with col2:
        # Use an expander for inline rename to fit Streamlit structure cleanly
        with st.popover("✏️", help="Rename conversation"):
            new_name = st.text_input("New Name", value=current_name, key=f"rename-in-{sess_id}")
            if st.button("Save", key=f"save-name-{sess_id}"):
                if new_name.strip():
                    st.session_state.session_names[sess_id] = new_name.strip()
                    st.rerun()
                    
    with col3:
        if st.button("🗑️", key=f"btn-del-{sess_id}", help="Delete conversation"):
            del st.session_state.sessions[sess_id]
            if sess_id in st.session_state.session_names:
                del st.session_state.session_names[sess_id]
            if st.session_state.active_session == sess_id:
                keys = list(st.session_state.sessions.keys())
                st.session_state.active_session = keys[-1] if keys else None
            st.rerun()

# 15 Mutual Fund Checkboxes (Left Sidebar Filters)
st.sidebar.markdown("<br><hr style='margin: 10px 0;'>", unsafe_allow_html=True)
st.sidebar.subheader("📁 ICICI PRUDENTIAL MF")

# Collect Checked schemes
selected_schemes = []

with st.sidebar.expander("Equity Funds", expanded=True):
    for scheme in EQUITY_FUNDS:
        # Default Small Cap checked as per app behavior
        default_val = (scheme == 'Small Cap Fund')
        if st.checkbox(scheme, value=default_val, key=f"chk-{scheme}"):
            selected_schemes.append(scheme)

with st.sidebar.expander("Hybrid Funds", expanded=False):
    for scheme in HYBRID_FUNDS:
        if st.checkbox(scheme, value=False, key=f"chk-{scheme}"):
            selected_schemes.append(scheme)

with st.sidebar.expander("Index, ETFs & Tax", expanded=False):
    for scheme in INDEX_ETFS_TAX:
        if st.checkbox(scheme, value=False, key=f"chk-{scheme}"):
            selected_schemes.append(scheme)

# Map checked schemes to fund IDs
selected_fund_ids = [FUND_ID_MAP[name] for name in selected_schemes if name in FUND_ID_MAP]

# Main Area Header / Compliance warning badge (aligned right)
h_col1, h_col2 = st.columns([7, 3])
with h_col2:
    st.markdown("""
    <div style="text-align: right;">
        <span class="warning-badge">⚠️ Facts-Only. No Investment Advice.</span>
    </div>
    """, unsafe_allow_html=True)

# Main Chat display
active_sess = st.session_state.active_session
messages = st.session_state.sessions.get(active_sess, []) if active_sess else []

# Function to submit queries to the RAG pipeline
def submit_query(query_text):
    if not query_text.strip():
        return
    
    # 1. Add user query to conversation
    st.session_state.sessions[active_sess].append({"sender": "user", "text": query_text})
    
    # 2. Query RAG pipeline
    with st.spinner("Analyzing factsheets..."):
        # If no schemes checked, pass None (defaults to all)
        pass_filter = selected_fund_ids if selected_fund_ids else None
        response_data = pipeline.generate_response(query_text, selected_funds=pass_filter)
        
    # 3. Add assistant response
    st.session_state.sessions[active_sess].append({
        "sender": "assistant",
        "text": response_data.get("answer", ""),
        "status": response_data.get("status", "success"),
        "type": response_data.get("type", "factual"),
        "citation": response_data.get("citation"),
        "last_updated": response_data.get("last_updated")
    })
    st.rerun()

# Welcome screen if session is empty
if not messages:
    st.markdown("<h1 style='text-align: center;'>How can I help you today?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280; font-size: 1rem;'>Ask me anything about ICICI Prudential funds, expense ratios, tax implications, or performance data.</p><br>", unsafe_allow_html=True)
    
    # Dynamic Suggestive Prompt Grid
    # Collect suggestions for active selections
    dynamic_suggestions = []
    if len(selected_schemes) == 0 or len(selected_schemes) == len(FUND_ID_MAP):
        dynamic_suggestions = DEFAULT_QUESTIONS
    else:
        for name in selected_schemes:
            if name in QUESTIONS_BY_FUND:
                dynamic_suggestions.extend(QUESTIONS_BY_FUND[name])
                
    # Limit to 4 cards
    suggestions_to_show = dynamic_suggestions[:4]
    
    # Draw suggestive prompt grid buttons in columns
    cols = st.columns(2)
    for idx, card in enumerate(suggestions_to_show):
        with cols[idx % 2]:
            # Styled card button
            st.markdown(f"""
            <div style="background-color: #ffffff; border: 1.5px solid #e5e7eb; border-radius: 12px; padding: 16px; min-height: 90px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <p style="font-family: 'Inter', sans-serif; font-weight: 600; color: #111827; margin: 0 0 4px 0; font-size: 0.9rem;">{card['label']}</p>
                <span style="font-size: 0.65rem; color: #6b7280; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">SUGGESTION</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Ask Query", key=f"prompt-card-{idx}", use_container_width=True):
                submit_query(card['query'])
else:
    # Render chat log
    for msg in messages:
        if msg["sender"] == "user":
            with st.chat_message("user"):
                st.write(msg["text"])
        else:
            with st.chat_message("assistant"):
                if msg.get("status") == "refused":
                    # Refusal UI mapping (colored warning panel layout)
                    bg_class = "refusal-error" if msg.get("type") == "pii" else "refusal-block"
                    title = "PII Security Block" if msg.get("type") == "pii" else "Regulatory Notice"
                    st.markdown(f"""
                    <div class="{bg_class}">
                        <h4 style="margin: 0 0 6px 0; font-weight: 700; font-size: 0.9rem;">{title}</h4>
                        <p style="margin: 0; font-size: 0.8rem; line-height: 1.4;">{msg['text']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Refusal Action educational redirect links
                    if msg.get("type") == "advisory":
                        st.markdown("[Visit AMFI Investor Education ↗](https://www.amfiindia.com/investor-corner/education/interest-rates.html)")
                    elif msg.get("type") == "comparison":
                        st.markdown("[Visit SEBI Portal ↗](https://www.sebi.gov.in)")
                else:
                    # Clean fact response text
                    st.write(msg["text"])
                    
                    # Sourced citation card and last updated stamp
                    citation = msg.get("citation")
                    last_updated = msg.get("last_updated")
                    if citation or last_updated:
                        meta_cols = st.columns([6, 4])
                        with meta_cols[0]:
                            if citation:
                                label = citation.get("label", "Factsheet Source")
                                url = citation.get("url", "https://www.indmoney.com")
                                st.markdown(f"<a href='{url}' target='_blank' class='citation-pill'>📁 {label}</a>", unsafe_allow_html=True)
                        with meta_cols[1]:
                            if last_updated and last_updated != "Not available":
                                try:
                                    dt = datetime.fromisoformat(last_updated)
                                    friendly_date = dt.strftime("%d %b %Y")
                                except Exception:
                                    friendly_date = last_scraped[:10]
                                st.markdown(f"<div style='text-align: right;' class='last-updated-date'>Updated: {friendly_date}</div>", unsafe_allow_html=True)

# Stacked selection pill container (shows selected count and pills dynamically)
active_count = len(selected_schemes)
st.markdown("<br><hr style='margin: 10px 0;'>", unsafe_allow_html=True)

# Horizontal display of active selected badge options
pill_cols = st.columns([1.5, 8.5])
with pill_cols[0]:
    st.markdown(f"**Selected: [ {active_count} ]**")
with pill_cols[1]:
    # Display pills. Clicking a pill removes it (unchecks checkbox via session state)
    pill_html = ""
    for name in selected_schemes:
        pill_html += f"""
        <span style="display: inline-flex; align-items: center; gap: 4px; background-color: #e0e7ff; color: #1d4ed8; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 500; border: 1px solid #e5e7eb; margin-right: 6px;">
            {name}
        </span>
        """
    st.markdown(pill_html, unsafe_allow_html=True)

# Chat Input at the bottom
query_input = st.chat_input("Type your financial question here...")
if query_input:
    if not active_sess:
        # Create a fallback chat session if none active
        active_sess = f"session-{int(datetime.now().timestamp() * 1000)}"
        st.session_state.sessions[active_sess] = []
        st.session_state.session_names[active_sess] = "Chat 1"
        st.session_state.active_session = active_sess
    submit_query(query_input)

# Footer row with link modals/expanders
st.markdown("<br>", unsafe_allow_html=True)
foot_col1, foot_col2 = st.columns([5, 5])
with foot_col1:
    st.markdown("<span style='color: #6b7280; font-size: 0.725rem;'>🕒 Last updated from official AMC sources.</span>", unsafe_allow_html=True)
with foot_col2:
    # Compliance modal tabs
    with st.expander("ℹ️ Compliance & Privacy Details"):
        st.markdown("""
        **1. Zero PII Retention Guardrail**
        * PAN/Aadhaar/Phone numbers are identified and immediately quarantined before reaching the language models.
        
        **2. Strict Isolation**
        * Retrieval strictly accesses official public factsheet context parsed from verified URLs. No portfolio transaction connections exist.
        
        **3. Facts-Only Limit**
        * All completions are strictly restricted to factual answers under 3 sentences. Advisory/speculative investment checks trigger refusals.
        """)
