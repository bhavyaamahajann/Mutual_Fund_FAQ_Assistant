import React, { useState, useEffect, useRef } from 'react';
import { 
  Folder, 
  Sun, 
  Moon, 
  AlertTriangle, 
  Send, 
  Clock, 
  Plus, 
  MessageSquare, 
  Info, 
  CheckCircle, 
  Search, 
  X, 
  DownloadCloud, 
  Binary, 
  Database, 
  Cpu, 
  CheckSquare,
  BarChart2,
  TrendingUp,
  Wallet,
  Shield,
  ExternalLink,
  Menu,
  ShieldAlert,
  Trash2,
  Edit2,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api/chat'
  : '/api/chat';

// Mapping of checkbox keys to backend fund ID identifiers
const fundIdMap = {
  'Small Cap Fund': 'icici-pru-smallcap-direct-growth',
  'Large & Mid Cap Fund': 'icici-pru-large-midcap-direct-growth',
  'Flexi Cap Fund': 'icici-pru-flexicap-direct-growth',
  'Focused Equity Fund': 'icici-pru-focused-equity-direct-growth',
  'Mid Cap Fund': 'icici-pru-midcap-direct-growth',
  'Multi Cap Fund': 'icici-pru-multicap-direct-growth',
  'Large Cap Fund': 'icici-pru-largecap-direct-growth',
  'Equity Savings Fund': 'icici-pru-equity-savings-direct-growth',
  'Equity & Debt Fund': 'icici-pru-equity-debt-direct-growth',
  'Regular Savings Fund': 'icici-pru-regular-savings-direct-growth',
  'Multi Asset Fund': 'icici-pru-multi-asset-direct-growth',
  'ELSS Tax Saver Fund': 'icici-pru-elss-direct-growth',
  'Nifty 50 Index Fund': 'icici-pru-nifty50-index-direct-growth',
  'Gold ETF FoF': 'icici-pru-gold-etf-fof-direct-growth',
  'Silver ETF FoF': 'icici-pru-silver-etf-fof-direct-growth'
};

// Suggestive questions categorized by fund checkbox name
const QUESTIONS_BY_FUND = {
  'Small Cap Fund': [
    {
      query: 'What is the expense ratio of ICICI Prudential Small Cap Fund?',
      icon: BarChart2,
      text: 'Expense ratio of Small Cap?',
      subtext: 'FUND PARAMETERS'
    },
    {
      query: 'Who manages the ICICI Prudential Small Cap Fund?',
      icon: Cpu,
      text: 'Fund Manager: Small Cap',
      subtext: 'MANAGEMENT'
    }
  ],
  'Large & Mid Cap Fund': [
    {
      query: 'What is the minimum investment amount for ICICI Prudential Large & Mid Cap Fund?',
      icon: Wallet,
      text: 'Min investment Large & Mid Cap',
      subtext: 'FUND PARAMETERS'
    }
  ],
  'Flexi Cap Fund': [
    {
      query: 'What is the 3-year CAGR for ICICI Prudential Flexi Cap Fund?',
      icon: TrendingUp,
      text: '3-year CAGR for Flexi Cap',
      subtext: 'PERFORMANCE'
    }
  ],
  'Focused Equity Fund': [
    {
      query: 'What is the exit load for ICICI Prudential Focused Equity Fund?',
      icon: Shield,
      text: 'Exit load for Focused Equity',
      subtext: 'REDEMPTION'
    }
  ],
  'Mid Cap Fund': [
    {
      query: 'Who are the fund managers of ICICI Prudential Mid Cap Fund?',
      icon: Cpu,
      text: 'Fund Managers: Mid Cap',
      subtext: 'MANAGEMENT'
    }
  ],
  'Multi Cap Fund': [
    {
      query: 'What is the expense ratio of ICICI Prudential Multi Cap Fund?',
      icon: BarChart2,
      text: 'Expense ratio: Multi Cap',
      subtext: 'FUND PARAMETERS'
    }
  ],
  'Large Cap Fund': [
    {
      query: 'What is the AUM of ICICI Prudential Large Cap Fund?',
      icon: BarChart2,
      text: 'AUM of Large Cap Fund',
      subtext: 'AUM SIZE'
    }
  ],
  'Equity Savings Fund': [
    {
      query: 'What is the exit load of ICICI Prudential Equity Savings Fund?',
      icon: Shield,
      text: 'Exit load: Equity Savings',
      subtext: 'REDEMPTION'
    }
  ],
  'Equity & Debt Fund': [
    {
      query: 'What is the AUM of ICICI Prudential Equity & Debt Fund?',
      icon: BarChart2,
      text: 'AUM of Equity & Debt',
      subtext: 'AUM SIZE'
    }
  ],
  'Regular Savings Fund': [
    {
      query: 'Who manages the ICICI Prudential Regular Savings Fund?',
      icon: Cpu,
      text: 'Fund Manager: Regular Savings',
      subtext: 'MANAGEMENT'
    }
  ],
  'Multi Asset Fund': [
    {
      query: 'What is the risk profile of ICICI Prudential Multi Asset Fund?',
      icon: Shield,
      text: 'Risk profile: Multi Asset',
      subtext: 'RISK ANALYSIS'
    }
  ],
  'ELSS Tax Saver Fund': [
    {
      query: 'What are the tax implications for ICICI Prudential ELSS Tax Saver Fund?',
      icon: Wallet,
      text: 'Tax implications for ELSS?',
      subtext: 'TAXATION'
    },
    {
      query: 'What is the lock-in period for ICICI Prudential ELSS Tax Saver Fund?',
      icon: Wallet,
      text: 'Lock-in period: ELSS',
      subtext: 'TAXATION'
    }
  ],
  'Nifty 50 Index Fund': [
    {
      query: 'What is the tracking error of ICICI Prudential Nifty 50 Index Fund?',
      icon: TrendingUp,
      text: 'Tracking error: Nifty 50 Index',
      subtext: 'PERFORMANCE'
    }
  ],
  'Gold ETF FoF': [
    {
      query: 'What is the exit load of ICICI Prudential Gold ETF Fund of Fund?',
      icon: Shield,
      text: 'Exit load: Gold ETF FoF',
      subtext: 'REDEMPTION'
    }
  ],
  'Silver ETF FoF': [
    {
      query: 'What is the minimum investment for ICICI Prudential Silver ETF Fund of Fund?',
      icon: Wallet,
      text: 'Min investment: Silver ETF FoF',
      subtext: 'FUND PARAMETERS'
    }
  ]
};


function App() {
  // Checkbox State (All 15 schemes from context.md)
  const [checkboxes, setCheckboxes] = useState({
    'Small Cap Fund': true,
    'Large & Mid Cap Fund': false,
    'Flexi Cap Fund': false,
    'Focused Equity Fund': false,
    'Mid Cap Fund': false,
    'Multi Cap Fund': false,
    'Large Cap Fund': false,
    'Equity Savings Fund': false,
    'Equity & Debt Fund': false,
    'Regular Savings Fund': false,
    'Multi Asset Fund': false,
    'ELSS Tax Saver Fund': false,
    'Nifty 50 Index Fund': false,
    'Gold ETF FoF': false,
    'Silver ETF FoF': false,
  });

  const [expandedCategories, setExpandedCategories] = useState({
    equity: true,
    hybrid: true,
    indexEtfTax: true
  });

  const toggleCategory = (cat) => {
    setExpandedCategories(prev => ({
      ...prev,
      [cat]: !prev[cat]
    }));
  };

  // Get active selected checkboxes keys
  const activeSelectedKeys = Object.keys(checkboxes).filter(k => checkboxes[k]);

  // Compute dynamic suggestions
  const getDynamicSuggestions = () => {
    const defaultSet = [
      {
        id: 'card-1',
        category: 'Small Cap Fund',
        query: 'What is the expense ratio of ICICI Prudential Small Cap Fund?',
        icon: BarChart2,
        text: 'Expense ratio of Small Cap?',
        subtext: 'FUND PARAMETERS'
      },
      {
        id: 'card-2',
        category: 'Small Cap Fund',
        query: 'Who manages the ICICI Prudential Small Cap Fund?',
        icon: Cpu,
        text: 'Fund Manager: Small Cap',
        subtext: 'MANAGEMENT'
      },
      {
        id: 'card-3',
        category: 'Flexi Cap Fund',
        query: 'What is the 3-year CAGR for ICICI Prudential Flexi Cap Fund?',
        icon: TrendingUp,
        text: '3-year CAGR for Flexi Cap',
        subtext: 'PERFORMANCE'
      },
      {
        id: 'card-4',
        category: 'ELSS Tax Saver Fund',
        query: 'What are the tax implications for ICICI Prudential ELSS Tax Saver Fund?',
        icon: Wallet,
        text: 'Tax implications for ELSS?',
        subtext: 'TAXATION'
      },
      {
        id: 'card-5',
        category: 'Multi Asset Fund',
        query: 'What is the risk profile of ICICI Prudential Multi Asset Fund?',
        icon: Shield,
        text: 'Risk profile: Multi Asset',
        subtext: 'RISK ANALYSIS'
      },
      {
        id: 'card-6',
        category: 'Focused Equity Fund',
        query: 'What is the exit load for ICICI Prudential Focused Equity Fund?',
        icon: Shield,
        text: 'Exit load for Focused Equity',
        subtext: 'REDEMPTION'
      }
    ];

    const displayAll = activeSelectedKeys.length === 0;
    if (displayAll || activeSelectedKeys.length === Object.keys(checkboxes).length) {
      return defaultSet;
    }
    
    let list = [];
    const queryTracker = new Set();

    activeSelectedKeys.forEach(key => {
      if (QUESTIONS_BY_FUND[key]) {
        QUESTIONS_BY_FUND[key].forEach((q, idx) => {
          list.push({
            id: `dynamic-${key}-${idx}`,
            category: key,
            ...q
          });
          queryTracker.add(q.query);
        });
      }
    });

    if (list.length < 6) {
      defaultSet.forEach(item => {
        if (list.length < 6 && !queryTracker.has(item.query)) {
          list.push(item);
          queryTracker.add(item.query);
        }
      });
    }

    return list.slice(0, 6);
  };
  
  const dynamicSuggestiveQuestions = getDynamicSuggestions();

  const [inputVal, setInputVal] = useState('');
  const [isArchModalOpen, setIsArchModalOpen] = useState(false);
  const [isPrivacyOpen, setIsPrivacyOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Mobile drawer visibility states
  const [isLeftOpen, setIsLeftOpen] = useState(false);
  const [isRightOpen, setIsRightOpen] = useState(false);

  // Chat Conversations State
  const [activeSession, setActiveSession] = useState('session-1');
  const [sessions, setSessions] = useState({
    'session-1': [
      { sender: 'user', text: 'Hi, what can this assistant help me with?' },
      {
        sender: 'assistant',
        text: 'I am a facts-only assistant for ICICI Prudential Mutual Funds. I can provide verified details like NAV, expense ratios, exit loads, fund managers, and minimum SIP amounts based on official sources. I do not provide investment recommendations or comparisons.',
        status: 'success',
        type: 'greeting'
      },
      { sender: 'user', text: 'Who manages the ICICI Prudential Small Cap Fund?' },
      {
        sender: 'assistant',
        text: 'The ICICI Prudential Small Cap Fund is managed by Rajat Chandak and Anish Tawakley.',
        status: 'success',
        type: 'factual',
        citation: {
          label: 'ICICI Prudential Small Cap Fund Factsheet',
          url: 'https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588'
        },
        last_updated: '2026-06-04'
      }
    ],
    'session-2': [
      { sender: 'user', text: 'What is the expense ratio for ICICI Prudential Small Cap and ELSS Tax Saver?' },
      {
        sender: 'assistant',
        text: 'The ICICI Prudential Small Cap Fund has an expense ratio of 0.7%. The ICICI Prudential ELSS Tax Saver Fund has an expense ratio of 0.9%.',
        status: 'success',
        type: 'factual',
        citation: {
          label: 'ICICI Prudential Small Cap Fund Factsheet',
          url: 'https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588'
        },
        last_updated: '2026-06-04'
      },
      { sender: 'user', text: 'Should I invest in them to save taxes?' },
      {
        sender: 'assistant',
        text: 'We detected advisory intent. As a facts-only assistant, we cannot provide investment advice. Please refer to the AMFI educational portal or a SEBI registered adviser.',
        status: 'refused',
        type: 'advisory'
      }
    ]
  });

  const [sessionNames, setSessionNames] = useState({
    'session-1': 'Chat 1',
    'session-2': 'Chat 2'
  });
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editingNameVal, setEditingNameVal] = useState('');

  const chatPaneRef = useRef(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    setTimeout(() => {
      if (chatPaneRef.current) {
        chatPaneRef.current.scrollTop = chatPaneRef.current.scrollHeight;
      }
    }, 50);
  };

  useEffect(() => {
    scrollToBottom();
  }, [sessions, activeSession, isLoading]);

  // Checkbox interactions
  const handleCheckboxChange = (key) => {
    setCheckboxes(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const deleteSession = (sessionId, e) => {
    e.stopPropagation();
    setSessions(prev => {
      const nextSessions = { ...prev };
      delete nextSessions[sessionId];
      
      if (activeSession === sessionId) {
        const remainingKeys = Object.keys(nextSessions);
        if (remainingKeys.length > 0) {
          setActiveSession(remainingKeys[remainingKeys.length - 1]);
        } else {
          setActiveSession(null);
        }
      }
      return nextSessions;
    });
  };

  const startEditing = (sessionId, currentName, e) => {
    e.stopPropagation();
    setEditingSessionId(sessionId);
    setEditingNameVal(currentName);
  };

  const handleRenameSave = (sessionId) => {
    if (editingNameVal.trim()) {
      setSessionNames(prev => ({
        ...prev,
        [sessionId]: editingNameVal.trim()
      }));
    }
    setEditingSessionId(null);
  };

  const handleRenameKeyDown = (sessionId, e) => {
    if (e.key === 'Enter') {
      handleRenameSave(sessionId);
    } else if (e.key === 'Escape') {
      setEditingSessionId(null);
    }
  };

  // Form submission handler
  const sendQuery = async (queryText) => {
    if (!queryText.trim()) return;
    
    const userMsg = { sender: 'user', text: queryText };
    
    let targetSession = activeSession;
    if (!targetSession) {
      targetSession = `session-${Date.now()}`;
      setActiveSession(targetSession);
      setSessionNames(prev => ({
        ...prev,
        [targetSession]: `Chat ${Object.keys(sessions).length + 1}`
      }));
      setSessions(prev => ({
        ...prev,
        [targetSession]: [userMsg]
      }));
    } else {
      setSessions(prev => ({
        ...prev,
        [targetSession]: [...(prev[targetSession] || []), userMsg]
      }));
    }
    
    setIsLoading(true);
    
    try {
      const selectedFunds = activeSelectedKeys.map(k => fundIdMap[k]).filter(Boolean);
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: queryText,
          session_id: targetSession,
          selected_funds: selectedFunds
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }
      
      const responseData = await response.json();
      
      setSessions(prev => ({
        ...prev,
        [targetSession]: [...(prev[targetSession] || []), responseData]
      }));
      
    } catch (err) {
      console.error('API Query Error:', err);
      setSessions(prev => ({
        ...prev,
        [targetSession]: [...(prev[targetSession] || []), {
          status: 'refused',
          type: 'pii', // triggers error theme
          answer: 'Failed to communicate with RAG Assistant server. Please check that backend server is running on port 8000.'
        }]
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    sendQuery(inputVal.trim());
    setInputVal('');
  };

  // Switch between sessions
  const handleSessionChange = (sessionId) => {
    setActiveSession(sessionId);
    setIsLeftOpen(false);
    setIsRightOpen(false);
  };

  // Reset to New Chat welcome state
  const handleNewChat = () => {
    setActiveSession(null);
    setInputVal('');
    setIsLeftOpen(false);
    setIsRightOpen(false);
  };

  // Click on recently asked
  const handleAskedClick = (query) => {
    setInputVal(query);
    setIsRightOpen(false);
  };

  const activeMessages = activeSession ? (sessions[activeSession] || []) : [];

  return (
    <div className="app-layout">
      
      {/* Mobile left-right toggle trigger buttons */}
      <button 
        className="mobile-toggle-btn" 
        onClick={() => { setIsLeftOpen(!isLeftOpen); setIsRightOpen(false); }}
        aria-label="Toggle Left Sidebar"
        style={{ left: '8px' }}
      >
        <Menu />
      </button>

      <button 
        className="mobile-toggle-btn" 
        onClick={() => { setIsRightOpen(!isRightOpen); setIsLeftOpen(false); }}
        aria-label="Toggle Right Sidebar"
        style={{ right: '8px', left: 'auto' }}
      >
        <MessageSquare />
      </button>

      {/* 1. LEFT SIDEBAR: Brand & Filters (15 Schemes) */}
      <aside className={`sidebar-left ${isLeftOpen ? 'open' : ''}`} id="sidebar-left">
        <div className="brand-container">
          <div className="indmoney-logo" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="brand-text" style={{ fontSize: '1.25rem', color: 'var(--primary-blue)', fontWeight: '750', letterSpacing: '-0.02em', fontFamily: 'var(--font-heading)' }}>
              INDMoney
            </span>
            <span className="ai-badge">AI</span>
          </div>
        </div>

        <div className="amc-header">
          <Folder className="amc-icon" />
          <span>ICICI PRUDENTIAL MF</span>
        </div>

        {/* Selected Funds Summary at the top of the Left Sidebar */}
        <div className="sidebar-selected-summary" style={{
          marginBottom: '15px',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '12px',
          paddingLeft: '4px'
        }}>
          <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-navy)', textTransform: 'uppercase', display: 'block' }}>
            Selected ({activeSelectedKeys.length > 0 ? activeSelectedKeys.length : 'All 15'})
          </span>
        </div>

        {/* Default Behavior Note */}
        <div style={{
          fontSize: '0.7rem',
          color: 'var(--text-muted)',
          backgroundColor: 'var(--bg-sidebar)',
          border: '1px solid var(--border-color)',
          borderRadius: '6px',
          padding: '6px 8px',
          marginBottom: '15px',
          lineHeight: '1.3'
        }}>
          💡 <b>Default behavior:</b> All 15 funds are selected for context if none are checked.
        </div>

        <div className="filters-container">
          {/* Category 1: Equity Funds (7) */}
          <div className="filter-section">
            <h3 
              className="filter-section-title"
              onClick={() => toggleCategory('equity')}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
            >
              <span>Equity Funds</span>
              {expandedCategories.equity ? <ChevronDown style={{ width: '14px', height: '14px' }} /> : <ChevronRight style={{ width: '14px', height: '14px' }} />}
            </h3>
            {expandedCategories.equity && (
              <ul className="filter-list">
                {[
                  { label: 'Small Cap Fund', val: 'Small Cap Fund' },
                  { label: 'Large & Mid Cap', val: 'Large & Mid Cap Fund' },
                  { label: 'Flexi Cap Fund', val: 'Flexi Cap Fund' },
                  { label: 'Focused Equity', val: 'Focused Equity Fund' },
                  { label: 'Mid Cap Fund', val: 'Mid Cap Fund' },
                  { label: 'Multi Cap Fund', val: 'Multi Cap Fund' },
                  { label: 'Large Cap Fund', val: 'Large Cap Fund' }
                ].map((item) => (
                  <li key={item.val}>
                    <label className="checkbox-container">
                      <input 
                        type="checkbox" 
                        name="scheme" 
                        value={item.val} 
                        checked={checkboxes[item.val] || false}
                        onChange={() => handleCheckboxChange(item.val)} 
                      />
                      <span className="checkmark"></span>
                      <span className="label-text">{item.label}</span>
                    </label>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Category 2: Hybrid Funds (4) */}
          <div className="filter-section">
            <h3 
              className="filter-section-title"
              onClick={() => toggleCategory('hybrid')}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
            >
              <span>Hybrid Funds</span>
              {expandedCategories.hybrid ? <ChevronDown style={{ width: '14px', height: '14px' }} /> : <ChevronRight style={{ width: '14px', height: '14px' }} />}
            </h3>
            {expandedCategories.hybrid && (
              <ul className="filter-list">
                {[
                  { label: 'Equity Savings', val: 'Equity Savings Fund' },
                  { label: 'Equity & Debt', val: 'Equity & Debt Fund' },
                  { label: 'Regular Savings', val: 'Regular Savings Fund' },
                  { label: 'Multi Asset Fund', val: 'Multi Asset Fund' }
                ].map((item) => (
                  <li key={item.val}>
                    <label className="checkbox-container">
                      <input 
                        type="checkbox" 
                        name="scheme" 
                        value={item.val} 
                        checked={checkboxes[item.val] || false}
                        onChange={() => handleCheckboxChange(item.val)}
                      />
                      <span className="checkmark"></span>
                      <span className="label-text">{item.label}</span>
                    </label>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Category 3: Index & ETFs & Tax (4) */}
          <div className="filter-section">
            <h3 
              className="filter-section-title"
              onClick={() => toggleCategory('indexEtfTax')}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
            >
              <span>Index, ETFs & Tax</span>
              {expandedCategories.indexEtfTax ? <ChevronDown style={{ width: '14px', height: '14px' }} /> : <ChevronRight style={{ width: '14px', height: '14px' }} />}
            </h3>
            {expandedCategories.indexEtfTax && (
              <ul className="filter-list">
                {[
                  { label: 'ELSS Tax Saver', val: 'ELSS Tax Saver Fund' },
                  { label: 'Nifty 50 Index', val: 'Nifty 50 Index Fund' },
                  { label: 'Gold ETF FoF', val: 'Gold ETF FoF' },
                  { label: 'Silver ETF FoF', val: 'Silver ETF FoF' }
                ].map((item) => (
                  <li key={item.val}>
                    <label className="checkbox-container">
                      <input 
                        type="checkbox" 
                        name="scheme" 
                        value={item.val} 
                        checked={checkboxes[item.val] || false}
                        onChange={() => handleCheckboxChange(item.val)}
                      />
                      <span className="checkmark"></span>
                      <span className="label-text">{item.label}</span>
                    </label>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

      </aside>

      {/* 2. CENTER PANEL: Chat Area (Disclaimer Badge aligned right) */}
      <main className="center-panel">
        <div className="center-header">
          <div className="compliance-warning-badge">
            <AlertTriangle className="warning-badge-icon" />
            <span>Facts-Only. No Investment Advice.</span>
          </div>
        </div>



        {/* Chat Pane */}
        <section className="chat-pane" ref={chatPaneRef} id="chat-pane">
          {(!activeSession || activeMessages.length === 0) ? (
            /* Welcome Screen Container */
            <div className="welcome-container" id="welcome-container">
              <div className="welcome-heading-group">
                <h1 className="welcome-title">How can I help you today?</h1>
                <p className="welcome-subtitle">Ask me anything about ICICI Prudential funds, expense ratios, tax implications, or performance data.</p>
              </div>

              {/* Grid of suggestive prompt cards */}
              <div className="suggestive-grid">
                {dynamicSuggestiveQuestions.map((q) => {
                  const IconComponent = q.icon;
                  return (
                    <div 
                      key={q.id}
                      className="question-card"
                      onClick={() => sendQuery(q.query)}
                    >
                      <div className="card-icon-box">
                        <IconComponent />
                      </div>
                      <div className="card-content-box">
                        <p className="card-text">{q.text}</p>
                        <span className="card-subtext">{q.subtext}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Chat message logs */
            <div className="messages-container" id="messages-container">
              {activeMessages.map((msg, index) => {
                const isUser = msg.sender === 'user';
                return (
                  <div key={index} className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
                    {msg.status === 'refused' ? (
                      /* Refusal panel formatting */
                      <div className={`refusal-panel ${msg.type === 'pii' ? 'error' : 'warning'}`}>
                        <div className="refusal-icon-container">
                          {msg.type === 'pii' ? <ShieldAlert /> : <AlertTriangle />}
                        </div>
                        <div className="refusal-content">
                          <h4 className="refusal-title">
                            {msg.type === 'pii' ? 'PII Security Block' : 'Regulatory Notice'}
                          </h4>
                          <p className="refusal-text">{msg.answer}</p>
                          
                          {/* Conditional educational links */}
                          {msg.type === 'advisory' && (
                            <a 
                              href="https://www.amfiindia.com/investor-corner/education/interest-rates.html" 
                              target="_blank" 
                              rel="noreferrer"
                              className="refusal-action-link"
                            >
                              Visit AMFI Investor Education <ExternalLink style={{ width: '12px', height: '12px', display: 'inline', marginLeft: '2px' }} />
                            </a>
                          )}
                          {msg.type === 'comparison' && (
                            <a 
                              href="https://www.sebi.gov.in" 
                              target="_blank" 
                              rel="noreferrer"
                              className="refusal-action-link"
                            >
                              Visit SEBI Portal <ExternalLink style={{ width: '12px', height: '12px', display: 'inline', marginLeft: '2px' }} />
                            </a>
                          )}
                        </div>
                      </div>
                    ) : (
                      /* Standard factual bubble */
                      <div className="message-bubble">
                        <p>{isUser ? msg.text : (msg.answer || msg.text)}</p>
                        
                        {/* Citation blocks */}
                        {(msg.citation || msg.last_updated) && (
                          <div className="message-citation-block">
                            {msg.citation && (
                              <a 
                                className="citation-pill" 
                                href={msg.citation.url} 
                                target="_blank" 
                                rel="noreferrer"
                                title={`Verify official factsheet at ${msg.citation.label}`}
                              >
                                <Folder style={{ width: '10px', height: '10px', marginRight: '3px' }} />
                                <span>{msg.citation.label || 'Factsheet Source'}</span>
                              </a>
                            )}
                            {msg.last_updated && (
                              <span className="message-last-updated">
                                Updated: {new Date(msg.last_updated).toLocaleDateString('en-US', {
                                  year: 'numeric', month: 'short', day: 'numeric'
                                })}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Typing Indicator bubbles */}
          {isLoading && (
            <div className="typing-indicator" id="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}
        </section>

        {/* Footer controls & input */}
        <footer className="center-footer">
          <form className="chat-form" onSubmit={handleFormSubmit}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', marginBottom: '4px' }}>
              {/* Active Selected Funds count and pills display (placed stacked above input field) */}
              <div className="chat-selected-summary-bottom" style={{
                display: 'flex',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '8px',
                paddingLeft: '4px',
                userSelect: 'none',
                marginBottom: '8px'
              }}>
                <span style={{ fontFamily: 'var(--font-heading)', fontWeight: '700', fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: '4px' }}>
                  Selected: [ {activeSelectedKeys.length === 0 ? 'All 15 Funds' : activeSelectedKeys.length} ] {activeSelectedKeys.length === 0 && '(Default)'}
                </span>
                {activeSelectedKeys.map(key => (
                  <span 
                    key={key} 
                    onClick={() => handleCheckboxChange(key)}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      backgroundColor: 'var(--bg-active-pill)',
                      color: 'var(--text-active-pill)',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '10px',
                      fontWeight: '500',
                      cursor: 'pointer',
                      border: '1px solid var(--border-color)',
                      transition: 'all 0.15s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--error-bg)';
                      e.currentTarget.style.color = 'var(--error-text)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--bg-active-pill)';
                      e.currentTarget.style.color = 'var(--text-active-pill)';
                    }}
                    title={`Click to remove ${key}`}
                  >
                    {key} <X style={{ width: '10px', height: '10px' }} />
                  </span>
                ))}
              </div>
              <div className="input-box-wrapper" style={{ width: '100%' }}>
                <input 
                  type="text" 
                  id="chat-input" 
                  placeholder="Type your financial question here..." 
                  value={inputVal}
                  onChange={(e) => setInputVal(e.target.value)}
                  disabled={isLoading}
                  autoComplete="off"
                />
                <button type="submit" className="send-btn" disabled={isLoading} aria-label="Send Message">
                  <Send />
                </button>
              </div>
            </div>
          </form>

          <div className="footer-links-row">
            <div className="last-updated-notice">
              <Clock />
              <span>Last updated from official AMC sources.</span>
            </div>
            <div className="compliance-links">
              <span className="footer-link-btn" onClick={() => setIsArchModalOpen(true)}>System Architecture</span>
              <span className="divider">•</span>
              <span className="footer-link-btn" onClick={() => setIsPrivacyOpen(true)}>Privacy Policy</span>
            </div>
          </div>
        </footer>
      </main>

      {/* 3. RIGHT SIDEBAR: History & How it Works */}
      <aside className={`sidebar-right ${isRightOpen ? 'open' : ''}`} id="sidebar-right">
        <div className="sidebar-right-action">
          <button className="btn-new-chat" onClick={handleNewChat}>
            <Plus />
            <span>New Chat</span>
          </button>
        </div>

        <div className="sidebar-right-section">
          <h3 className="sidebar-right-title">Recent Conversations</h3>
          <ul className="chat-threads-list">
            {Object.keys(sessions).map((sessionId, index) => {
              const currentName = sessionNames[sessionId] || `Chat ${index + 1}`;
              const isEditing = editingSessionId === sessionId;
              return (
                <li 
                  key={sessionId}
                  className={`thread-item ${activeSession === sessionId ? 'active' : ''}`} 
                  onClick={() => handleSessionChange(sessionId)}
                >
                  <div className="thread-title-group" style={{ display: 'flex', alignItems: 'center', gap: '8px', flexGrow: 1, minWidth: 0 }}>
                    <MessageSquare style={{ flexShrink: 0 }} />
                    {isEditing ? (
                      <input 
                        type="text"
                        value={editingNameVal}
                        onChange={(e) => setEditingNameVal(e.target.value)}
                        onBlur={() => handleRenameSave(sessionId)}
                        onKeyDown={(e) => handleRenameKeyDown(sessionId, e)}
                        autoFocus
                        style={{
                          background: 'var(--bg-sidebar)',
                          border: '1.5px solid var(--primary-blue)',
                          borderRadius: '4px',
                          color: 'var(--text-navy)',
                          fontSize: '0.8rem',
                          padding: '2px 4px',
                          width: '100%',
                          outline: 'none'
                        }}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <span 
                        onDoubleClick={(e) => startEditing(sessionId, currentName, e)}
                        style={{ cursor: 'pointer', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                        title="Double click to rename"
                      >
                        {currentName}
                      </span>
                    )}
                  </div>
                  
                  <div className="thread-actions" style={{ display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
                    {!isEditing && (
                      <button 
                        className="delete-btn" 
                        onClick={(e) => startEditing(sessionId, currentName, e)}
                        title="Rename conversation"
                        aria-label={`Rename Chat ${index + 1}`}
                      >
                        <Edit2 style={{ width: '12px', height: '12px' }} />
                      </button>
                    )}
                    <button 
                      className="delete-btn" 
                      onClick={(e) => deleteSession(sessionId, e)}
                      title="Delete conversation"
                      aria-label={`Delete Chat ${index + 1}`}
                    >
                      <Trash2 style={{ width: '13px', height: '13px' }} />
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="how-it-works-card">
          <div className="how-header">
            <Info className="how-info-icon" />
            <span>HOW IT WORKS?</span>
          </div>
          <ul className="how-list">
            <li>
              <CheckCircle className="how-check-icon" />
              <span>Factual answers only (NAV, AUM, returns, holdings, etc.)</span>
            </li>
            <li>
              <CheckCircle className="how-check-icon" />
              <span>No advice or comparisons; short replies with sources</span>
            </li>
            <li>
              <CheckCircle className="how-check-icon" />
              <span>Rejects PII and opinion questions</span>
            </li>
          </ul>
          <div className="how-footer">
            AI-generated responses. Verify with cited sources. Free-tier API: wait a few minutes if limits are hit.
          </div>
        </div>

        <div className="sidebar-right-section recently-asked-box">
          <h3 className="sidebar-right-title">Recently Asked</h3>
          <ul className="recently-asked-list">
            <li 
              className="asked-item" 
              onClick={() => handleAskedClick("What is the minimum investment amount for ICICI Prudential Large & Mid Cap Fund?")}
              title="What is the minimum investment amount for ICICI Prudential Large & Mid Cap Fund?"
            >
              <Search style={{ flexShrink: 0 }} />
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>Min investment: Large & Mid Cap</span>
            </li>
            <li 
              className="asked-item" 
              onClick={() => handleAskedClick("What is the AUM of ICICI Prudential Equity & Debt Fund?")}
              title="What is the AUM of ICICI Prudential Equity & Debt Fund?"
            >
              <Search style={{ flexShrink: 0 }} />
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>AUM of Equity & Debt</span>
            </li>
            <li 
              className="asked-item" 
              onClick={() => handleAskedClick("What is the lock-in period for ICICI Prudential ELSS Tax Saver Fund?")}
              title="What is the lock-in period for ICICI Prudential ELSS Tax Saver Fund?"
            >
              <Search style={{ flexShrink: 0 }} />
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>Lock-in period: ELSS</span>
            </li>
            <li 
              className="asked-item" 
              onClick={() => handleAskedClick("What is the benchmark index of ICICI Prudential Nifty 50 Index Fund?")}
              title="What is the benchmark index of ICICI Prudential Nifty 50 Index Fund?"
            >
              <Search style={{ flexShrink: 0 }} />
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>Benchmark of Nifty 50 Index</span>
            </li>
            <li 
              className="asked-item" 
              onClick={() => handleAskedClick("What is the tracking error of ICICI Prudential Nifty 50 Index Fund?")}
              title="What is the tracking error of ICICI Prudential Nifty 50 Index Fund?"
            >
              <Search style={{ flexShrink: 0 }} />
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>Tracking error: Nifty 50 Index</span>
            </li>
          </ul>
        </div>
      </aside>

      {/* Mobile overlay backdrops */}
      <div 
        className={`mobile-overlay ${isLeftOpen ? 'open' : ''}`} 
        onClick={() => setIsLeftOpen(false)}
        id="mobile-overlay-left"
      ></div>
      
      <div 
        className={`mobile-overlay ${isRightOpen ? 'open' : ''}`} 
        onClick={() => setIsRightOpen(false)}
        id="mobile-overlay-right"
      ></div>

      {/* 4. System Design Modal */}
      <div className={`modal-overlay ${isArchModalOpen ? 'open' : ''}`}>
        <div className="modal-container">
          <div className="modal-header">
            <h2 className="modal-title">System Architecture (Facts-Only RAG)</h2>
            <button className="close-btn" onClick={() => setIsArchModalOpen(false)} aria-label="Close Modal">
              <X />
            </button>
          </div>
          <div className="modal-body">
            <div className="workflow-steps">
              
              <div className="workflow-step">
                <div className="step-icon"><DownloadCloud style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4>1. Scraper & Parser</h4>
                  <p>Fetches client props from 15 INDMoney URLs using <code>curl-cffi</code> Chrome impersonation. Extracts 13 key parameters directly from <code>__NEXT_DATA__</code>.</p>
                </div>
              </div>

              <div className="workflow-step">
                <div className="step-icon"><Binary style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4>2. Chunking & Embeddings</h4>
                  <p>Chunks metadata with context-aware prefixes (Scheme + Plan). Generates 1024-dimension embeddings via local <code>BAAI/bge-large-en-v1.5</code>.</p>
                </div>
              </div>

              <div className="workflow-step">
                <div className="step-icon"><Database style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4>3. Vector DB Retrieval</h4>
                  <p>Stores vectors in ChromaDB. Uses cosine similarity with strict L2 distance threshold filters to omit irrelevant sources.</p>
                </div>
              </div>

              <div className="workflow-step">
                <div className="step-icon"><ShieldAlert style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4>4. Query Classification</h4>
                  <p>Pre-evaluates input for PII leaks (PAN, Aadhaar), advisory intent, performance comparisons, and greetings using strict regex and classifiers.</p>
                </div>
              </div>

              <div className="workflow-step">
                <div className="step-icon"><Cpu style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4>5. Generation (Groq LLaMA 3.3)</h4>
                  <p>Forwards retrieved facts to <code>llama-3.3-70b-versatile</code>. Enforces a strict response limit of ≤3 sentences, no investment advice, and 1 source citation.</p>
                </div>
              </div>

              <div className="workflow-step">
                <div className="step-icon"><CheckSquare style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4>6. Output Validation</h4>
                  <p>Validates sentence limit, citation inclusion, and scraper timestamp. Truncates and auto-corrects before serving response.</p>
                </div>
              </div>

            </div>

            <div className="compliance-box-warning">
              <h5>Compliance Rules Guardrail</h5>
              <ul>
                <li>No comparisons: Triggers polite refusals.</li>
                <li>No advisory: Prompts redirect to AMFI educational portal.</li>
                <li>No PII leakage: Phone/PAN checks immediately quarantine queries before LLM input.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Privacy Policy Details Modal */}
      <div className={`modal-overlay ${isPrivacyOpen ? 'open' : ''}`}>
        <div className="modal-container">
          <div className="modal-header">
            <h2 className="modal-title">Privacy Policy & Security Guardrails</h2>
            <button className="close-btn" onClick={() => setIsPrivacyOpen(false)} aria-label="Close Privacy Modal">
              <X />
            </button>
          </div>
          <div className="modal-body">
            <div className="compliance-box-warning" style={{ backgroundColor: '#ECFDF3', borderColor: '#A7F3D0', color: '#047857' }}>
              <h5 style={{ fontFamily: 'var(--font-heading)', fontWeight: 700 }}>Strict Regulatory Compliance & Safety Shield</h5>
              <p style={{ fontSize: '0.8rem', lineHeight: 1.45, marginTop: '0.25rem' }}>
                In strict alignment with SEBI, AMFI, and INDMoney security guidelines, this Facts-Only FAQ Assistant enforces the following data protection protocols:
              </p>
            </div>

            <div className="workflow-steps" style={{ marginTop: '0.5rem' }}>
              <div className="workflow-step" style={{ backgroundColor: '#FFFFFF' }}>
                <div className="step-icon" style={{ backgroundColor: '#FEE2E2', color: '#991B1B' }}><ShieldAlert style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4 style={{ color: '#991B1B' }}>Zero PII Retention</h4>
                  <p>Our pipeline incorporates query classifier filters that identify and block Personal Identifiable Information (PAN cards, Aadhaar cards, phone numbers, email addresses, and OTP codes) prior to processing.</p>
                </div>
              </div>

              <div className="workflow-step" style={{ backgroundColor: '#FFFFFF' }}>
                <div className="step-icon" style={{ backgroundColor: '#E0F2FE', color: '#0369A1' }}><Database style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4 style={{ color: '#0369A1' }}>No Data Caching or Logs</h4>
                  <p>All query interactions are processed in volatile memory. No user inputs, vector queries, or financial profile attributes are ever cached, saved, or logged to disk.</p>
                </div>
              </div>

              <div className="workflow-step" style={{ backgroundColor: '#FFFFFF' }}>
                <div className="step-icon" style={{ backgroundColor: '#FEF3C7', color: '#D97706' }}><Info style={{ width: '14px', height: '14px' }} /></div>
                <div className="step-info">
                  <h4 style={{ color: '#D97706' }}>Official Facts Isolation</h4>
                  <p>Retrieval focuses exclusively on verified factsheets directly matched from official public AMC URLs. The system does not possess any links to client portfolios or transaction gateways.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

export default App;
