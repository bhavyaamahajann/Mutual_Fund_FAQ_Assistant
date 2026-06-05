import { useState, useEffect, useRef } from 'react';
import { Menu, MessageSquare, BarChart2, Cpu, TrendingUp, Shield, Wallet } from 'lucide-react';
import { SidebarLeft } from './ui/SidebarLeft';
import { SidebarRight } from './ui/SidebarRight';
import { ChatArea } from './ui/ChatArea';
import { Modals } from './ui/Modals';

const API_URL = import.meta.env.VITE_API_URL || 
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api/chat'
    : '/api/chat');

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
    { query: 'What is the expense ratio of Small Cap Fund?', icon: BarChart2, text: 'What is the expense ratio of Small Cap Fund?', subtext: 'FUND PARAMETERS' },
    { query: 'Who manages the ICICI Prudential Small Cap Fund?', icon: Cpu, text: 'Who manages the ICICI Prudential Small Cap Fund?', subtext: 'MANAGEMENT' }
  ],
  'Large & Mid Cap Fund': [
    { query: 'What is the minimum investment amount for ICICI Prudential Large & Mid Cap Fund?', icon: Wallet, text: 'Min investment Large & Mid Cap', subtext: 'FUND PARAMETERS' }
  ],
  'Flexi Cap Fund': [
    { query: 'What is the sector-wise allocation of Flexi Cap Fund?', icon: TrendingUp, text: 'What is the sector-wise allocation of Flexi Cap Fund?', subtext: 'PORTFOLIO ANALYSIS' }
  ],
  'Focused Equity Fund': [
    { query: 'What is the exit load of Focused Equity Fund?', icon: Shield, text: 'What is the exit load of Focused Equity Fund?', subtext: 'REDEMPTION' }
  ],
  'Mid Cap Fund': [
    { query: 'Who are the fund managers of ICICI Prudential Mid Cap Fund?', icon: Cpu, text: 'Fund Managers: Mid Cap', subtext: 'MANAGEMENT' }
  ],
  'Multi Cap Fund': [
    { query: 'What is the expense ratio of ICICI Prudential Multi Cap Fund?', icon: BarChart2, text: 'Expense ratio: Multi Cap', subtext: 'FUND PARAMETERS' }
  ],
  'Large Cap Fund': [
    { query: 'Who is the fund manager of Large Cap Fund?', icon: Cpu, text: 'Who is the fund manager of Large Cap Fund?', subtext: 'MANAGEMENT' }
  ],
  'Equity Savings Fund': [
    { query: 'What is the exit load of ICICI Prudential Equity Savings Fund?', icon: Shield, text: 'Exit load: Equity Savings', subtext: 'REDEMPTION' }
  ],
  'Equity & Debt Fund': [
    { query: 'What is the AUM of ICICI Prudential Equity & Debt Fund?', icon: BarChart2, text: 'AUM of Equity & Debt', subtext: 'AUM SIZE' }
  ],
  'Regular Savings Fund': [
    { query: 'Who manages the ICICI Prudential Regular Savings Fund?', icon: Cpu, text: 'Fund Manager: Regular Savings', subtext: 'MANAGEMENT' }
  ],
  'Multi Asset Fund': [
    { query: 'What is the riskometer classification of Multi Asset Fund?', icon: Shield, text: 'What is the riskometer classification of Multi Asset Fund?', subtext: 'RISK PROFILE' }
  ],
  'ELSS Tax Saver Fund': [
    { query: 'What are the tax implications for ICICI Prudential ELSS Tax Saver Fund?', icon: Wallet, text: 'Tax implications for ELSS?', subtext: 'TAXATION' },
    { query: 'What is the lock-in period for ICICI Prudential ELSS Tax Saver Fund?', icon: Wallet, text: 'Lock-in period: ELSS', subtext: 'TAXATION' }
  ],
  'Nifty 50 Index Fund': [
    { query: 'What is the tracking error of ICICI Prudential Nifty 50 Index Fund?', icon: TrendingUp, text: 'Tracking error: Nifty 50 Index', subtext: 'PERFORMANCE' }
  ],
  'Gold ETF FoF': [
    { query: 'What is the exit load of ICICI Prudential Gold ETF Fund of Fund?', icon: Shield, text: 'Exit load: Gold ETF FoF', subtext: 'REDEMPTION' }
  ],
  'Silver ETF FoF': [
    { query: 'What is the minimum investment for ICICI Prudential Silver ETF Fund of Fund?', icon: Wallet, text: 'Min investment: Silver ETF FoF', subtext: 'FUND PARAMETERS' }
  ]
};

function App() {
  const [checkboxes, setCheckboxes] = useState({
    'Small Cap Fund': false,
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
    equity: false,
    hybrid: false,
    indexEtfTax: false
  });

  const toggleCategory = (cat) => {
    setExpandedCategories(prev => ({
      ...prev,
      [cat]: !prev[cat]
    }));
  };

  const activeSelectedKeys = Object.keys(checkboxes).filter(k => checkboxes[k]);

  const getDynamicSuggestions = () => {
    const defaultSet = [
      { id: 'card-1', category: 'Small Cap Fund', query: 'What is the AUM of all ICICI Prudential funds?', icon: BarChart2, text: 'What is the AUM of all ICICI Prudential funds?', subtext: 'FUND OVERVIEW' },
      { id: 'card-2', category: 'Small Cap Fund', query: 'What is the expense ratio of Small Cap Fund?', icon: BarChart2, text: 'What is the expense ratio of Small Cap Fund?', subtext: 'FUND PARAMETERS' },
      { id: 'card-3', category: 'Flexi Cap Fund', query: 'What is the sector-wise allocation of Flexi Cap Fund?', icon: TrendingUp, text: 'What is the sector-wise allocation of Flexi Cap Fund?', subtext: 'PORTFOLIO ANALYSIS' },
      { id: 'card-4', category: 'Large Cap Fund', query: 'Who is the fund manager of Large Cap Fund?', icon: Cpu, text: 'Who is the fund manager of Large Cap Fund?', subtext: 'MANAGEMENT' },
      { id: 'card-5', category: 'Multi Asset Fund', query: 'What is the riskometer classification of Multi Asset Fund?', icon: Shield, text: 'What is the riskometer classification of Multi Asset Fund?', subtext: 'RISK PROFILE' },
      { id: 'card-6', category: 'Focused Equity Fund', query: 'What is the exit load of Focused Equity Fund?', icon: Shield, text: 'What is the exit load of Focused Equity Fund?', subtext: 'REDEMPTION' }
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
          list.push({ id: `dynamic-${key}-${idx}`, category: key, ...q });
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
  
  const [isLeftOpen, setIsLeftOpen] = useState(false);
  const [isRightOpen, setIsRightOpen] = useState(false);

  const [activeSession, setActiveSession] = useState(null);
  const [sessions, setSessions] = useState({
    'session-1': [
      { sender: 'user', text: 'Hi, what can this assistant help me with?' },
      { sender: 'assistant', text: 'I am a facts-only assistant for ICICI Prudential Mutual Funds. I can provide verified details like NAV, expense ratios, exit loads, fund managers, and minimum SIP amounts based on official sources. I do not provide investment recommendations or comparisons.', status: 'success', type: 'greeting' },
      { sender: 'user', text: 'Who manages the ICICI Prudential Small Cap Fund?' },
      { sender: 'assistant', text: 'The ICICI Prudential Small Cap Fund is managed by Rajat Chandak and Anish Tawakley.', status: 'success', type: 'factual', citation: { label: 'ICICI Prudential Small Cap Fund Factsheet', url: 'https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588' }, last_updated: '2026-06-04' }
    ],
    'session-2': [
      { sender: 'user', text: 'What is the expense ratio for ICICI Prudential Small Cap and ELSS Tax Saver?' },
      { sender: 'assistant', text: 'The ICICI Prudential Small Cap Fund has an expense ratio of 0.7%. The ICICI Prudential ELSS Tax Saver Fund has an expense ratio of 0.9%.', status: 'success', type: 'factual', citation: { label: 'ICICI Prudential Small Cap Fund Factsheet', url: 'https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588' }, last_updated: '2026-06-04' },
      { sender: 'user', text: 'Should I invest in them to save taxes?' },
      { sender: 'assistant', text: 'We detected advisory intent. As a facts-only assistant, we cannot provide investment advice. Please refer to the AMFI educational portal or a SEBI registered adviser.', status: 'refused', type: 'advisory' }
    ]
  });

  const [sessionNames, setSessionNames] = useState({
    'session-1': 'Chat 1',
    'session-2': 'Chat 2'
  });
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editingNameVal, setEditingNameVal] = useState('');

  const chatPaneRef = useRef(null);

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

  const handleCheckboxChange = (key) => {
    setCheckboxes(prev => ({ ...prev, [key]: !prev[key] }));
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
      setSessionNames(prev => ({ ...prev, [sessionId]: editingNameVal.trim() }));
    }
    setEditingSessionId(null);
  };

  const handleRenameKeyDown = (sessionId, e) => {
    if (e.key === 'Enter') handleRenameSave(sessionId);
    else if (e.key === 'Escape') setEditingSessionId(null);
  };

  const sendQuery = async (queryText) => {
    if (!queryText.trim()) return;
    const userMsg = { sender: 'user', text: queryText };
    
    let targetSession = activeSession;
    if (!targetSession) {
      targetSession = `session-${Date.now()}`;
      setActiveSession(targetSession);
      setSessionNames(prev => ({ ...prev, [targetSession]: `Chat ${Object.keys(sessions).length + 1}` }));
      setSessions(prev => ({ ...prev, [targetSession]: [userMsg] }));
    } else {
      setSessions(prev => ({ ...prev, [targetSession]: [...(prev[targetSession] || []), userMsg] }));
    }
    
    setIsLoading(true);
    
    try {
      const selectedFunds = activeSelectedKeys.map(k => fundIdMap[k]).filter(Boolean);
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText, session_id: targetSession, selected_funds: selectedFunds })
      });
      
      if (!response.ok) throw new Error(`Server returned HTTP ${response.status}`);
      const responseData = await response.json();
      
      setSessions(prev => ({ ...prev, [targetSession]: [...(prev[targetSession] || []), responseData] }));
    } catch (err) {
      console.error('API Query Error:', err);
      setSessions(prev => ({
        ...prev,
        [targetSession]: [...(prev[targetSession] || []), {
          status: 'refused',
          type: 'pii',
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

  const handleSessionChange = (sessionId) => {
    setActiveSession(sessionId);
    setIsLeftOpen(false);
    setIsRightOpen(false);
  };

  const handleNewChat = () => {
    setActiveSession(null);
    setInputVal('');
    setIsLeftOpen(false);
    setIsRightOpen(false);
  };

  const handleAskedClick = (query) => {
    setInputVal(query);
    setIsRightOpen(false);
  };

  const activeMessages = activeSession ? (sessions[activeSession] || []) : [];

  return (
    <div className="app-layout">
      
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

      <SidebarLeft 
        isLeftOpen={isLeftOpen}
        toggleCategory={toggleCategory}
        expandedCategories={expandedCategories}
        checkboxes={checkboxes}
        handleCheckboxChange={handleCheckboxChange}
        activeSelectedKeys={activeSelectedKeys}
      />

      <ChatArea 
        chatPaneRef={chatPaneRef}
        activeSession={activeSession}
        activeMessages={activeMessages}
        dynamicSuggestiveQuestions={dynamicSuggestiveQuestions}
        sendQuery={sendQuery}
        isLoading={isLoading}
        handleFormSubmit={handleFormSubmit}
        activeSelectedKeys={activeSelectedKeys}
        handleCheckboxChange={handleCheckboxChange}
        inputVal={inputVal}
        setInputVal={setInputVal}
        setIsArchModalOpen={setIsArchModalOpen}
        setIsPrivacyOpen={setIsPrivacyOpen}
      />

      <SidebarRight 
        isRightOpen={isRightOpen}
        handleNewChat={handleNewChat}
        sessions={sessions}
        sessionNames={sessionNames}
        editingSessionId={editingSessionId}
        activeSession={activeSession}
        handleSessionChange={handleSessionChange}
        editingNameVal={editingNameVal}
        setEditingNameVal={setEditingNameVal}
        handleRenameSave={handleRenameSave}
        handleRenameKeyDown={handleRenameKeyDown}
        startEditing={startEditing}
        deleteSession={deleteSession}
        handleAskedClick={handleAskedClick}
      />

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

      <Modals 
        isArchModalOpen={isArchModalOpen}
        setIsArchModalOpen={setIsArchModalOpen}
        isPrivacyOpen={isPrivacyOpen}
        setIsPrivacyOpen={setIsPrivacyOpen}
      />

    </div>
  );
}

export default App;
