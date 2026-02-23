"""
Research Assistant - Advanced research assistant mode.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ResearchQuery:
    """A research query."""
    query: str
    context: Optional[str] = None
    papers: Optional[List[str]] = None  # List of paper paths to search in


@dataclass
class ResearchAnswer:
    """Answer to a research query."""
    query: str
    answer: str
    sources: List[str]
    confidence: float
    related_queries: List[str]


class ResearchAssistant:
    """Advanced research assistant for paper-related queries."""

    def __init__(self):
        """Initialize the research assistant."""
        self._indexed_papers: Dict[str, Dict[str, Any]] = {}
        self._qa_mode = None

    def index_paper(self, pdf_path: str) -> str:
        """
        Index a paper for research queries.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Paper ID
        """
        # Import here to avoid circular dependency
        from ..qa_mode import QAMode
        from ..pdf_reader import extract_pdf_text, extract_title

        if self._qa_mode is None:
            self._qa_mode = QAMode()

        # Extract paper info
        try:
            title = extract_title(pdf_path)
            content = extract_pdf_text(pdf_path)

            # Create basic state for indexing
            state = {
                "source": pdf_path,
                "title": title or "未知标题",
                "background": "",
                "innovation": "",
                "results": "",
                "methodology": "",
                "related_work": "",
                "limitations": ""
            }

            # Index the paper
            paper_id = self._qa_mode.index_paper(state)

            # Store paper info
            self._indexed_papers[paper_id] = {
                "path": pdf_path,
                "title": title,
                "content": content
            }

            return paper_id

        except Exception as e:
            print(f"索引论文失败: {e}")
            return ""

    def ask(self, query: str, paper_id: Optional[str] = None,
            n_results: int = 3) -> ResearchAnswer:
        """
        Ask a research question.

        Args:
            query: The question to ask
            paper_id: Specific paper to search in (None for all)
            n_results: Number of relevant results to retrieve

        Returns:
            ResearchAnswer with answer and sources
        """
        if not self._indexed_papers:
            raise ValueError("没有已索引的论文。请先使用 index_paper() 索引论文。")

        if self._qa_mode is None:
            from ..qa_mode import QAMode
            self._qa_mode = QAMode()

        # If no specific paper, search all indexed papers
        if paper_id is None:
            # For simplicity, use the first indexed paper
            paper_id = list(self._indexed_papers.keys())[0]

        # Query the Q&A mode
        qa_result = self._qa_mode.query(query, paper_id, n_results)

        # Generate related queries
        related_queries = self._generate_related_queries(query)

        return ResearchAnswer(
            query=query,
            answer=qa_result.answer,
            sources=qa_result.source_sections,
            confidence=qa_result.confidence,
            related_queries=related_queries
        )

    def _generate_related_queries(self, query: str) -> List[str]:
        """Generate related queries."""
        # Simple heuristic: extract key terms and generate variations
        related = []

        # Common research question patterns
        patterns = [
            ("为什么", "What is the reason for"),
            ("如何", "How to"),
            ("什么", "What"),
            ("哪个", "Which")
        ]

        # Extract potential key terms
        words = query.split()
        if len(words) > 1:
            # Create a more specific version
            related.append(f"{query} 的优势")
            related.append(f"{query} 的局限性")
            related.append(f"{query} 的应用")

        return related[:5]

    def list_indexed_papers(self) -> List[Dict[str, Any]]:
        """List all indexed papers."""
        return [
            {
                "paper_id": paper_id,
                "path": info["path"],
                "title": info["title"]
            }
            for paper_id, info in self._indexed_papers.items()
        ]

    def clear_index(self) -> None:
        """Clear all indexed papers."""
        if self._qa_mode:
            for paper_id in self._indexed_papers:
                self._qa_mode.clear_paper(paper_id)

        self._indexed_papers.clear()