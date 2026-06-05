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

# Custom CSS styling for Cafe Light Theme and structure overrides
st.markdown("""
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
if "renaming_session" not in st.session_state:
    st.session_state.renaming_session = None

# Left Sidebar: Checkboxes and Logo
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px;">
  <span style="font-size: 1.5rem; color: #1d4ed8; font-weight: 750; font-family: 'Outfit', sans-serif; letter-spacing: -0.02em;">
    INDMoney
  </span>
  <span style="background-color: #e0e7ff; color: #1d4ed8; font-size: 0.9rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-family: 'Outfit', sans-serif; display: inline-block;">
    AI
  </span>
</div>
<div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.8rem; color: #111827; letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px; margin-bottom: 15px;">
  📁 ICICI PRUDENTIAL MF
</div>
""", unsafe_allow_html=True)

# Collect Checked Schemes
selected_schemes = []

st.sidebar.markdown("<span style='font-size:0.75rem; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:8px;'>Equity Funds</span>", unsafe_allow_html=True)
for scheme in EQUITY_FUNDS:
    # Default Small Cap checked as per app behavior
    default_val = (scheme == 'Small Cap Fund')
    if st.sidebar.checkbox(scheme, value=default_val, key=f"chk-{scheme}"):
        selected_schemes.append(scheme)

st.sidebar.markdown("<br><span style='font-size:0.75rem; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:8px;'>Hybrid Funds</span>", unsafe_allow_html=True)
for scheme in HYBRID_FUNDS:
    if st.sidebar.checkbox(scheme, value=False, key=f"chk-{scheme}"):
        selected_schemes.append(scheme)

st.sidebar.markdown("<br><span style='font-size:0.75rem; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:8px;'>Index, ETFs & Tax</span>", unsafe_allow_html=True)
for scheme in INDEX_ETFS_TAX:
    if st.sidebar.checkbox(scheme, value=False, key=f"chk-{scheme}"):
        selected_schemes.append(scheme)

# Map checked schemes to fund IDs
selected_fund_ids = [FUND_ID_MAP[name] for name in selected_schemes if name in FUND_ID_MAP]

# ----------------- STATE MACHINE USING QUERY PARAMS -----------------
params = st.query_params

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
        # Create fallback session if none active
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
    st.markdown("""
    <div style="display: flex; justify-content: flex-end; width: 100%; margin-bottom: 20px;">
        <div class="warning-badge">⚠️ Facts-Only. No Investment Advice.</div>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; margin-bottom: 40px;">
            <h1 style="font-size: 2.1rem; font-weight: 700; color: #111827; margin-bottom: 8px;">How can I help you today?</h1>
            <p style="font-size: 0.875rem; color: #6b7280; max-width: 500px; margin: 0 auto; line-height: 1.5;">
                Ask me anything about ICICI Prudential funds, expense ratios, tax implications, or performance data.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Suggestive Prompt Cards Grid
        # Get active selection questions
        dynamic_suggestions = []
        if len(selected_schemes) == 0 or len(selected_schemes) == len(FUND_ID_MAP):
            dynamic_suggestions = DEFAULT_QUESTIONS
        else:
            for name in selected_schemes:
                if name in QUESTIONS_BY_FUND:
                    dynamic_suggestions.extend(QUESTIONS_BY_FUND[name])
                    
        suggestions_to_show = dynamic_suggestions[:4]
        
        # Render cards as columns of styled HTML anchors linking to ?ask=
        card_cols = st.columns(2)
        for idx, card in enumerate(suggestions_to_show):
            with card_cols[idx % 2]:
                card_url = f"?ask={card['query'].replace(' ', '+').replace('&', '%26')}"
                st.markdown(f"""
                <a href="{card_url}" target="_self" style="text-decoration: none;">
                    <div class="suggestive-btn">
                        <span style="font-size: 0.85rem; font-weight: 600; color: #111827;">{card['label']}</span>
                        <span style="font-size: 0.65rem; color: #6b7280; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-top: auto;">FUND PARAMETERS</span>
                    </div>
                </a>
                """, unsafe_allow_html=True)
    else:
        # Message bubble display (HTML high-fidelity alignment)
        for msg in messages:
            if msg["sender"] == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 16px; width: 100%;">
                    <div style="background-color: #1d4ed8; color: #ffffff; padding: 12px 16px; border-radius: 12px; border-bottom-right-radius: 2px; max-width: 80%; font-size: 0.85rem; line-height: 1.45; box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-family: sans-serif;">
                        {msg['text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
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
                        
                    st.markdown(f"""
                    <div class="{bg_class}" style="max-width: 80%; font-family: sans-serif; font-size: 0.85rem; margin-bottom: 16px;">
                        <h4 style="margin: 0 0 6px 0; font-weight: 700; font-size: 0.9rem; color: inherit;">{title}</h4>
                        <p style="margin: 0; line-height: 1.4; color: inherit;">{msg['text']}</p>
                        {link_html}
                    </div>
                    """, unsafe_allow_html=True)
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
                        
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-start; margin-bottom: 16px; width: 100%;">
                        <div style="background-color: #ffffff; color: #1f2937; padding: 12px 16px; border-radius: 12px; border-bottom-left-radius: 2px; border: 1px solid #e5e7eb; max-width: 80%; font-size: 0.85rem; line-height: 1.45; box-shadow: 0 1px 3px rgba(0,0,0,0.02); font-family: sans-serif;">
                            <p style="margin: 0;">{msg['text']}</p>
                            {citation_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # Active Selected Funds count and pills display (placed stacked above input field)
    active_count = len(selected_schemes)
    st.markdown("<br>", unsafe_allow_html=True)
    
    pill_html = ""
    for name in selected_schemes:
        pill_html += f"""
        <span style="display: inline-flex; align-items: center; gap: 4px; background-color: #e0e7ff; color: #1d4ed8; padding: 3px 8px; border-radius: 12px; font-size: 10px; font-weight: 500; border: 1px solid #e5e7eb; margin-right: 6px; margin-bottom: 6px;">
            {name}
        </span>
        """
        
    st.markdown(f"""
    <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
        <span style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.8rem; color: #6b7280; margin-right: 4px;">Selected: [ {active_count} ]</span>
        {pill_html}
    </div>
    """, unsafe_allow_html=True)

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
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; color: #6b7280; margin-top: 15px; border-top: 1px solid rgba(0,0,0,0.03); padding-top: 10px; font-family: sans-serif;">
        <span>🕒 Last updated from official AMC sources.</span>
        <div>
            <span style="cursor: pointer; text-decoration: underline;">System Architecture</span>
            <span style="margin: 0 4px;">•</span>
            <span style="cursor: pointer; text-decoration: underline;">Privacy Policy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- RIGHT COLUMN: Threads and info widgets -----------------
with right_col:
    # New Chat Button (Styled royal blue card link)
    st.markdown("""
    <a href="?new_chat=true" target="_self" style="text-decoration: none;">
        <div style="background-color: #1d4ed8; color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.85rem; text-align: center; border-radius: 8px; padding: 10px 16px; margin-bottom: 20px; transition: background-color 0.2s;">
            + New Chat
        </div>
    </a>
    """, unsafe_allow_html=True)
    
    # Recent Conversations Section
    st.markdown("<span style='font-size:0.75rem; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:10px;'>Recent Conversations</span>", unsafe_allow_html=True)
    
    # Render Threads using high fidelity list formatting
    threads_html = "<div style='display: flex; flex-direction: column; gap: 6px; margin-bottom: 25px; font-family: sans-serif;'>"
    for idx, s_id in enumerate(list(st.session_state.sessions.keys())):
        s_name = st.session_state.session_names.get(s_id, s_id)
        is_active = (active_sess == s_id)
        
        bg_style = "background-color: #e0e7ff; color: #1d4ed8; font-weight: 600;" if is_active else "background-color: transparent; color: #1f2937;"
        
        threads_html += f"""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; border-radius: 8px; {bg_style} transition: background-color 0.15s;">
            <a href="?session={s_id}" target="_self" style="color: inherit; text-decoration: none; flex: 1; font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                💬 {s_name}
            </a>
            <div style="display: flex; align-items: center; gap: 8px;">
                <a href="?trigger_rename={s_id}" target="_self" style="color: inherit; text-decoration: none; font-size: 0.75rem;" title="Rename">✏️</a>
                <a href="?delete={s_id}" target="_self" style="color: #ef4444; text-decoration: none; font-size: 0.85rem;" title="Delete">🗑️</a>
            </div>
        </div>
        """
    threads_html += "</div>"
    st.markdown(threads_html, unsafe_allow_html=True)
    
    # HOW IT WORKS? Card
    st.markdown("""
    <div style="background-color: #eef2f6; border-radius: 12px; padding: 16px; margin-bottom: 25px; font-family: sans-serif;">
        <div style="font-family: 'Outfit', sans-serif; color: #111827; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.03em; display: flex; align-items: center; gap: 6px; margin-bottom: 10px;">
            ℹ️ HOW IT WORKS?
        </div>
        <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px;">
            <li style="display: flex; gap: 6px; font-size: 0.725rem; color: #1f2937; line-height: 1.4;">
                <span style="color: #1d4ed8;">✓</span> Factual answers only (NAV, AUM, returns, holdings, etc.)
            </li>
            <li style="display: flex; gap: 6px; font-size: 0.725rem; color: #1f2937; line-height: 1.4;">
                <span style="color: #1d4ed8;">✓</span> No advice or comparisons; short replies with sources
            </li>
            <li style="display: flex; gap: 6px; font-size: 0.725rem; color: #1f2937; line-height: 1.4;">
                <span style="color: #1d4ed8;">✓</span> Rejects PII and opinion questions
            </li>
        </ul>
        <div style="color: #6b7280; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 10px; margin-top: 10px; font-size: 0.625rem; line-height: 1.45;">
            AI-generated responses. Verify with cited sources. Free-tier API: wait a few minutes if limits are hit.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # RECENTLY ASKED list
    st.markdown("<span style='font-size:0.75rem; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:10px;'>Recently Asked</span>", unsafe_allow_html=True)
    
    recently_asked_queries = [
        {"q": "What are the top holdings of ICICI Prudential Bluechip Fund?", "label": "Top holdings of Bluechip Fund?"},
        {"q": "What is the difference in expense ratios between ICICI Prudential mutual funds?", "label": "Expense ratio comparison"},
        {"q": "What is the NAV of ICICI Prudential Small Cap Fund?", "label": "NAV of Small Cap Fund"}
    ]
    
    for idx, item in enumerate(recently_asked_queries):
        ask_url = f"?ask={item['q'].replace(' ', '+').replace('&', '%26')}"
        st.markdown(f"""
        <div style="margin-bottom: 8px; font-family: sans-serif;">
            <a href="{ask_url}" target="_self" style="display: flex; align-items: center; gap: 6px; text-decoration: none; color: #1f2937; font-size: 0.75rem; padding: 4px 0;">
                🔍 <span style="cursor: pointer; transition: color 0.15s;">{item['label']}</span>
            </a>
        </div>
        """, unsafe_allow_html=True)
        # Adding CSS support for hover decoration on link text
        st.markdown("""
        <style>
            a:hover span {
                text-decoration: underline !important;
                color: #1d4ed8 !important;
            }
        </style>
        """, unsafe_allow_html=True)
