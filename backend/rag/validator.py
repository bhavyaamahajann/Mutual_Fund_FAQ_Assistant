import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Find all HTTP/HTTPS URLs
URL_PATTERN = re.compile(r'https?://[^\s()<>]+(?:\([\w\d]+\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’])')

class ResponseValidator:
    def split_sentences(self, text: str) -> list[str]:
        """
        Splits text into sentences, ignoring decimal points in numbers.
        """
        # Split on periods not surrounded by digits, or question/exclamation marks
        raw_sentences = re.split(r'(?<!\d)\.(?!\d)|[!?]', text)
        sentences = []
        for s in raw_sentences:
            s_clean = s.strip()
            if s_clean:
                # Re-add period if it was a period in original text
                sentences.append(s_clean)
        return sentences

    def validate_and_fix(self, answer: str, source_url: str, last_scraped: str) -> dict:
        """
        Validates the LLM answer and applies auto-correct fixes if rules are violated:
        1. Limits sentence count to max 3 sentences (excluding markdown tables).
        2. Ensures exactly 1 source URL citation is present.
        3. Appends the mandatory "Last updated from sources:" footer.
        
        Returns: {
            "answer": str (the verified & corrected answer),
            "citations_fixed": bool,
            "truncated": bool,
            "footer_added": bool
        }
        """
        fixed_answer = answer.strip()
        truncated = False
        citations_fixed = False
        footer_added = False

        # --- Rule 1: Footer & Source Check & Remove ---
        # First, if the LLM already output a footer like "Last updated from sources:",
        # or "Source:", remove it temporarily to count sentences and validate properly.
        # We will reconstruct it at the end.
        footer_regex = re.compile(r'Last updated from sources:.*$', re.IGNORECASE)
        if footer_regex.search(fixed_answer):
            fixed_answer = footer_regex.sub('', fixed_answer).strip()

        source_regex = re.compile(r'Source:.*$', re.IGNORECASE)
        if source_regex.search(fixed_answer):
            fixed_answer = source_regex.sub('', fixed_answer).strip()

        # --- Rule 2: Extract & Temporarily Strip URLs ---
        # We strip URLs from the text during sentence counting to prevent periods in URLs (like 'www.indmoney.com')
        # from being parsed as sentence boundaries and formatted with spaces.
        urls = URL_PATTERN.findall(fixed_answer)
        text_without_urls = fixed_answer
        for url in urls:
            text_without_urls = text_without_urls.replace(url, "")
        
        # Clean up any trailing space or double spaces on each line, keeping newlines
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text_without_urls.split('\n')]
        text_without_urls = "\n".join(lines)

        # --- Rule 3: Sentence Count check (max 3 sentences) excluding tables ---
        # Strip markdown table lines before counting
        lines = text_without_urls.split('\n')
        lines_no_table = [line for line in lines if not line.strip().startswith('|')]
        text_for_sentence_count = " ".join(lines_no_table)
        text_for_sentence_count = re.sub(r'\s+', ' ', text_for_sentence_count).strip()

        sentences = self.split_sentences(text_for_sentence_count)
        
        if len(sentences) > 3:
            logger.warning(f"Response exceeded sentence count ({len(sentences)}). Truncating.")
            # Join the first 3 sentences
            # Since we are truncating, we truncate the original text_without_urls by sentence mapping,
            # or simply truncate the text_for_sentence_count.
            # To be simple and robust:
            truncated_text = ". ".join(sentences[:3]) + "."
            # If there was a table, we keep the table in the final output and just truncate the text part.
            # Usually LLM generated answers have text first, then table, or just table.
            # If there's a table, we keep table lines in text_without_urls, but truncate sentences.
            # Let's map sentences back or just replace the text part.
            # A simple way to do it: if we truncated, we can rebuild the text using table lines + truncated text.
            table_lines = [line for line in fixed_answer.split('\n') if line.strip().startswith('|')]
            if table_lines:
                # Keep table lines and append the truncated text
                fixed_answer = truncated_text + "\n\n" + "\n".join(table_lines)
            else:
                fixed_answer = truncated_text
            truncated = True
        else:
            # If not truncated, we can keep the original fixed_answer (without URLs)
            # but wait, we stripped URLs from it so we must re-append the URL.
            # Let's use text_without_urls as the base.
            fixed_answer = text_without_urls

        # --- Rule 4: Reconstruct with Single Citation URL ---
        if urls:
            citation_url = urls[0]
        else:
            citation_url = source_url
            citations_fixed = True
            
        fixed_answer = f"{fixed_answer.strip()}\n\nSource: {citation_url}"
        
        if not urls or len(urls) > 1:
            citations_fixed = True

        # --- Rule 5: Append Mandatory Footer ---
        friendly_date = "Not available"
        if last_scraped and last_scraped != "Not available":
            try:
                # Try parsing ISO timestamp (e.g. 2026-06-04T17:24:02.430604)
                dt = datetime.fromisoformat(last_scraped)
                friendly_date = dt.strftime("%d %b %Y")
            except Exception:
                # Try other parsing formats
                for fmt in ("%d %b %Y", "%Y-%m-%d"):
                    try:
                        dt = datetime.strptime(last_scraped[:10], fmt)
                        friendly_date = dt.strftime("%d %b %Y")
                        break
                    except Exception:
                        continue
                else:
                    friendly_date = last_scraped[:10]

        footer_text = f"\n\nLast updated from sources: {friendly_date}"
        fixed_answer = f"{fixed_answer.strip()}{footer_text}"
        footer_added = True

        return {
            "answer": fixed_answer,
            "citations_fixed": citations_fixed,
            "truncated": truncated,
            "footer_added": footer_added
        }


