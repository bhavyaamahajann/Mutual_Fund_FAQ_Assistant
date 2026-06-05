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

# Page Config (Cafe Light theme settings)
st.set_page_config(
    page_title="INDMoney AI — Mutual Fund FAQ Assistant",
    page_icon="https://www.indmoney.com/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load RAG Pipeline (Cached)
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
if "renaming_session" not in st.session_state:
    st.session_state.renaming_session = None

# Initialize checkbox state in session state before anything else
for category in [EQUITY_FUNDS, HYBRID_FUNDS, INDEX_ETFS_TAX]:
    for scheme in category:
        key = f"chk-{scheme}"
        if key not in st.session_state:
            st.session_state[key] = (scheme == 'Small Cap Fund')

# Collect Checked Schemes from session state directly
selected_schemes = []
for category in [EQUITY_FUNDS, HYBRID_FUNDS, INDEX_ETFS_TAX]:
    for scheme in category:
        key = f"chk-{scheme}"
        if st.session_state.get(key, False):
            selected_schemes.append(scheme)

# Map checked schemes to fund IDs
selected_fund_ids = [FUND_ID_MAP[name] for name in selected_schemes if name in FUND_ID_MAP]

# ----------------- STATE MACHINE USING QUERY PARAMS -----------------
params = st.query_params

# Handle uncheck action from selected pills
if "uncheck" in params:
    uncheck_val = params["uncheck"]
    key = f"chk-{uncheck_val}"
    if key in st.session_state:
        st.session_state[key] = False
    st.query_params.clear()
    st.rerun()

# Handle New Chat Trigger
if "new_chat" in params:
    new_id = f"session-{int(datetime.now().timestamp() * 1000)}"
    st.session_state.sessions[new_id] = []
    st.session_state.session_names[new_id] = f"Chat {len(st.session_state.sessions) + 1}"
    st.session_state.active_session = new_id
    st.query_params.clear()
    st.rerun()

# Handle Select Session Trigger
if "session" in params:
    sess_val = params["session"]
    if sess_val in st.session_state.sessions:
        st.session_state.active_session = sess_val
    st.query_params.clear()
    st.rerun()

# Handle Delete Session Trigger
if "delete" in params:
    del_val = params["delete"]
    if del_val in st.session_state.sessions:
        del st.session_state.sessions[del_val]
        if del_val in st.session_state.session_names:
            del st.session_state.session_names[del_val]
        if st.session_state.active_session == del_val:
            keys = list(st.session_state.sessions.keys())
            st.session_state.active_session = keys[-1] if keys else None
    st.query_params.clear()
    st.rerun()

# Handle Rename Trigger
if "trigger_rename" in params:
    st.session_state.renaming_session = params["trigger_rename"]
    st.query_params.clear()
    st.rerun()

# Handle Ask Question Trigger (Suggestive prompts or recently asked)
if "ask" in params:
    ask_val = params["ask"]
    if not st.session_state.active_session:
        new_id = f"session-{int(datetime.now().timestamp() * 1000)}"
        st.session_state.sessions[new_id] = []
        st.session_state.session_names[new_id] = "Chat 1"
        st.session_state.active_session = new_id
    
    active_sess = st.session_state.active_session
    st.session_state.sessions[active_sess].append({"sender": "user", "text": ask_val})
    
    # Run pipeline
    pass_filter = selected_fund_ids if selected_fund_ids else None
    response_data = pipeline.generate_response(ask_val, selected_funds=pass_filter)
    
    st.session_state.sessions[active_sess].append({
        "sender": "assistant",
        "text": response_data.get("answer", ""),
        "status": response_data.get("status", "success"),
        "type": response_data.get("type", "factual"),
        "citation": response_data.get("citation"),
        "last_updated": response_data.get("last_updated")
    })
    st.query_params.clear()
    st.rerun()


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
    {"query": "Who manages the ICICI Prudential Small Cap Fund?", "label": "Fund Manager: Small Cap"},
    {"query": "What is the 3-year CAGR for ICICI Prudential Flexi Cap Fund?", "label": "3-year CAGR for Flexi Cap"},
    {"query": "What are the tax implications for ICICI Prudential ELSS Tax Saver Fund?", "label": "Tax implications for ELSS?"},
    {"query": "What is the risk profile of ICICI Prudential Multi Asset Fund?", "label": "Risk profile: Multi Asset"},
    {"query": "What is the exit load for ICICI Prudential Focused Equity Fund?", "label": "Exit load for Focused Equity"}
]

# Helper function to render raw HTML safely using st.html
def render_html(html_str: str, sidebar: bool = False):
    if sidebar:
        st.sidebar.html(html_str)
    else:
        st.html(html_str)

# Custom CSS styling for Cafe Light Theme and structure overrides
st.html("""
<style>
    /* Premium Cafe Light Theme */
    .stApp {
        background-color: #f5f2eb !important;
        color: #1f2937 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header background removal */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Sidebar styling overrides */
    section[data-testid="stSidebar"] {
        background-color: #faf9f6 !important;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Input field styling */
    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 9999px !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03) !important;
        max-width: 640px !important;
        margin: 0 auto !important;
    }
    
    /* Heading Fonts */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        color: #111827 !important;
    }
    
    /* Remove padding around main container */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Expander styling to match Cafe Light theme */
    div[data-testid="stExpander"], .stExpander {
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid #e5e7eb !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        margin-bottom: 10px !important;
        padding: 0 !important;
    }
    div[data-testid="stExpander"] details, .stExpander details {
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
    }
    div[data-testid="stExpander"] [data-testid="stExpanderToggle"], .stExpander [data-testid="stExpanderToggle"] {
        padding: 6px 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stExpander"] summary, .stExpander summary {
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: #6b7280 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    div[data-testid="stExpander"] summary:hover, .stExpander summary:hover {
        color: #1d4ed8 !important;
    }
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"], .stExpander [data-testid="stExpanderDetails"] {
        padding: 10px 0 5px 0 !important;
        background-color: transparent !important;
    }

    /* Column layout overrides to structure Right Sidebar */
    div[data-testid="column"]:first-child {
        padding-right: 1.5rem !important;
    }
    div[data-testid="column"]:last-child {
        background-color: #faf9f6 !important;
        border-left: 1px solid #e5e7eb !important;
        padding: 1.25rem 1rem !important;
        min-height: 100vh !important;
        margin-top: -1.5rem !important;
        margin-bottom: -2rem !important;
        margin-right: -2rem !important;
    }

    /* Logo & Branding */
    .brand-container {
        padding: 5px 0;
    }
    .indmoney-logo {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-text {
        font-size: 1.25rem;
        color: #1d4ed8;
        font-weight: 750;
        letter-spacing: -0.02em;
        font-family: 'Outfit', sans-serif;
    }
    .ai-badge {
        background-color: #e0e7ff;
        color: #1d4ed8;
        font-family: 'Outfit', sans-serif;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        letter-spacing: 0.02em;
        display: inline-block;
    }

    /* Compliance Warning Badge */
    .warning-badge {
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.4rem !important;
        background-color: #FFF7E6 !important;
        border: 1.5px solid #FFE8CC !important;
        color: #92400E !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 9999px !important;
        font-size: 0.725rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Refusal Cards */
    .refusal-error {
        background-color: #FEF2F2 !important;
        border: 1px solid #FCA5A5 !important;
        color: #991B1B !important;
        border-radius: 12px !important;
        padding: 0.85rem 1rem !important;
    }
    .refusal-block {
        background-color: #FFF7E6 !important;
        border: 1px solid #FFE8CC !important;
        color: #92400E !important;
        border-radius: 12px !important;
        padding: 0.85rem 1rem !important;
    }
    
    /* Suggestive Buttons */
    .suggestive-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 1rem !important;
        max-width: 640px !important;
        margin: 0 auto !important;
    }
    .suggestive-btn {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        cursor: pointer !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.2rem !important;
        min-height: 84px !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-sizing: border-box !important;
    }
    .suggestive-btn:hover {
        transform: translateY(-1.5px) !important;
        border-color: #CBD5E1 !important;
    }
    
    /* Selected Counter Pills */
    .selected-pill {
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
        background-color: #e0e7ff !important;
        color: #1d4ed8 !important;
        padding: 2px 8px !important;
        border-radius: 12px !important;
        font-size: 10px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        border: 1px solid #e5e7eb !important;
        transition: all 0.15s ease !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
    }
    .selected-pill:hover {
        background-color: #fef2f2 !important;
        color: #991b1b !important;
    }
    .pill-x {
        font-size: 10px !important;
        font-weight: bold !important;
        margin-left: 2px !important;
    }

    /* Citation Pills */
    .citation-pill {
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.3rem !important;
        background-color: #E0E7FF !important;
        color: #1D4ED8 !important;
        font-weight: 600 !important;
        font-size: 0.7rem !important;
        padding: 0.2rem 0.5rem !important;
        border-radius: 9999px !important;
        text-decoration: none !important;
    }
    .citation-pill:hover {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
    }
    .last-updated-date {
        font-size: 0.65rem !important;
        color: #6B7280 !important;
    }

    /* Right Sidebar: Conversation Threads & Info Cards */
    .btn-new-chat {
        width: 100%;
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
        padding: 0.65rem 1rem !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: background-color 0.15s ease !important;
        font-size: 0.85rem !important;
        margin-bottom: 20px !important;
    }
    .btn-new-chat:hover {
        background-color: #1e40af !important;
    }
    .sidebar-right-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.725rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        color: #6b7280 !important;
        letter-spacing: 0.05em !important;
    }
    .thread-item {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 0.6rem !important;
        padding: 0.55rem 0.75rem !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        color: #1f2937 !important;
        transition: all 0.15s ease !important;
        margin-bottom: 6px !important;
    }
    .thread-item:hover {
        background-color: rgba(29, 78, 216, 0.03) !important;
    }
    .thread-item.active {
        background-color: #e0e7ff !important;
        color: #1d4ed8 !important;
        font-weight: 600 !important;
    }
    .thread-link {
        color: inherit !important;
        text-decoration: none !important;
        flex: 1 !important;
        font-size: 0.8rem !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    .thread-actions {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        flex-shrink: 0 !important;
    }
    .thread-action-btn {
        color: #6b7280 !important;
        text-decoration: none !important;
        font-size: 0.8rem !important;
        opacity: 0.6 !important;
        transition: opacity 0.15s ease !important;
    }
    .thread-action-btn:hover {
        opacity: 1 !important;
    }
    .thread-action-btn.delete:hover {
        color: #ef4444 !important;
    }
    .how-it-works-card {
        background-color: #eef2f6 !important;
        border-radius: 12px !important;
        padding: 1.1rem !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.85rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.01) !important;
        margin-bottom: 25px !important;
    }
    .how-header {
        display: flex !important;
        align-items: center !important;
        gap: 0.45rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        letter-spacing: 0.03em !important;
    }
    .how-list {
        list-style: none !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.65rem !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .how-list li {
        display: flex !important;
        gap: 0.5rem !important;
        font-size: 0.75rem !important;
        line-height: 1.4 !important;
        color: #1f2937 !important;
    }
    .how-check-icon {
        color: #1d4ed8 !important;
        flex-shrink: 0 !important;
        font-weight: bold !important;
    }
    .how-footer {
        font-size: 0.65rem !important;
        color: #6b7280 !important;
        line-height: 1.45 !important;
        border-top: 1px solid rgba(0, 0, 0, 0.05) !important;
        padding-top: 0.65rem !important;
    }
    .recently-asked-box {
        display: flex !important;
        flex-direction: column !important;
        gap: 0.65rem !important;
    }
    .recently-asked-list {
        list-style: none !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.25rem !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .asked-item {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        padding: 0.45rem 0.5rem !important;
        font-size: 0.75rem !important;
        color: #1f2937 !important;
        cursor: pointer !important;
        border-radius: 6px !important;
        transition: all 0.1s ease !important;
        text-decoration: none !important;
    }
    .asked-item:hover {
        background-color: rgba(0, 0, 0, 0.02) !important;
        text-decoration: underline !important;
    }

    /* Modal Styling */
    .modal-overlay {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background-color: rgba(17, 24, 39, 0.4) !important;
        backdrop-filter: blur(3px) !important;
        z-index: 99999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 1rem !important;
    }
    .modal-container {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 16px !important;
        max-width: 600px !important;
        width: 100% !important;
        max-height: 85vh !important;
        overflow-y: auto !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
        display: flex !important;
        flex-direction: column !important;
        box-sizing: border-box !important;
    }
    .modal-header {
        padding: 1rem 1.25rem !important;
        border-bottom: 1px solid #e5e7eb !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
    .modal-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
    }
    .close-btn {
        background: none !important;
        border: none !important;
        cursor: pointer !important;
        color: #6b7280 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.25rem !important;
        border-radius: 6px !important;
        text-decoration: none !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
    .close-btn:hover {
        background-color: #f1f5f9 !important;
        color: #111827 !important;
    }
    .modal-body {
        padding: 1.25rem !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 1rem !important;
        box-sizing: border-box !important;
    }
    .workflow-steps {
        display: flex !important;
        flex-direction: column !important;
        gap: 0.75rem !important;
    }
    .workflow-step {
        display: flex !important;
        gap: 0.75rem !important;
        background-color: #faf9f6 !important;
        border: 1px solid #e5e7eb !important;
        padding: 0.75rem !important;
        border-radius: 8px !important;
    }
    .step-icon {
        width: 28px !important;
        height: 28px !important;
        border-radius: 6px !important;
        background-color: #e0e7ff !important;
        color: #1d4ed8 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
        font-weight: bold !important;
    }
    .step-info h4 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        margin: 0 0 0.15rem 0 !important;
    }
    .step-info p {
        font-size: 0.75rem !important;
        color: #6b7280 !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }
    .step-info code {
        background-color: #e2e8f0 !important;
        padding: 0.05rem 0.2rem !important;
        border-radius: 3px !important;
        font-size: 0.7rem !important;
        font-family: monospace !important;
    }
    .compliance-box-warning {
        background-color: #fff7e6 !important;
        border: 1px solid #ffe8cc !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        color: #92400e !important;
        font-size: 0.75rem !important;
    }
    .compliance-box-warning h5 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        margin: 0 0 0.25rem 0 !important;
        color: inherit !important;
    }
    .compliance-box-warning ul {
        padding-left: 1.1rem !important;
        margin: 0 !important;
    }
</style>
""")

# Left Sidebar: Logo and Header
render_html("""
<div class="brand-container" style="margin-bottom: 20px;">
  <div class="indmoney-logo" style="display: flex; align-items: center; gap: 8px;">
    <span class="brand-text">INDMoney</span>
    <span class="ai-badge">AI</span>
  </div>
</div>
<div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.8rem; color: #111827; letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px; margin-bottom: 15px;">
  📁 ICICI PRUDENTIAL MF
</div>
""", sidebar=True)

# Show selected funds count/summary on top of the sidebar
sidebar_label = f"Selected ({len(selected_schemes)})" if selected_schemes else "Selected (All 15)"
st.sidebar.html(f"""
<div style="margin-bottom: 15px; border-bottom: 1px solid #e5e7eb; padding-bottom: 12px;">
    <span style="font-family: 'Outfit', sans-serif; font-size:0.75rem; font-weight:700; color:#111827; text-transform:uppercase; display:block;">{sidebar_label}</span>
</div>
""")

# Default behavior notice
st.sidebar.html("""
<div style="font-size: 0.7rem; color: #6b7280; background-color: #f3f4f6; border-radius: 6px; padding: 6px 8px; margin-bottom: 15px; line-height: 1.3;">
  💡 <b>Default behavior:</b> All 15 funds are selected for context if none are checked.
</div>
""")

# Fund selection categories (collapsible expanders)
with st.sidebar.expander("EQUITY FUNDS", expanded=True):
    for scheme in EQUITY_FUNDS:
        st.checkbox(scheme, key=f"chk-{scheme}")

with st.sidebar.expander("HYBRID FUNDS", expanded=True):
    for scheme in HYBRID_FUNDS:
        st.checkbox(scheme, key=f"chk-{scheme}")

with st.sidebar.expander("INDEX, ETFS & TAX", expanded=True):
    for scheme in INDEX_ETFS_TAX:
        st.checkbox(scheme, key=f"chk-{scheme}")

# ----------------- MAIN LAYOUT IN 2 COLUMNS -----------------
# This creates a 3-column layout combined with the left sidebar
chat_col, right_col = st.columns([7.5, 2.5])

active_sess = st.session_state.active_session
messages = st.session_state.sessions.get(active_sess, []) if active_sess else []

# Function to submit message from standard chat input box
def submit_chat_message(query_text):
    if not query_text.strip():
        return
    
    # Add user message
    st.session_state.sessions[active_sess].append({"sender": "user", "text": query_text})
    
    # Run RAG
    pass_filter = selected_fund_ids if selected_fund_ids else None
    response_data = pipeline.generate_response(query_text, selected_funds=pass_filter)
    
    # Add assistant response
    st.session_state.sessions[active_sess].append({
        "sender": "assistant",
        "text": response_data.get("answer", ""),
        "status": response_data.get("status", "success"),
        "type": response_data.get("type", "factual"),
        "citation": response_data.get("citation"),
        "last_updated": response_data.get("last_updated")
    })
    st.rerun()

# ----------------- CENTER COLUMN: Chat Area -----------------
with chat_col:
    # Compliance warning badge at the top-right
    render_html("""
    <div style="display: flex; justify-content: flex-end; width: 100%; max-width: 640px; margin: 0 auto 20px auto;">
        <div class="warning-badge">⚠️ Facts-Only. No Investment Advice.</div>
    </div>
    """)
    
    # Thread Inline Rename form (if triggered)
    if st.session_state.renaming_session:
        ren_id = st.session_state.renaming_session
        curr_name = st.session_state.session_names.get(ren_id, "Chat")
        st.markdown(f"**Rename conversation:**")
        new_name = st.text_input("New Name", value=curr_name, key="rename-txt-in")
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            if st.button("Save", key="btn-save-rn"):
                if new_name.strip():
                    st.session_state.session_names[ren_id] = new_name.strip()
                st.session_state.renaming_session = None
                st.rerun()
        with r_col2:
            if st.button("Cancel", key="btn-cancel-rn"):
                st.session_state.renaming_session = None
                st.rerun()

    # Welcome screen
    if not messages:
        render_html("""
        <div style="text-align: center; margin: 40px auto 40px auto; max-width: 640px;">
            <h1 style="font-size: 2.1rem; font-weight: 700; color: #111827; margin-bottom: 8px;">How can I help you today?</h1>
            <p style="font-size: 0.875rem; color: #6b7280; max-width: 500px; margin: 0 auto; line-height: 1.5;">
                Ask me anything about ICICI Prudential funds, expense ratios, tax implications, or performance data.
            </p>
        </div>
        """)
        
        # Suggestive Prompt Cards Grid
        # Get active selection questions
        dynamic_suggestions = []
        if len(selected_schemes) == 0 or len(selected_schemes) == len(FUND_ID_MAP):
            dynamic_suggestions = DEFAULT_QUESTIONS.copy()
        else:
            for name in selected_schemes:
                if name in QUESTIONS_BY_FUND:
                    for q in QUESTIONS_BY_FUND[name]:
                        if q not in dynamic_suggestions:
                            dynamic_suggestions.append(q)
            # Backfill to ensure exactly 6 questions
            if len(dynamic_suggestions) < 6:
                for q in DEFAULT_QUESTIONS:
                    if q not in dynamic_suggestions and len(dynamic_suggestions) < 6:
                        dynamic_suggestions.append(q)
                    
        suggestions_to_show = dynamic_suggestions[:6]
        
        # Render cards as a CSS Grid of styled HTML anchors linking to ?ask=
        suggestions_html = '<div class="suggestive-grid">'
        for idx, card in enumerate(suggestions_to_show):
            card_url = f"?ask={card['query'].replace(' ', '+').replace('&', '%26')}"
            suggestions_html += f"""
            <a href="{card_url}" target="_self" style="text-decoration: none;">
                <div class="suggestive-btn">
                    <span style="font-size: 0.85rem; font-weight: 600; color: #111827; line-height: 1.35;">{card['label']}</span>
                    <span style="font-size: 0.65rem; color: #6b7280; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-top: auto;">FUND PARAMETERS</span>
                </div>
            </a>
            """
        suggestions_html += '</div>'
        render_html(suggestions_html)
    else:
        # Message bubble display (HTML high-fidelity alignment)
        for msg in messages:
            if msg["sender"] == "user":
                render_html(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 16px; width: 100%; max-width: 640px; margin-left: auto; margin-right: auto;">
                    <div style="background-color: #1d4ed8; color: #ffffff; padding: 12px 16px; border-radius: 12px; border-bottom-right-radius: 2px; max-width: 80%; font-size: 0.85rem; line-height: 1.45; box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-family: sans-serif;">
                        {msg['text']}
                    </div>
                </div>
                """)
            else:
                # Assistant message bubble
                if msg.get("status") == "refused":
                    # Colored refusal cards
                    bg_class = "refusal-error" if msg.get("type") == "pii" else "refusal-block"
                    title = "🛡️ PII Security Block" if msg.get("type") == "pii" else "⚠️ Regulatory Notice"
                    link_html = ""
                    if msg.get("type") == "advisory":
                        link_html = "<br><a href='https://www.amfiindia.com/investor-corner/education/interest-rates.html' target='_blank' style='color:#92400e; font-weight:600; text-decoration:underline; font-size:0.75rem;'>Visit AMFI Investor Education ↗</a>"
                    elif msg.get("type") == "comparison":
                        link_html = "<br><a href='https://www.sebi.gov.in' target='_blank' style='color:#92400e; font-weight:600; text-decoration:underline; font-size:0.75rem;'>Visit SEBI Portal ↗</a>"
                        
                    render_html(f"""
                    <div class="{bg_class}" style="max-width: 640px; font-family: sans-serif; font-size: 0.85rem; margin: 0 auto 16px auto; box-sizing: border-box;">
                        <h4 style="margin: 0 0 6px 0; font-weight: 700; font-size: 0.9rem; color: inherit;">{title}</h4>
                        <p style="margin: 0; line-height: 1.4; color: inherit;">{msg['text']}</p>
                        {link_html}
                    </div>
                    """)
                else:
                    # Clean fact response card
                    citation = msg.get("citation")
                    last_updated = msg.get("last_updated")
                    
                    citation_html = ""
                    if citation or last_updated:
                        label = citation.get("label", "Factsheet Source") if citation else "Factsheet Source"
                        url = citation.get("url", "https://www.indmoney.com") if citation else "https://www.indmoney.com"
                        
                        friendly_date = "Not available"
                        if last_updated and last_updated != "Not available":
                            try:
                                dt = datetime.fromisoformat(last_updated)
                                friendly_date = dt.strftime("%d %b %Y")
                            except Exception:
                                friendly_date = last_updated[:10]
                                
                        citation_html = f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #e5e7eb; margin-top: 10px; padding-top: 8px; flex-wrap: wrap; gap: 8px;">
                            <a href="{url}" target="_blank" class="citation-pill">📁 {label}</a>
                            <span class="last-updated-date">Updated: {friendly_date}</span>
                        </div>
                        """
                        
                    render_html(f"""
                    <div style="display: flex; justify-content: flex-start; margin-bottom: 16px; width: 100%; max-width: 640px; margin-left: auto; margin-right: auto;">
                        <div style="background-color: #ffffff; color: #1f2937; padding: 12px 16px; border-radius: 12px; border-bottom-left-radius: 2px; border: 1px solid #e5e7eb; max-width: 80%; font-size: 0.85rem; line-height: 1.45; box-shadow: 0 1px 3px rgba(0,0,0,0.02); font-family: sans-serif; box-sizing: border-box;">
                            <p style="margin: 0;">{msg['text']}</p>
                            {citation_html}
                        </div>
                    </div>
                    """)

    # Active Selected Funds count and pills display (placed stacked above input field)
    active_count = len(selected_schemes)
    if active_count == 0:
        render_html(f"""
        <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; max-width: 640px; margin-left: auto; margin-right: auto; padding: 4px 0;">
            <span style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.8rem; color: #6b7280; margin-right: 4px;">Selected: [ All 15 Funds ] (Default)</span>
        </div>
        """)
    else:
        # Generate pills with uncheck links matching React UI hover/style behaviour
        pill_html = "".join([
            f'<a href="?uncheck={name.replace(" ", "+")}" target="_self" style="text-decoration: none;" title="Click to remove {name}">'
            f'<span class="selected-pill">{name} <span class="pill-x">×</span></span>'
            f'</a>'
            for name in selected_schemes
        ])
        render_html(f"""
        <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; max-width: 640px; margin-left: auto; margin-right: auto;">
            <span style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.8rem; color: #6b7280; margin-right: 4px;">Selected: [ {active_count} ]</span>
            {pill_html}
        </div>
        """)

    # Chat Input field
    input_text = st.chat_input("Type your financial question here...")
    if input_text:
        if not active_sess:
            # Setup session if empty
            active_sess = f"session-{int(datetime.now().timestamp() * 1000)}"
            st.session_state.sessions[active_sess] = []
            st.session_state.session_names[active_sess] = "Chat 1"
            st.session_state.active_session = active_sess
        submit_chat_message(input_text)

    # Footer links rows
    render_html("""
    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; color: #6b7280; margin-top: 15px; border-top: 1px solid rgba(0,0,0,0.03); padding-top: 10px; font-family: sans-serif; max-width: 640px; margin-left: auto; margin-right: auto;">
        <span>🕒 Last updated from official AMC sources.</span>
        <div>
            <a href="?modal=arch" target="_self" style="color: inherit; text-decoration: underline;">System Architecture</a>
            <span style="margin: 0 4px;">•</span>
            <a href="?modal=privacy" target="_self" style="color: inherit; text-decoration: underline;">Privacy Policy</a>
        </div>
    </div>
    """)

# ----------------- RIGHT COLUMN: Threads and info widgets -----------------
with right_col:
    # New Chat Button (Styled royal blue card link)
    render_html("""
    <a href="?new_chat=true" target="_self" style="text-decoration: none;">
        <div class="btn-new-chat">
            <span>+</span> <span>New Chat</span>
        </div>
    </a>
    """)
    
    # Recent Conversations Section
    st.html("<span class='sidebar-right-title' style='display:block; margin-bottom:10px;'>Recent Conversations</span>")
    
    # Render Threads using high fidelity list formatting
    threads_html = "<div style='display: flex; flex-direction: column; gap: 6px; margin-bottom: 25px;'>"
    for idx, s_id in enumerate(list(st.session_state.sessions.keys())):
        s_name = st.session_state.session_names.get(s_id, s_id)
        is_active = (active_sess == s_id)
        
        bg_active_class = "active" if is_active else ""
        
        threads_html += f"""
        <div class="thread-item {bg_active_class}">
            <a href="?session={s_id}" target="_self" class="thread-link">
                💬 {s_name}
            </a>
            <div class="thread-actions">
                <a href="?trigger_rename={s_id}" target="_self" class="thread-action-btn" title="Rename conversation">✏️</a>
                <a href="?delete={s_id}" target="_self" class="thread-action-btn delete" title="Delete conversation">🗑️</a>
            </div>
        </div>
        """
    threads_html += "</div>"
    render_html(threads_html)
    
    # HOW IT WORKS? Card
    render_html("""
    <div class="how-it-works-card">
        <div class="how-header">
            <span class="how-info-icon">ℹ️</span> <span>HOW IT WORKS?</span>
        </div>
        <ul class="how-list">
            <li>
                <span class="how-check-icon">✓</span>
                <span>Factual answers only (NAV, AUM, returns, holdings, etc.)</span>
            </li>
            <li>
                <span class="how-check-icon">✓</span>
                <span>No advice or comparisons; short replies with sources</span>
            </li>
            <li>
                <span class="how-check-icon">✓</span>
                <span>Rejects PII and opinion questions</span>
            </li>
        </ul>
        <div class="how-footer">
            AI-generated responses. Verify with cited sources. Free-tier API: wait a few minutes if limits are hit.
        </div>
    </div>
    """)
    
    # RECENTLY ASKED list
    st.html("<span class='sidebar-right-title' style='display:block; margin-bottom:10px;'>Recently Asked</span>")
    
    render_html("""
    <div class="recently-asked-box">
        <ul class="recently-asked-list">
            <li>
                <a href="?ask=What+is+the+minimum+investment+amount+for+ICICI+Prudential+Large+%26+Mid+Cap+Fund%3F" target="_self" class="asked-item" title="What is the minimum investment amount for ICICI Prudential Large & Mid Cap Fund?">
                    🔍 <span>Min investment: Large & Mid Cap</span>
                </a>
            </li>
            <li>
                <a href="?ask=What+is+the+AUM+of+ICICI+Prudential+Equity+%26+Debt+Fund%3F" target="_self" class="asked-item" title="What is the AUM of ICICI Prudential Equity & Debt Fund?">
                    🔍 <span>AUM of Equity & Debt</span>
                </a>
            </li>
            <li>
                <a href="?ask=What+is+the+lock-in+period+for+ICICI+Prudential+ELSS+Tax+Saver+Fund%3F" target="_self" class="asked-item" title="What is the lock-in period for ICICI Prudential ELSS Tax Saver Fund?">
                    🔍 <span>Lock-in period: ELSS</span>
                </a>
            </li>
            <li>
                <a href="?ask=What+is+the+benchmark+index+of+ICICI+Prudential+Nifty+50+Index+Fund%3F" target="_self" class="asked-item" title="What is the benchmark index of ICICI Prudential Nifty 50 Index Fund?">
                    🔍 <span>Benchmark of Nifty 50 Index</span>
                </a>
            </li>
            <li>
                <a href="?ask=What+is+the+tracking+error+of+ICICI+Prudential+Nifty+50+Index+Fund%3F" target="_self" class="asked-item" title="What is the tracking error of ICICI Prudential Nifty 50 Index Fund?">
                    🔍 <span>Tracking error: Nifty 50 Index</span>
                </a>
            </li>
        </ul>
    </div>
    """)

    # Adding CSS support for hover decoration on link text
    st.html("""
    <style>
        a:hover span {
            text-decoration: underline !important;
            color: #1d4ed8 !important;
        }
    </style>
    """)

# ----------------- SYSTEM OVERLAYS (MODALS) -----------------
modal_param = st.query_params.get("modal")
if modal_param == "arch":
    render_html("""
    <div class="modal-overlay">
        <div class="modal-container">
            <div class="modal-header">
                <h2 class="modal-title">System Architecture (Facts-Only RAG)</h2>
                <a href="?" target="_self" class="close-btn">&times;</a>
            </div>
            <div class="modal-body">
                <div class="workflow-steps">
                    <div class="workflow-step">
                        <div class="step-icon">☁️</div>
                        <div class="step-info">
                            <h4>1. Scraper & Parser</h4>
                            <p>Fetches client props from 15 INDMoney URLs using <code>curl-cffi</code> Chrome impersonation. Extracts 13 key parameters directly from <code>__NEXT_DATA__</code>.</p>
                        </div>
                    </div>
                    <div class="workflow-step">
                        <div class="step-icon">🔢</div>
                        <div class="step-info">
                            <h4>2. Chunking & Embeddings</h4>
                            <p>Chunks metadata with context-aware prefixes (Scheme + Plan). Generates 1024-dimension embeddings via local <code>BAAI/bge-large-en-v1.5</code>.</p>
                        </div>
                    </div>
                    <div class="workflow-step">
                        <div class="step-icon">🗄️</div>
                        <div class="step-info">
                            <h4>3. Vector DB Retrieval</h4>
                            <p>Stores vectors in ChromaDB. Uses cosine similarity with strict L2 distance threshold filters to omit irrelevant sources.</p>
                        </div>
                    </div>
                    <div class="workflow-step">
                        <div class="step-icon">🛡️</div>
                        <div class="step-info">
                            <h4>4. Query Classification</h4>
                            <p>Pre-evaluates input for PII leaks (PAN, Aadhaar), advisory intent, performance comparisons, and greetings using strict regex and classifiers.</p>
                        </div>
                    </div>
                    <div class="workflow-step">
                        <div class="step-icon">⚙️</div>
                        <div class="step-info">
                            <h4>5. Generation (Groq LLaMA 3.3)</h4>
                            <p>Forwards retrieved facts to <code>llama-3.3-70b-versatile</code>. Enforces a strict response limit of ≤3 sentences, no investment advice, and 1 source citation.</p>
                        </div>
                    </div>
                    <div class="workflow-step">
                        <div class="step-icon">✅</div>
                        <div class="step-info">
                            <h4>6. Output Validation</h4>
                            <p>Validates sentence limit, citation inclusion, and scraper timestamp. Truncates and auto-corrects before serving response.</p>
                        </div>
                    </div>
                </div>
                <div class="compliance-box-warning">
                    <h5>Compliance Rules Guardrail</h5>
                    <ul>
                        <li>No comparisons: Triggers polite refusals.</li>
                        <li>No advisory: Prompts redirect to AMFI educational portal.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """)
elif modal_param == "privacy":
    render_html("""
    <div class="modal-overlay">
        <div class="modal-container">
            <div class="modal-header">
                <h2 class="modal-title">Privacy Policy & Security Guardrails</h2>
                <a href="?" target="_self" class="close-btn">&times;</a>
            </div>
            <div class="modal-body">
                <div class="compliance-box-warning" style="background-color: #ECFDF3; border-color: #A7F3D0; color: #047857;">
                    <h5 style="font-family: 'Outfit', sans-serif; font-weight: 700;">Strict Regulatory Compliance & Safety Shield</h5>
                    <p style="font-size: 0.8rem; line-height: 1.45; margin-top: 0.25rem; color: inherit;">
                        In strict alignment with SEBI, AMFI, and INDMoney security guidelines, this Facts-Only FAQ Assistant enforces the following data protection protocols:
                    </p>
                </div>
                <div class="workflow-steps" style="margin-top: 0.5rem;">
                    <div class="workflow-step" style="background-color: #FFFFFF;">
                        <div class="step-icon" style="background-color: #FEE2E2; color: #991B1B;">🛡️</div>
                        <div class="step-info">
                            <h4 style="color: #991B1B;">Zero PII Retention</h4>
                            <p>Our pipeline incorporates query classifier filters that identify and block Personal Identifiable Information (PAN cards, Aadhaar cards, phone numbers, email addresses, and OTP codes) prior to processing.</p>
                        </div>
                    </div>
                    <div class="workflow-step" style="background-color: #FFFFFF;">
                        <div class="step-icon" style="background-color: #E0F2FE; color: #0369A1;">🗄️</div>
                        <div class="step-info">
                            <h4 style="color: #0369A1;">No Data Caching or Logs</h4>
                            <p>All query interactions are processed in volatile memory. No user inputs, vector queries, or financial profile attributes are ever cached, saved, or logged to disk.</p>
                        </div>
                    </div>
                    <div class="workflow-step" style="background-color: #FFFFFF;">
                        <div class="step-icon" style="background-color: #FEF3C7; color: #D97706;">ℹ️</div>
                        <div class="step-info">
                            <h4 style="color: #D97706;">Official Facts Isolation</h4>
                            <p>Retrieval focuses exclusively on verified factsheets directly matched from official public AMC URLs. The system does not possess any links to client portfolios or transaction gateways.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """)
