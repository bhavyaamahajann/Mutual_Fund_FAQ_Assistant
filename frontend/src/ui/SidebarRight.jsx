import { 
  Plus, 
  MessageSquare, 
  Edit2, 
  Trash2, 
  Info, 
  CheckCircle, 
  Search 
} from 'lucide-react';

export const SidebarRight = ({
  isRightOpen,
  handleNewChat,
  sessions,
  sessionNames,
  editingSessionId,
  activeSession,
  handleSessionChange,
  editingNameVal,
  setEditingNameVal,
  handleRenameSave,
  handleRenameKeyDown,
  startEditing,
  deleteSession,
  handleAskedClick
}) => {
  return (
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
  );
};
