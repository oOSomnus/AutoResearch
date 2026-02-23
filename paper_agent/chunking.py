"""
Chapter Chunking - Extract and organize paper content by sections.
"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

import PyPDF2


@dataclass
class Chapter:
    """Represents a single chapter/section of a paper."""
    title: str
    content: str
    page_range: tuple = None  # (start_page, end_page)
    chapter_type: Optional[str] = None  # 'introduction', 'method', 'results', 'conclusion', etc.


# Common section heading patterns across different formatting styles
SECTION_PATTERNS = [
    # Numeric sections: 1. Introduction, 2. Related Work
    r'(?m)^(?:\s*)(\d+(?:\.\d+)*)\.\s+(.+?)(?:\n|$)',
    # Roman numeral: I. Introduction, II. Background
    r'(?m)^(?:\s*)([IVXLCDM]+)\.\s+(.+?)(?:\n|$)',
    # Capitalized section headers
    r'(?m)^(?:\s*)([A-Z][A-Z\s]{5,})(?:\n|$)',
    # Numbered with parentheses: (1) Introduction, (2) Methodology
    r'(?m)^(?:\s*)\((\d+)\)\s+(.+?)(?:\n|$)',
    # Common academic section names
    r'(?m)^(?:\s*)(Abstract|Introduction|Background|Related\s+Work|Methodology|Method|Methods|Experiments|Results|Discussion|Conclusion|Future\s+Work|References|Acknowledgments)(?:\s*)$',
]

# Mapping of section keywords to chapter types
SECTION_TYPE_MAP = {
    'introduction': 'introduction',
    'intro': 'introduction',
    'background': 'background',
    'related work': 'related_work',
    'related works': 'related_work',
    'literature review': 'related_work',
    'methodology': 'methodology',
    'method': 'methodology',
    'methods': 'methodology',
    'approach': 'methodology',
    'approaches': 'methodology',
    'experiments': 'experiments',
    'experiment': 'experiments',
    'evaluation': 'experiments',
    'results': 'results',
    'result': 'results',
    'discussion': 'discussion',
    'conclusion': 'conclusion',
    'conclusions': 'conclusion',
    'future work': 'future_work',
    'future': 'future_work',
    'limitations': 'limitations',
    'limitations and future work': 'conclusion',
}


def _extract_full_text(pdf_path: str) -> str:
    """Extract full text from PDF with page boundaries marked."""
    if not pdf_path:
        return ""

    text_content = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    # Mark page boundaries for tracking
                    text_content.append(f"===PAGE_{page_num}===\n{page_text}")
    except Exception as e:
        print(f"Warning: Failed to extract PDF text: {e}")
        return ""

    return '\n\n'.join(text_content)


def _detect_section_boundaries(full_text: str) -> List[tuple]:
    """Detect section boundaries using multiple patterns."""
    boundaries = []

    for pattern in SECTION_PATTERNS:
        matches = list(re.finditer(pattern, full_text, re.MULTILINE | re.IGNORECASE))
        for match in matches:
            start_pos = match.start()
            title = match.group(1) if match.lastindex >= 1 else match.group(0)
            title = title.strip()

            # Clean up the title
            title = re.sub(r'===PAGE_\d+===', '', title).strip()
            title = re.sub(r'\s+', ' ', title)

            # Filter out false positives (very short or unlikely section headers)
            if len(title) < 2 or len(title) > 200:
                continue

            boundaries.append((start_pos, title))

    # Remove duplicates (same position, similar titles) and sort
    unique_boundaries = {}
    for pos, title in boundaries:
        key = pos
        if key not in unique_boundaries or len(title) > len(unique_boundaries[key]):
            unique_boundaries[key] = title

    boundaries = [(pos, title) for pos, title in sorted(unique_boundaries.items())]
    return boundaries


def _get_chapter_type(title: str) -> Optional[str]:
    """Determine the type of a chapter based on its title."""
    title_lower = title.lower().strip()

    for keyword, chapter_type in SECTION_TYPE_MAP.items():
        if keyword in title_lower:
            return chapter_type

    return None


def extract_chapters(pdf_path: str) -> List[Chapter]:
    """
    Extract chapters from PDF using section heading detection.

    Returns:
        List of Chapter objects ordered by appearance
    """
    if not pdf_path:
        return []

    full_text = _extract_full_text(pdf_path)

    if not full_text:
        return []

    boundaries = _detect_section_boundaries(full_text)

    if not boundaries:
        # No sections detected - return entire content as one chapter
        content = re.sub(r'===PAGE_\d+===\n', '', full_text)
        content = re.sub(r'\s+', ' ', content).strip()
        return [Chapter(title="Full Content", content=content)]

    chapters = []

    # Create chapters from boundaries
    for i in range(len(boundaries)):
        start_pos, title = boundaries[i]

        # Determine end position (start of next chapter or end of text)
        if i + 1 < len(boundaries):
            end_pos = boundaries[i + 1][0]
        else:
            end_pos = len(full_text)

        # Extract chapter content
        chapter_text = full_text[start_pos:end_pos]

        # Clean up the content
        chapter_text = re.sub(r'===PAGE_\d+===\n', '', chapter_text)
        chapter_text = re.sub(r'\s+', ' ', chapter_text).strip()

        # Remove the title from content (first line/phrase)
        title_normalized = re.sub(r'\s+', ' ', title).strip()
        if chapter_text.startswith(title_normalized):
            chapter_text = chapter_text[len(title_normalized):].strip()

        if not chapter_text:
            continue

        # Get chapter type
        chapter_type = _get_chapter_type(title)

        # Extract page range if possible
        page_match = re.findall(r'===PAGE_(\d+)===', full_text[start_pos:end_pos])
        page_range = None
        if page_match:
            page_range = (int(page_match[0]), int(page_match[-1]))

        chapters.append(Chapter(
            title=title_normalized,
            content=chapter_text,
            page_range=page_range,
            chapter_type=chapter_type
        ))

    return chapters


def get_chapter_for_analysis(chapters: List[Chapter], chapter_type: str) -> str:
    """
    Get content for a specific chapter type.

    Args:
        chapters: List of Chapter objects
        chapter_type: 'introduction', 'methodology', 'experiments', 'results', 'conclusion', etc.

    Returns:
        Combined content of all chapters matching the type
    """
    matching_chapters = [c for c in chapters if c.chapter_type == chapter_type]

    if not matching_chapters:
        return ""

    return '\n\n'.join([c.content for c in matching_chapters])


def get_chapters_by_keyword(chapters: List[Chapter], keywords: List[str]) -> List[Chapter]:
    """
    Get chapters that match any of the given keywords (case-insensitive).

    Args:
        chapters: List of Chapter objects
        keywords: List of keywords to match

    Returns:
        List of matching Chapter objects
    """
    matching = []
    keywords_lower = [k.lower() for k in keywords]

    for chapter in chapters:
        title_lower = chapter.title.lower()
        if any(keyword in title_lower for keyword in keywords_lower):
            matching.append(chapter)

    return matching


def get_relevant_content_for_analysis(chapters: List[Chapter], analysis_type: str) -> str:
    """
    Get relevant content for a specific analysis type.

    This combines content from multiple related chapters.

    Args:
        chapters: List of Chapter objects
        analysis_type: 'background', 'innovation', 'methodology', 'results', 'related_work', 'limitations'

    Returns:
        Combined relevant content
    """
    if analysis_type == 'background':
        # Introduction and background chapters
        keywords = ['introduction', 'intro', 'background', 'motivation', 'problem']
        relevant = get_chapters_by_keyword(chapters, keywords)

    elif analysis_type == 'innovation':
        # Introduction and methodology chapters (for understanding the approach)
        keywords = ['introduction', 'intro', 'approach', 'methodology', 'method', 'proposed', 'our method', 'contribution']
        relevant = get_chapters_by_keyword(chapters, keywords)

    elif analysis_type == 'methodology':
        # Methodology and methods chapters
        keywords = ['methodology', 'method', 'methods', 'approach', 'approaches', 'model', 'architecture', 'algorithm']
        relevant = get_chapters_by_keyword(chapters, keywords)

    elif analysis_type == 'results':
        # Results, experiments, evaluation chapters
        keywords = ['results', 'result', 'experiments', 'experiment', 'evaluation', 'performance']
        relevant = get_chapters_by_keyword(chapters, keywords)

    elif analysis_type == 'related_work':
        # Related work and literature review chapters
        keywords = ['related work', 'related works', 'literature review', 'background', 'prior work']
        relevant = get_chapters_by_keyword(chapters, keywords)

    elif analysis_type == 'limitations':
        # Conclusion and discussion chapters
        keywords = ['conclusion', 'conclusions', 'discussion', 'future work', 'limitations', 'future']
        relevant = get_chapters_by_keyword(chapters, keywords)

    else:
        # Default: return all content
        relevant = chapters

    if not relevant:
        # Fallback: return all content if no specific chapters found
        return '\n\n'.join([c.content for c in chapters])

    # Limit total content length to avoid token limits
    combined = '\n\n'.join([c.content for c in relevant])
    max_chars = 50000  # Increased limit for long papers
    if len(combined) > max_chars:
        combined = combined[:max_chars]

    return combined