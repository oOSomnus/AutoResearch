"""
Base definitions for node functions.

Contains the AgentState TypedDict and common utilities used across all nodes.
"""
import os
from typing import TypedDict, List, Optional, Dict, Any

from langchain_openai import ChatOpenAI


class AgentState(TypedDict):
    """State object passed between nodes in the workflow."""
    pdf_path: str
    content: str
    background: str
    innovation: str
    results: str
    report: str
    title: str
    source: str
    # New fields for enhanced analysis
    chapters: List  # Extracted chapters list
    paper_type: str  # 'survey', 'experimental', 'theoretical', 'unknown'
    methodology: str  # Experimental methodology analysis
    related_work: str  # Related work analysis
    limitations: str  # Limitations analysis

    # Output configuration fields (Phase 1)
    output_format: str  # 'markdown', 'html', 'pdf', 'json'
    language: str  # 'zh', 'en'
    detail_level: str  # 'brief', 'standard', 'detailed'

    # New extraction dimensions (Phase 4)
    citations: str  # Citation analysis
    figures: str  # Figure analysis
    code: str  # Code extraction
    reproducibility: str  # Reproducibility assessment

    # Structured extraction data
    citations_list: List[dict]  # List of citation info
    figures_list: List[dict]  # List of figure info
    code_snippets: List[dict]  # List of code snippets
    reproducibility_score: float  # Reproducibility score (0-1)

    # Progress and checkpoint fields (Phase 2)
    completed_nodes: List[str]  # List of completed node names
    checkpoint_path: str  # Path to checkpoint file
    cache_key: str  # Cache key for the analysis

    # Adaptive analysis fields (Phase 5)
    analysis_plan: Dict[str, Any]  # Analysis plan with dimensions and priority
    quality_scores: Dict[str, float]  # Quality scores for each dimension
    iteration_count: Dict[str, int]  # Iteration count for each dimension
    pending_questions: List[str]  # Questions pending user confirmation
    user_feedback: Dict[str, Any]  # User feedback on analysis
    conversation_history: List[Dict]  # Conversation history for interactive mode
    needs_refinement: List[str]  # Dimensions needing refinement
    should_exit: bool  # Whether to exit early
    research_mode: str  # Current mode: 'auto', 'interactive', 'manual'
    current_dimension: str  # Current dimension being analyzed
    dimension_to_assess: str  # Dimension to assess for quality
    max_iterations: int  # Maximum iterations per dimension
    quality_threshold: float  # Quality threshold for acceptance


def get_llm():
    """Get configured LLM instance from environment variables."""
    from dotenv import load_dotenv
    load_dotenv()

    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gpt-4")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")

    return ChatOpenAI(
        openai_api_base=api_base,
        openai_api_key=api_key,
        model=model_name,
        temperature=0.3
    )