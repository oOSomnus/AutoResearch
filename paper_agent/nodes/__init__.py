"""
Node functions for the LangGraph workflow.

This module exports all node functions and the AgentState TypedDict for
backward compatibility with existing code.
"""
from .base import AgentState, get_llm
from .input import fetch_pdf, extract_content, detect_paper_type
from .analysis import (
    analyze_background, analyze_innovation, analyze_results,
    analyze_methodology, analyze_related_work, analyze_limitations
)
from .output import generate_report, save_report
from .adaptive import plan_analysis, assess_quality, gather_user_feedback
from .extraction import extract_citations, analyze_figures, extract_code, assess_reproducibility

__all__ = [
    "AgentState", "get_llm",
    "fetch_pdf", "extract_content", "detect_paper_type",
    "analyze_background", "analyze_innovation", "analyze_results",
    "analyze_methodology", "analyze_related_work", "analyze_limitations",
    "generate_report", "save_report",
    "plan_analysis", "assess_quality", "gather_user_feedback",
    "extract_citations", "analyze_figures", "extract_code", "assess_reproducibility"
]