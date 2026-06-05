import { 
  X, 
  DownloadCloud, 
  Binary, 
  Database, 
  Cpu, 
  CheckSquare,
  ShieldAlert,
  Info
} from 'lucide-react';

export const Modals = ({
  isArchModalOpen,
  setIsArchModalOpen,
  isPrivacyOpen,
  setIsPrivacyOpen
}) => {
  return (
    <>
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
    </>
  );
};
