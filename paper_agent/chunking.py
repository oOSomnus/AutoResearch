"""
Chapter Chunking - Extract and organize paper content by sections.
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

import PyPDF2


@dataclass
class Chapter:
    """Represents a single chapter/section of a paper."""
    title: str
    content: str
    page_range: tuple = None  # (start_page, end_page)
    chapter_type: Optional[str] = None  # 'introduction', 'method', 'results', 'conclusion', etc.


@dataclass
class FigureInfo:
    """Information about a figure or table extracted from the paper."""
    figure_type: str  # 'figure' or 'table'
    identifier: str  # e.g., "Figure 1", "Table 2"
    caption: str  # Full caption text
    page_num: int  # Page number where found
    description: str = ""  # Simplified description


# Common section heading patterns across different formatting styles
# These patterns balance specificity with flexibility
SECTION_PATTERNS = [
    # Numeric sections: 1. Introduction, 2. Related Work (most common)
    r'(?m)^(?:\s*)(\d+(?:\.\d+)*)\.\s+([A-Z][A-Za-z0-9\s&\-]{5,100}?)(?:\n|$)',
    # Roman numeral: I. Introduction, II. Background
    r'(?m)^(?:\s*)([IVXLCDM]+)\.\s+([A-Z][A-Za-z0-9\s&\-]{5,100}?)(?:\n|$)',
    # Numbered with parentheses: (1) Introduction, (2) Methodology
    r'(?m)^(?:\s*)\((\d+)\)\s+([A-Z][A-Za-z0-9\s&\-]{5,100}?)(?:\n|$)',
    # Common academic section names (specific match)
    r'(?m)^(?:\s*)(Abstract|Introduction|Background|Related\s+Work|Methodology|Method|Methods|Experiments|Results|Discussion|Conclusion|Future\s+Work|References|Acknowledgments|Appendix|Acknowledgement)(?:\s*)(?:\n|$)',
    # Pattern for sections with more flexibility (no dot, like "1 Introduction")
    r'(?m)^(?:\s*)(\d+)\s+([A-Z][A-Za-z0-9\s&\-]{5,80}?)(?:\n|$)',
]


# Patterns that indicate a line is NOT a section header
NON_SECTION_PATTERNS = [
    # URLs and emails
    r'https?://|www\.|\.edu|\.com|@',
    # Conference/journal info
    r'proceedings|conference|symposium|transactions|journal',
    # Dates
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+\d{4}|\b\d{4}\b',
    # University/affiliation terms (more specific to avoid false positives)
    r'University\s+of|College\s+of|Institute\s+for',
    # Figure/table captions
    r'^Fig\.?\s+\d+|^Figure\s+\d+|^Table\s+\d+',
    # Very short or very long (after filtering)
    r'.{1,3}|.{100,}',
    # Multiple author names pattern (more specific)
    r'^[A-Z][a-z]+,\s*[A-Z]\.,\s*[A-Z]\.',  # Three or more authors like "Smith, J., Johnson, B."
]


def _is_valid_section_header(title: str) -> bool:
    """
    Check if a candidate title is actually a valid section header.

    Args:
        title: Candidate section title

    Returns:
        True if valid section header
    """
    title = title.strip()

    # Length constraints (check before regex to avoid issues)
    if len(title) < 3 or len(title) > 100:
        return False

    # Check against non-section patterns (exclude length-based patterns here)
    non_section_patterns = [
        # URLs and emails
        r'https?://|www\.|\.edu|\.com|@',
        # Conference/journal info
        r'proceedings|conference|symposium|transactions|journal',
        # Dates
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+\d{4}|\b\d{4}\b',
        # University/affiliation terms (more specific)
        r'University\s+of|College\s+of|Institute\s+for',
        # Figure/table captions
        r'^Fig\.?\s+\d+|^Figure\s+\d+|^Table\s+\d+',
        # Multiple author names pattern (more specific)
        r'^[A-Z][a-z]+,\s*[A-Z]\.,\s*[A-Z]\.',  # Three or more authors
    ]

    for pattern in non_section_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            return False

    # Check for common false positive patterns
    # Skip lines that look like they have multiple authors (with comma and "and")
    if re.search(r',\s*[A-Z]\.\s+and|,\s*[A-Z]\.,\s*[A-Z]\.', title):
        return False

    # Skip lines with excessive punctuation (likely citations)
    if re.search(r'\[.*?\]|\(.*?\d{4}.*?\)', title):
        return False

    # Allow common single-word section names
    common_single_words = {'Abstract', 'Introduction', 'Conclusion', 'References', 'Background'}
    if len(title.split()) == 1 and title not in common_single_words and len(title) < 5:
        return False

    return True

# Mapping of section keywords to chapter types (expanded)
SECTION_TYPE_MAP = {
    'introduction': 'introduction',
    'intro': 'introduction',
    'background': 'background',
    'motivation': 'introduction',
    'problem statement': 'introduction',
    'related work': 'related_work',
    'related works': 'related_work',
    'literature review': 'related_work',
    'prior work': 'related_work',
    'methodology': 'methodology',
    'method': 'methodology',
    'methods': 'methodology',
    'approach': 'methodology',
    'approaches': 'methodology',
    'model': 'methodology',
    'architecture': 'methodology',
    'algorithm': 'methodology',
    'proposed method': 'methodology',
    'our method': 'methodology',
    'experiments': 'experiments',
    'experiment': 'experiments',
    'evaluation': 'experiments',
    'experimental setup': 'experiments',
    'results': 'results',
    'result': 'results',
    'discussion': 'discussion',
    'analysis': 'results',
    'conclusion': 'conclusion',
    'conclusions': 'conclusion',
    'future work': 'future_work',
    'future': 'future_work',
    'limitations': 'limitations',
    'limitations and future work': 'conclusion',
}


# Expanded keyword lists for analysis type matching
ANALYSIS_KEYWORDS = {
    'background': [
        'introduction', 'intro', 'background', 'motivation', 'problem',
        'problem statement', 'overview', 'preliminaries'
    ],
    'innovation': [
        'introduction', 'intro', 'approach', 'methodology', 'method',
        'proposed', 'our method', 'contribution', 'model', 'architecture',
        'framework', 'algorithm', 'system'
    ],
    'methodology': [
        'methodology', 'method', 'methods', 'approach', 'approaches',
        'model', 'architecture', 'algorithm', 'implementation',
        'technical details', 'system design', 'framework'
    ],
    'results': [
        'results', 'result', 'experiments', 'experiment', 'evaluation',
        'performance', 'discussion', 'analysis', 'findings',
        'experimental results', 'evaluation'
    ],
    'related_work': [
        'related work', 'related works', 'literature review', 'background',
        'prior work', 'previous work', 'existing methods'
    ],
    'limitations': [
        'conclusion', 'conclusions', 'discussion', 'future work',
        'limitations', 'future', 'concluding remarks'
    ],
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
    """Detect section boundaries using improved patterns."""
    boundaries = []

    for pattern in SECTION_PATTERNS:
        matches = list(re.finditer(pattern, full_text, re.MULTILINE | re.IGNORECASE))
        for match in matches:
            start_pos = match.start()
            # Extract title based on match groups
            if match.lastindex >= 2:
                title = match.group(2) if match.group(2) else match.group(1)
            elif match.lastindex >= 1:
                title = match.group(1)
            else:
                title = match.group(0)

            title = title.strip()

            # Clean up the title
            title = re.sub(r'===PAGE_\d+===', '', title).strip()
            title = re.sub(r'\s+', ' ', title)

            # Validate section header with stricter rules
            if not _is_valid_section_header(title):
                continue

            boundaries.append((start_pos, title))

    # Remove duplicates (same position, similar titles) and sort
    unique_boundaries = {}
    for pos, title in boundaries:
        key = pos
        # Keep the longest title at the same position (most detailed)
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
        # Check for exact match first
        if any(keyword == title_lower for keyword in keywords_lower):
            matching.append(chapter)
        # Then check for partial match
        elif any(keyword in title_lower for keyword in keywords_lower):
            matching.append(chapter)

    return matching


def extract_figures_from_content(content: str, page_num: int = 0) -> List[FigureInfo]:
    """
    Extract figure and table references from content.

    Args:
        content: Content to search for figures/tables
        page_num: Default page number (not used in this text-based extraction)

    Returns:
        List of FigureInfo objects
    """
    figures = []

    # Pattern for figure references
    figure_patterns = [
        r'(?:Fig\.?|Figure)\s+(\d+)[.:]\s*([^\n]+?)(?=\n|Figure|Table|\[|$)',
        r'(?:图)\s*(\d+)[.:]\s*([^\n]+?)(?=\n|图|表|$)',
    ]

    # Pattern for table references
    table_patterns = [
        r'(?:Table)\s+(\d+)[.:]\s*([^\n]+?)(?=\n|Figure|Table|\[|$)',
        r'(?:表)\s*(\d+)[.:]\s*([^\n]+?)(?=\n|图|表|$)',
    ]

    # Extract figures
    for pattern in figure_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            fig_id = match.group(1)
            caption = match.group(2).strip()
            if caption:
                figures.append(FigureInfo(
                    figure_type='figure',
                    identifier=f'Figure {fig_id}',
                    caption=caption,
                    page_num=page_num,
                    description=caption
                ))

    # Extract tables
    for pattern in table_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            table_id = match.group(1)
            caption = match.group(2).strip()
            if caption:
                figures.append(FigureInfo(
                    figure_type='table',
                    identifier=f'Table {table_id}',
                    caption=caption,
                    page_num=page_num,
                    description=caption
                ))

    return figures


def _score_chapter_relevance(chapter: Chapter, analysis_type: str) -> float:
    """
    Score a chapter's relevance for a specific analysis type.

    Args:
        chapter: Chapter to score
        analysis_type: Type of analysis

    Returns:
        Relevance score (0-1)
    """
    keywords = ANALYSIS_KEYWORDS.get(analysis_type, [])
    title_lower = chapter.title.lower()

    # Exact keyword match gets highest score
    for keyword in keywords:
        if keyword == title_lower:
            return 1.0

    # Partial keyword match gets moderate score
    for keyword in keywords:
        if keyword in title_lower:
            return 0.7

    # No match gets low score
    return 0.2


def get_relevant_content_for_analysis(
    chapters: List[Chapter],
    analysis_type: str,
    max_chars: int = 60000
) -> Tuple[str, List[FigureInfo]]:
    """
    Get relevant content for a specific analysis type with intelligent selection.

    This combines content from multiple related chapters using:
    1. Multi-stage matching (exact → partial → semantic proximity)
    2. Content quality assessment
    3. Smart truncation when exceeding token limits
    4. Figure/table extraction

    Args:
        chapters: List of Chapter objects
        analysis_type: 'background', 'innovation', 'methodology', 'results', 'related_work', 'limitations'
        max_chars: Maximum characters to include (default: 60000)

    Returns:
        Tuple of (combined relevant content, list of extracted figures)
    """
    # Get keywords for this analysis type
    keywords = ANALYSIS_KEYWORDS.get(analysis_type, [])

    # Multi-stage matching
    relevant = []

    # Stage 1: Exact keyword match
    exact_matches = []
    for chapter in chapters:
        title_lower = chapter.title.lower()
        if any(keyword == title_lower for keyword in keywords):
            exact_matches.append((chapter, 1.0))

    # Stage 2: Partial keyword match
    if not exact_matches:
        for chapter in chapters:
            title_lower = chapter.title.lower()
            if any(keyword in title_lower for keyword in keywords):
                exact_matches.append((chapter, 0.7))

    # Stage 3: Position-based heuristics for introduction/results
    if not exact_matches and analysis_type in ['background', 'innovation']:
        # Introduction and approach usually come first
        if len(chapters) > 0:
            exact_matches.append((chapters[0], 0.5))
    elif not exact_matches and analysis_type == 'results':
        # Results usually come near the end
        if len(chapters) > 1:
            exact_matches.append((chapters[-1], 0.5))

    relevant = [ch for ch, _ in exact_matches]

    # If still no matches, try content-based matching
    if not relevant:
        for chapter in chapters:
            # Check if chapter content has relevant keywords
            content_lower = chapter.content.lower()
            if any(keyword.lower() in content_lower for keyword in keywords):
                relevant.append(chapter)

    # If no relevant chapters found, use all content as fallback
    if not relevant:
        relevant = chapters

    # Extract figures from relevant chapters
    all_figures = []
    for chapter in relevant:
        figures = extract_figures_from_content(chapter.content)
        all_figures.extend(figures)

    # Combine content with smart truncation
    combined_parts = []
    total_length = 0

    # Prioritize beginning and end of relevant content
    for chapter in relevant:
        if total_length >= max_chars:
            break

        chapter_content = chapter.content

        # If adding full chapter would exceed limit, truncate intelligently
        if total_length + len(chapter_content) > max_chars:
            remaining = max_chars - total_length
            # Take beginning (70%) and end (30%) for better coverage
            start_len = int(remaining * 0.7)
            end_len = remaining - start_len
            if start_len > 0:
                combined_parts.append(chapter_content[:start_len])
            if end_len > 0 and len(chapter_content) > start_len:
                combined_parts.append(f"\n\n... (truncated) ...\n\n{chapter_content[-end_len:]}")
        else:
            combined_parts.append(f"\n### {chapter.title}\n\n{chapter_content}")

        total_length += len(chapter_content)

    combined = '\n\n'.join(combined_parts)

    return combined, all_figures