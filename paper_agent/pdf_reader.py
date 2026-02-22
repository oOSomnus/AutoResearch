"""
PDF Reader Module - Handles PDF content extraction and URL downloads.
"""
import os
import re
from pathlib import Path
from typing import Optional

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


def extract_title(pdf_path: str) -> Optional[str]:
    """
    Attempt to extract the paper title from the PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted title or None if not found
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            # Try to get title from metadata
            if reader.metadata:
                title = reader.metadata.get('/Title')
                if title and title.strip():
                    return title.strip()

            # Fall back to first few lines of first page
            if len(reader.pages) > 0:
                first_page_text = reader.pages[0].extract_text()
                if first_page_text:
                    lines = first_page_text.split('\n')
                    for line in lines[:5]:  # Check first 5 lines
                        line = line.strip()
                        # Heuristic: title is often first non-empty line
                        # and is reasonably short
                        if line and len(line) < 200 and not line.lower().startswith(('abstract', 'introduction')):
                            return line

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