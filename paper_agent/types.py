"""
Types Module - Data structures for enhanced analysis.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class AnalysisDecision:
    """Analysis decision result from the planning phase."""
    dimensions_to_analyze: List[str]
    priority_order: List[str]
    reason: str
    confidence: float
    suggested_detail_level: str = "standard"
    suggested_additional_analyses: List[str] = None

    def __post_init__(self):
        if self.suggested_additional_analyses is None:
            self.suggested_additional_analyses = []


@dataclass
class QualityAssessment:
    """Quality assessment result for a dimension."""
    dimension: str
    score: float  # 0-1
    completeness: float  # 0-1
    depth: float  # 0-1
    clarity: float  # 0-1
    accuracy: float  # 0-1
    issues: List[str]
    needs_refinement: bool
    suggestion: str


@dataclass
class FigureInfo:
    """Information about a figure or image in the paper."""
    page_num: int
    caption: str
    figure_type: str  # 'chart', 'graph', 'image', 'diagram', 'table'
    description: str
    page_range: Optional[tuple] = None  # (start_page, end_page)


@dataclass
class TableInfo:
    """Information about a table in the paper."""
    page_num: int
    caption: str
    content: str
    headers: List[str]
    row_count: int
    col_count: int


@dataclass
class CodeSnippet:
    """Information about code or algorithm in the paper."""
    page_num: int
    language: str  # 'python', 'pseudocode', 'algorithm', etc.
    code: str
    description: str
    is_algorithm: bool = False
    algorithm_name: Optional[str] = None


@dataclass
class CitationInfo:
    """Information about a citation in the paper."""
    reference_id: str
    authors: List[str]
    title: str
    year: int
    citation_type: str  # 'foundational', 'recent', 'competing', 'other'
    context: str  # The sentence/paragraph where cited
    relevance_score: float = 0.0  # How relevant this citation is (0-1)


@dataclass
class ReproducibilityAssessment:
    """Assessment of paper reproducibility."""
    score: float  # Overall score (0-1)
    code_available: bool
    data_available: bool
    environment_specified: bool
    metrics_reported: bool
    results_reproducible: bool
    notes: List[str]
    suggestions: List[str]


@dataclass
class ComparisonResult:
    """Result of comparing multiple papers."""
    paper_ids: List[str]
    comparison_type: str  # 'methodology', 'results', 'approach', etc.
    similarities: List[str]
    differences: List[str]
    ranking: List[dict]  # Ranked papers by some metric
    summary: str