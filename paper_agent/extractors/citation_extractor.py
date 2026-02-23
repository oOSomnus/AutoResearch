"""
Citation Extractor - Extract and analyze citations from papers.
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass

from ..types import CitationInfo
from ..pdf_reader import extract_pdf_text


class CitationExtractor:
    """Extract and analyze citations from paper content."""

    def __init__(self):
        """Initialize the citation extractor."""
        # Common citation patterns
        self.citation_patterns = [
            # [1], [Author, Year], (Author et al., Year)
            r'\[(\d+)\]',
            r'\[([A-Z][a-z]+(?: et al\.)?,\s*\d{4})\]',
            r'\(([A-Z][a-z]+(?: et al\.)?,\s*\d{4})\)',
            # References section patterns
            r'^\[(\d+)\]\s+(.+)$',
            r'^(\d+)\.\s+(.+)$',
        ]

        self.foundational_keywords = [
            "foundational", "seminal", "pioneering", "classic",
            "开创性", "基础", "经典", "先驱"
        ]

        self.recent_keywords = [
            "recent", "latest", "state-of-the-art", "sota",
            "最新", "前沿", "最先进"
        ]

        self.competing_keywords = [
            "competing", "alternative", "baseline", "compared to",
            "竞争", "替代", "基线", "对比"
        ]

    def extract_citations(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract citations from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted citations and analysis
        """
        # Extract text
        content = extract_pdf_text(pdf_path)

        # Find all citation markers
        citations = []
        citation_markers = self._find_citation_markers(content)

        # Extract references section
        references = self._extract_references(content)

        # Analyze citations
        citation_list = self._analyze_citations(content, citation_markers, references)

        # Generate analysis text
        analysis_text = self._generate_analysis_text(citation_list)

        return {
            "citations": analysis_text,
            "citations_list": citation_list,
            "total_citations": len(citation_list),
            "reference_count": len(references)
        }

    def _find_citation_markers(self, content: str) -> List[Dict[str, Any]]:
        """Find citation markers in the text."""
        markers = []

        for pattern in self.citation_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Get context around the citation
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip()

                markers.append({
                    "text": match.group(0),
                    "position": match.start(),
                    "context": context
                })

        return markers

    def _extract_references(self, content: str) -> List[str]:
        """Extract the references section."""
        # Look for references section
        references_pattern = r'(?:References|参考文献|Bibliography)[\s\S]*$'
        references_match = re.search(references_pattern, content, re.IGNORECASE)

        if not references_match:
            return []

        references_text = references_match.group(0)
        references = []

        # Try to parse individual references
        ref_patterns = [
            r'^\[(\d+)\]\s+(.+)$',
            r'^(\d+)\.\s+(.+)$',
            r'^([A-Z][a-z]+(?: et al\.)?)\s*\(\d{4}\)\.?\s+(.+)$'
        ]

        for line in references_text.split('\n'):
            line = line.strip()
            if not line or line.lower().startswith(('references', '参考文献', 'bibliography')):
                continue

            for pattern in ref_patterns:
                if re.match(pattern, line):
                    references.append(line)
                    break

        return references

    def _analyze_citations(self, content: str, markers: List[Dict],
                          references: List[str]) -> List[CitationInfo]:
        """Analyze citations and categorize them."""
        citations = []

        for marker in markers:
            context = marker.get("context", "")
            citation_text = marker.get("text", "")

            # Determine citation type
            citation_type = self._determine_citation_type(context)

            # Extract author/year if possible
            author_year_match = re.search(r'([A-Z][a-z]+(?: et al\.)?),\s*(\d{4})', citation_text)
            if author_year_match:
                authors = [author_year_match.group(1)]
                year = int(author_year_match.group(2))
            else:
                authors = []
                year = 0

            # Try to find title from references
            title = ""
            ref_id = re.search(r'\[(\d+)\]', citation_text)
            if ref_id:
                idx = int(ref_id.group(1)) - 1
                if 0 <= idx < len(references):
                    title = references[idx][:100]  # First 100 chars

            citation_info = CitationInfo(
                reference_id=marker.get("text", ""),
                authors=authors,
                title=title,
                year=year,
                citation_type=citation_type,
                context=context,
                relevance_score=self._calculate_relevance(context)
            )

            citations.append(citation_info)

        return citations

    def _determine_citation_type(self, context: str) -> str:
        """Determine the type of citation based on context."""
        context_lower = context.lower()

        # Check for foundational keywords
        for keyword in self.foundational_keywords:
            if keyword in context_lower:
                return "foundational"

        # Check for recent keywords
        for keyword in self.recent_keywords:
            if keyword in context_lower:
                return "recent"

        # Check for competing keywords
        for keyword in self.competing_keywords:
            if keyword in context_lower:
                return "competing"

        return "other"

    def _calculate_relevance(self, context: str) -> float:
        """Calculate relevance score based on context."""
        # Simple heuristic: more mentions of key concepts = higher relevance
        score = 0.5  # Base score

        # Check for keywords indicating importance
        important_keywords = ["critical", "key", "main", "primary", "essential",
                            "关键", "主要", "重要", "核心"]

        for keyword in important_keywords:
            if keyword.lower() in context.lower():
                score += 0.1

        return min(score, 1.0)

    def _generate_analysis_text(self, citations: List[CitationInfo]) -> str:
        """Generate analysis text from citation list."""
        if not citations:
            return "未在论文中找到引用信息。"

        # Count by type
        type_counts = {}
        for citation in citations:
            c_type = citation.citation_type
            type_counts[c_type] = type_counts.get(c_type, 0) + 1

        # Get key references
        foundational = [c for c in citations if c.citation_type == "foundational"][:5]
        recent = [c for c in citations if c.citation_type == "recent"][:5]
        competing = [c for c in citations if c.citation_type == "competing"][:5]

        # Build analysis text
        parts = [f"## 引用分析"]

        parts.append(f"\n这篇论文共引用了 **{len(citations)}** 处文献。")

        if type_counts:
            type_labels = {
                "foundational": "基础文献",
                "recent": "近期研究",
                "competing": "竞争方法",
                "other": "其他"
            }
            type_parts = [f"- {type_labels.get(k, k)}: {v}" for k, v in type_counts.items()]
            parts.append("\n**引用类型分布：**\n" + "\n".join(type_parts))

        if foundational:
            parts.append("\n**重要基础文献：**")
            for c in foundational[:3]:
                if c.title:
                    parts.append(f"- {c.title[:80]}...")

        if recent:
            parts.append("\n**近期相关工作：**")
            for c in recent[:3]:
                if c.title:
                    parts.append(f"- {c.title[:80]}...")

        return "\n".join(parts)