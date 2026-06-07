# Sample Q&A

The following queries showcase the assistant's ability to answer factual questions, handle out-of-scope/advisory questions, and enforce PII constraints.

### Q1: Exact Factual Retrieval
**User:** What is the expense ratio for ICICI Prudential Small Cap Fund?
**Assistant:** The expense ratio for the ICICI Prudential Small Cap Fund is 0.72%.
**Citation:** [ICICI Prudential Small Cap Fund](https://www.indmoney.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth-3588)

### Q2: Multi-Fund Context (UI Checkbox feature)
*(User selects "ICICI Prudential Flexi Cap Fund" and "ICICI Prudential Focused Equity Fund" from the UI sidebar)*
**User:** What are the minimum investment amounts?
**Assistant:** The minimum investment amount for both the ICICI Prudential Flexi Cap Fund and the ICICI Prudential Focused Equity Fund is ₹100 for SIP and ₹100 for lumpsum investments.
**Citation:** [ICICI Prudential Flexi Cap Fund](https://www.indmoney.com/mutual-funds/icici-prudential-flexicap-fund-direct-growth-1006609)

### Q3: Aggregation / All Funds Query
**User:** What is the AUM for all ICICI Prudential funds?
**Assistant:** The AUM for the requested ICICI Prudential mutual funds is as follows: Small Cap Fund (₹8880 Cr), Large & Mid Cap Fund (₹15317 Cr), Flexi Cap Fund (₹15779 Cr), Focused Equity Fund (₹9564 Cr), Mid Cap Fund (₹6457 Cr), Multi Cap Fund (₹12686 Cr), Large Cap Fund (₹56976 Cr), ELSS Tax Saver Fund (₹14502 Cr), Equity Savings Fund (₹11311 Cr), Equity & Debt Fund (₹36636 Cr), Regular Savings Fund (₹3193 Cr), Multi Asset Fund (₹43834 Cr), Nifty 50 Index Fund (₹8393 Cr), Gold ETF Fund of Fund (₹560 Cr), and Silver ETF Fund of Fund (₹219 Cr).

### Q4: Refusal (Financial Advice)
**User:** Should I invest in the Small Cap Fund or the Large Cap Fund?
**Assistant:** I cannot provide financial advice, recommendations, or predictive analyses. Please consult a registered financial advisor for personalized investment guidance.

### Q5: Refusal (PII / Account Management)
**User:** Can you check my portfolio balance? My PAN number is ABCDE1234F.
**Assistant:** For your privacy and security, I cannot process queries containing sensitive personal information (like PAN, Aadhaar, or bank details) or access personal portfolio data.

### Q6: Refusal (Off-Topic / Out of Scope)
**User:** Who won the cricket match yesterday?
**Assistant:** I am a specialized assistant designed to answer factual questions about specific ICICI Prudential Mutual Fund schemes. I cannot help with general off-topic inquiries. Please ask about metrics like NAV, exit load, expense ratio, or fund managers.
