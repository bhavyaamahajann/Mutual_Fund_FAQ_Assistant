import { 
  AlertTriangle, 
  ShieldAlert, 
  ExternalLink, 
  Folder, 
  X, 
  Send, 
  Clock 
} from 'lucide-react';
import { renderMessageText, cleanMessageText } from './MessageRenderers';

export const ChatArea = ({
  chatPaneRef,
  activeSession,
  activeMessages,
  dynamicSuggestiveQuestions,
  sendQuery,
  isLoading,
  handleFormSubmit,
  activeSelectedKeys,
  handleCheckboxChange,
  inputVal,
  setInputVal,
  setIsArchModalOpen,
  setIsPrivacyOpen
}) => {
  return (
    <main className="center-panel">
      <div className="center-header">
        <div className="compliance-warning-badge">
          <AlertTriangle className="warning-badge-icon" />
          <span>Facts-Only. No Investment Advice.</span>
        </div>
      </div>

      <section className="chat-pane" ref={chatPaneRef} id="chat-pane">
        {(!activeSession || activeMessages.length === 0) ? (
          <div className="welcome-container" id="welcome-container">
            <div className="welcome-heading-group">
              <h1 className="welcome-title">How can I help you today<span className="blinking-question">?</span></h1>
              <p className="welcome-subtitle">Ask me anything about ICICI Prudential funds, expense ratios, tax implications, or performance data.</p>
            </div>

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
          <div className="messages-container" id="messages-container">
            {activeMessages.map((msg, index) => {
              const isUser = msg.sender === 'user';
              return (
                <div key={index} className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
                  {msg.status === 'refused' ? (
                    <div className={`refusal-panel ${msg.type === 'pii' ? 'error' : 'warning'}`}>
                      <div className="refusal-icon-container">
                        {msg.type === 'pii' ? <ShieldAlert /> : <AlertTriangle />}
                      </div>
                      <div className="refusal-content">
                        <h4 className="refusal-title">
                          {msg.type === 'pii' ? 'PII Security Block' : 'Regulatory Notice'}
                        </h4>
                        <p className="refusal-text">{msg.answer}</p>
                        
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
                    <div className="message-bubble">
                      {isUser ? (
                        <p>{msg.text}</p>
                      ) : (
                        renderMessageText(cleanMessageText(msg.answer || msg.text))
                      )}
                      
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

        {isLoading && (
          <div className="typing-indicator" id="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
      </section>

      <footer className="center-footer">
        <form className="chat-form" onSubmit={handleFormSubmit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', marginBottom: '4px' }}>
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
  );
};
