from bs4 import BeautifulSoup
import re
import logging
import json

logger = logging.getLogger(__name__)

class HtmlParser:
    def __init__(self):
        # Elements to completely remove from the HTML before extracting text
        self.tags_to_remove = [
            "script", "style", "nav", "footer", "header", "aside",
            "noscript", "iframe", "svg", "button", "form"
        ]

    def _clean_html(self, html: str) -> str:
        """Removes unwanted tags and extracts clean text."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove unwanted tags completely
        for tag in soup(self.tags_to_remove):
            tag.decompose()
            
        # Get text with space separator and strip whitespace
        text = soup.get_text(separator=" ", strip=True)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text

    def _extract_metadata(self, html: str, base_metadata: dict) -> dict:
        """
        Extracts key metadata from Next.js preloaded data (__NEXT_DATA__)
        with a fallback to standard regex-based extraction.
        """
        metadata = base_metadata.copy()
        soup = BeautifulSoup(html, "html.parser")
        
        # Initialize default values for the requested fields
        metadata["fund_name"] = base_metadata.get("fund_name", "Not available")
        metadata["fund_category"] = base_metadata.get("fund_category", "Not available")
        metadata["fund_plan"] = base_metadata.get("fund_plan", "Not available")
        metadata["nav"] = "Not available"
        metadata["nav_date"] = "Not available"
        metadata["expense_ratio"] = "Not available"
        metadata["exit_load"] = "Not available"
        metadata["min_sip"] = "Not available"
        metadata["min_lumpsum"] = "Not available"
        metadata["benchmark_index"] = "Not available"
        metadata["riskometer"] = "Not available"
        metadata["lock_in"] = "Not available"
        metadata["fund_managers"] = []
        metadata["aum"] = "Not available"
        metadata["fund_house"] = "Not available"
        
        # 1. Attempt to parse from Next.js preloaded props (best & most reliable source)
        next_data_script = soup.find("script", id="__NEXT_DATA__")
        if next_data_script:
            try:
                next_data = json.loads(next_data_script.string)
                fund_data = next_data.get("props", {}).get("pageProps", {}).get("mutualFundsDetailData", {}).get("data", {})
                if fund_data:
                    # Fund Name
                    if fund_data.get("name"):
                        metadata["fund_name"] = fund_data.get("name")
                    
                    # NAV
                    metadata["nav"] = fund_data.get("nav", "Not available")
                    metadata["nav_date"] = fund_data.get("nav_date", "Not available")
                    
                    # Info List (Expense Ratio, Exit Load, AUM, Lock-in, Benchmark, Min Lumpsum/SIP)
                    info_list = fund_data.get("fund_overview", {}).get("info", [])
                    info_dict = {item.get("name", "").lower(): item.get("value") for item in info_list}
                    
                    metadata["expense_ratio"] = info_dict.get("expense ratio", "Not available")
                    metadata["exit_load"] = info_dict.get("exit load", "Not available")
                    metadata["aum"] = info_dict.get("aum", "Not available")
                    metadata["lock_in"] = info_dict.get("lock in", "Not available")
                    metadata["benchmark_index"] = info_dict.get("benchmark", "Not available")
                    
                    min_lump_sip = info_dict.get("min lumpsum/sip")
                    if min_lump_sip:
                        parts = min_lump_sip.split('/')
                        metadata["min_lumpsum"] = parts[0].strip() if len(parts) > 0 else "Not available"
                        metadata["min_sip"] = parts[1].strip() if len(parts) > 1 else "Not available"
                    
                    # Riskometer
                    metadata["riskometer"] = fund_data.get("risk_meter", {}).get("widget_properties", {}).get("zone_title", "Not available")
                    
                    # Fund Managers
                    managers_info = fund_data.get("about", {}).get("managers", {}).get("widget_properties", {}).get("card_data", {}).get("managers_info", [])
                    metadata["fund_managers"] = [m.get("title") for m in managers_info if m.get("title")]
                    
                    # Fund House
                    amc_name = fund_data.get("about", {}).get("amc", {}).get("display_name", "")
                    if amc_name.startswith("Learn more about "):
                        amc_name = amc_name[len("Learn more about "):]
                    metadata["fund_house"] = amc_name if amc_name else "Not available"
                    
                    return metadata
            except Exception as e:
                logger.warning(f"Failed to parse __NEXT_DATA__ for metadata: {e}")

        # 2. Fallback regex extraction on raw text for specific fields (if NEXT_DATA fails)
        clean_text = self._clean_html(html)
        
        # NAV
        nav_match = re.search(r'NAV.*?₹?\s*([\d\.]+)', clean_text, re.IGNORECASE)
        metadata["nav"] = nav_match.group(1) if nav_match else "Not available"
        
        # Expense Ratio
        er_match = re.search(r'Expense Ratio.*?([\d\.]+%)', clean_text, re.IGNORECASE)
        metadata["expense_ratio"] = er_match.group(1) if er_match else "Not available"
        
        # Fund Manager
        fm_match = re.search(r'Fund Manager.*?(?:is|:)\s*([A-Za-z\s]+?)(?:\.|,)', clean_text, re.IGNORECASE)
        if fm_match:
            metadata["fund_managers"] = [fm_match.group(1).strip()]
        
        # Exit Load
        exit_match = re.search(r'Exit Load.*?(?:is|:)?\s*(\d.*?%)', clean_text, re.IGNORECASE)
        metadata["exit_load"] = exit_match.group(1).strip() if exit_match else "Not available"

        return metadata

    def parse(self, html: str, url: str, base_metadata: dict) -> tuple[str, dict]:
        """
        Parses raw HTML, returning cleaned text (with structured summary header) and extracted metadata.
        """
        if not html:
            return "", base_metadata
            
        metadata = self._extract_metadata(html, base_metadata)
        metadata["source_url"] = url
        
        # Build clean structured summary header for text chunking
        managers_str = ", ".join(metadata["fund_managers"]) if isinstance(metadata["fund_managers"], list) else str(metadata["fund_managers"])
        summary_header = (
            f"Mutual Fund Name: {metadata.get('fund_name')}\n"
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
            f"Source URL: {url}\n\n"
        )
        
        clean_body = self._clean_html(html)
        
        return clean_body, metadata


