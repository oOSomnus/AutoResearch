"""
PDF Reader Module - Handles PDF content extraction and URL downloads.
"""
import os
import re
from pathlib import Path
from typing import Optional, List

import requests
import PyPDF2


def is_url(path: str) -> bool:
    """Check if the given path is a URL."""
    return path.startswith(('http://', 'https://'))


def download_pdf_from_url(url: str, save_path: str) -> str:
    """
    Download a PDF from a URL and save it locally.

    Args:
        url: The URL of the PDF file
        save_path: Local path to save the downloaded file

    Returns:
        The actual path where the file was saved

    Raises:
        requests.RequestException: If download fails
    """
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return save_path


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text content

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        PyPDF2.PdfReadError: If the file is not a valid PDF
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text_content = []

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)

    full_text = '\n\n'.join(text_content)

    # Clean up extra whitespace
    full_text = re.sub(r'\s+', ' ', full_text).strip()

    return full_text


def _extract_title_with_llm(first_page_text: str) -> Optional[str]:
    """
    Extract title using LLM-based analysis.

    Args:
        first_page_text: Text content from the first page

    Returns:
        Extracted title or None if LLM extraction fails
    """
    try:
        from langchain_openai import ChatOpenAI
        from dotenv import load_dotenv
        load_dotenv()

        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("MODEL_NAME", "gpt-4")

        if not api_key:
            return None

        llm = ChatOpenAI(
            openai_api_base=api_base,
            openai_api_key=api_key,
            model=model_name,
            temperature=0.1
        )

        # Prepare prompt for title extraction
        prompt = f"""Extract the paper title from the following first page content.

Content (first 3000 chars):
{first_page_text[:3000]}

Requirements:
1. Carefully identify the title, which is typically at the top center or left of the page
2. The title is usually more prominent (though we can't see formatting, use position as a clue)
3. Exclude author names, affiliations, "Abstract", "Introduction", and other non-title content
4. If multiple lines appear to be the title, extract the complete title
5. If you cannot determine the title, return an empty string

Output ONLY the title text, nothing else."""

        response = llm.invoke(prompt)
        title = str(response.content).strip()

        # Validate the extracted title
        if title and len(title) > 3 and len(title) < 300:
            # Filter out common false positives
            title_lower = title.lower()
            skip_terms = ['abstract', 'introduction', 'acknowledgment', 'references', 'appendix']
            if not any(term in title_lower for term in skip_terms):
                return title

        return None
    except Exception:
        return None


def _is_likely_author_name(text: str) -> bool:
    """
    Check if the text looks like an author name.

    Args:
        text: Text to check

    Returns:
        True if likely an author name
    """
    # Common patterns for author names
    # Single word with first letter capitalized (e.g., "Smith")
    if re.match(r'^[A-Z][a-z]+$', text.strip()):
        return True

    # Pattern like "John Smith" or "Smith, John"
    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', text.strip()):
        return True

    # Pattern like "J. Smith" or "Smith, J."
    if re.match(r'^[A-Z]\. [A-Z][a-z]+$|^[A-Z][a-z]+, [A-Z]\.$', text.strip()):
        return True

    # Contains typical name separators
    if re.search(r',\s*[A-Z]\.|,\s*[A-Z][a-z]+\sand\s+[A-Z]', text):
        return True

    return False


def _is_common_false_positive(line: str) -> bool:
    """
    Check if a line is a common false positive for title.

    Args:
        line: Line to check

    Returns:
        True if likely a false positive
    """
    line_lower = line.lower().strip()

    # Skip section headers
    section_terms = ['abstract', 'introduction', 'background', 'conclusion',
                    'references', 'acknowledgments', 'appendix', 'keywords',
                    'keywords:', 'index terms']
    if any(term in line_lower for term in section_terms):
        return True

    # Skip lines with URLs or emails
    if re.search(r'https?://|www\.|\.edu|\.com|@', line_lower):
        return True

    # Skip lines with university names or affiliations
    affiliation_terms = ['university', 'college', 'institute', 'laboratory',
                        'department', 'school of', 'research lab']
    if any(term in line_lower for term in affiliation_terms):
        return True

    # Skip lines with conference/journal info
    if re.search(r'proceedings|conference|symposium|transactions|journal', line_lower):
        return True

    # Skip lines with dates
    if re.search(r'\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec', line_lower, re.IGNORECASE):
        return True

    # Skip very short or very long lines
    if len(line.strip()) < 5 or len(line.strip()) > 200:
        return True

    # Skip lines that look like author names
    if _is_likely_author_name(line):
        return True

    # Skip lines with numbers (likely figure captions or table headers)
    if re.search(r'^\d+\s+|^fig\.|table\s+\d+|figure\s+\d+', line_lower):
        return True

    return False


def extract_title(pdf_path: str) -> Optional[str]:
    """
    Attempt to extract the paper title from the PDF.

    Uses a multi-stage approach:
    1. LLM-based extraction (most accurate)
    2. Metadata extraction (fallback)
    3. Heuristic extraction from first page (fallback)

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted title or None if not found
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            # Get first page content for LLM extraction and heuristics
            if len(reader.pages) > 0:
                first_page_text = reader.pages[0].extract_text()
                if first_page_text:
                    # Try LLM-based extraction first
                    llm_title = _extract_title_with_llm(first_page_text)
                    if llm_title:
                        return llm_title

                    # Fallback to heuristic extraction
                    lines = first_page_text.split('\n')

                    # Analyze lines with improved heuristics
                    candidates = []
                    for i, line in enumerate(lines[:10]):  # Check first 10 lines
                        line = line.strip()

                        # Skip empty lines and obvious false positives
                        if not line or _is_common_false_positive(line):
                            continue

                        # Score the line as a potential title
                        score = 0

                        # Longer titles are more likely (but not too long)
                        if 20 <= len(line) <= 150:
                            score += 2

                        # Title often has capitalized words (not all caps)
                        words = line.split()
                        if words:
                            capitalized = sum(1 for w in words if w[0].isupper())
                            ratio = capitalized / len(words)
                            if 0.3 <= ratio <= 0.9:  # Mixed case, not all caps or all lower
                                score += 1

                        # Avoid lines with numbers (figure captions)
                        if not re.search(r'\d', line):
                            score += 1

                        # Avoid lines with common separators (likely author lists)
                        if not re.search(r',\s*[A-Z]\.|\sand\s', line):
                            score += 1

                        # Position: earlier is better
                        score += (10 - i) * 0.5

                        if score > 0:
                            candidates.append((score, line))

                    # Return the highest-scoring candidate
                    if candidates:
                        candidates.sort(key=lambda x: x[0], reverse=True)
                        return candidates[0][1]

            # Try to get title from metadata as final fallback
            if reader.metadata:
                title = reader.metadata.get('/Title')
                if title and title.strip():
                    title = title.strip()
                    # Validate metadata title
                    if not _is_common_false_positive(title):
                        return title

    except Exception:
        pass

    return None


def get_pdf_path(source: str, work_dir: str = ".") -> str:
    """
    Get the actual PDF file path, downloading from URL if necessary.

    Args:
        source: Either a local file path or a URL
        work_dir: Working directory for saving downloaded files

    Returns:
        The actual local path to the PDF file
    """
    if is_url(source):
        # Generate a filename from URL
        filename = source.split('/')[-1]
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        # Use MD5 hash of URL as filename if no good name
        if len(filename) > 50:
            import hashlib
            filename = hashlib.md5(source.encode()).hexdigest() + '.pdf'

        save_path = os.path.join(work_dir, filename)
        return download_pdf_from_url(source, save_path)

    # Local file path - convert to absolute path
    path = Path(source)
    if not path.is_absolute():
        path = Path(work_dir) / source

    return str(path.resolve())