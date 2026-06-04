from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""]
        )

    def chunk_document(self, body_text: str, metadata: dict) -> list[dict]:
        """
        Splits text into overlapping chunks, prepends fund context to each chunk,
        and creates a dedicated factsheet chunk at index 0.
        """
        chunked_data = []
        
        # 1. Create Factsheet Chunk at Index 0 containing all 13 metrics
        managers_str = ", ".join(metadata.get("fund_managers", [])) if isinstance(metadata.get("fund_managers"), list) else str(metadata.get("fund_managers", "Not available"))
        factsheet_text = (
            f"Mutual Fund Factsheet\n"
            f"Name: {metadata.get('fund_name')}\n"
            f"Category: {metadata.get('fund_category')}\n"
            f"Plan Type: {metadata.get('fund_plan')}\n"
            f"NAV: {metadata.get('nav')} (as of {metadata.get('nav_date')})\n"
            f"Expense Ratio: {metadata.get('expense_ratio')}\n"
            f"Exit Load: {metadata.get('exit_load')}\n"
            f"Minimum Lumpsum Investment: {metadata.get('min_lumpsum')}\n"
            f"Minimum SIP Investment: {metadata.get('min_sip')}\n"
            f"Benchmark Index: {metadata.get('benchmark_index')}\n"
            f"Riskometer: {metadata.get('riskometer')}\n"
            f"Lock-in Period: {metadata.get('lock_in')}\n"
            f"Fund Managers: {managers_str}\n"
            f"AUM (Assets Under Management): {metadata.get('aum')}\n"
            f"Fund House: {metadata.get('fund_house')}\n"
            f"Source URL: {metadata.get('source_url')}"
        )
        
        meta_0 = metadata.copy()
        meta_0["chunk_index"] = 0
        chunked_data.append({
            "text": factsheet_text.strip(),
            "metadata": meta_0
        })
        
        # 2. Chunk the body text and prepend context to each chunk
        if body_text and body_text.strip():
            body_chunks = self.splitter.split_text(body_text)
            for i, chunk in enumerate(body_chunks):
                if chunk.strip():
                    # Prepend context to avoid losing fund details across boundaries
                    context_prefix = f"Fund: {metadata.get('fund_name')} ({metadata.get('fund_plan')})\n\n"
                    chunk_text = context_prefix + chunk.strip()
                    
                    meta_i = metadata.copy()
                    meta_i["chunk_index"] = i + 1
                    chunked_data.append({
                        "text": chunk_text,
                        "metadata": meta_i
                    })
                    
        return chunked_data

