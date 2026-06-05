import { Folder, ChevronDown, ChevronRight } from 'lucide-react';

export const SidebarLeft = ({
  isLeftOpen,
  toggleCategory,
  expandedCategories,
  checkboxes,
  handleCheckboxChange,
  activeSelectedKeys
}) => {
  return (
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
  );
};
