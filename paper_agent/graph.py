"""
Graph Module - LangGraph workflow definition for the paper reading agent.
Supports checkpoint recovery, caching, and output configuration.
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional, List

from .nodes import (
    AgentState,
    fetch_pdf,
    extract_content,
    detect_paper_type,
    analyze_background,
    analyze_innovation,
    analyze_methodology,
    analyze_results,
    analyze_related_work,
    analyze_limitations,
    generate_report,
    save_report
)


def route_to_background(state: AgentState) -> str:
    """Route from paper type detection to background analysis."""
    return "analyze_background"


def route_from_background(state: AgentState) -> str:
    """Route from background to next analysis based on paper type."""
    paper_type = state.get("paper_type", "unknown")

    if paper_type == "survey":
        return "analyze_related_work"
    elif paper_type == "experimental":
        return "analyze_innovation"
    else:  # theoretical or unknown
        return "analyze_innovation"


def route_from_related_work(state: AgentState) -> str:
    """Route from related work to innovation (for survey papers)."""
    return "analyze_innovation"


def route_from_innovation(state: AgentState) -> str:
    """Route from innovation to next analysis based on paper type."""
    paper_type = state.get("paper_type", "unknown")

    if paper_type == "survey":
        return "analyze_results"
    elif paper_type == "experimental":
        return "analyze_methodology"
    else:  # theoretical or unknown
        return "analyze_limitations"


def route_from_methodology(state: AgentState) -> str:
    """Route from methodology to results (for experimental papers)."""
    return "analyze_results"


def route_from_limitations(state: AgentState) -> str:
    """Route from limitations to results (for theoretical/unknown papers)."""
    return "analyze_results"


def route_to_report(state: AgentState) -> str:
    """Route from any analysis node to report generation."""
    return "generate_report"


def create_paper_agent_graph():
    """
    Create and return the LangGraph workflow for paper analysis.

    The workflow uses conditional branching based on paper type:
    - Survey papers: background -> related_work -> innovation -> results
    - Experimental papers: background -> innovation -> methodology -> results
    - Theoretical/Unknown papers: background -> innovation -> limitations -> results

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the workflow graph
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("fetch_pdf", fetch_pdf)
    workflow.add_node("extract_content", extract_content)
    workflow.add_node("detect_paper_type", detect_paper_type)
    workflow.add_node("analyze_background", analyze_background)
    workflow.add_node("analyze_innovation", analyze_innovation)
    workflow.add_node("analyze_methodology", analyze_methodology)
    workflow.add_node("analyze_results", analyze_results)
    workflow.add_node("analyze_related_work", analyze_related_work)
    workflow.add_node("analyze_limitations", analyze_limitations)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("save_report", save_report)

    # Define the entry point
    workflow.set_entry_point("fetch_pdf")

    # Define initial sequential edges
    workflow.add_edge("fetch_pdf", "extract_content")
    workflow.add_edge("extract_content", "detect_paper_type")

    # Route from paper type detection to background analysis
    workflow.add_conditional_edges(
        "detect_paper_type",
        route_to_background,
        {"analyze_background": "analyze_background"}
    )

    # Conditional branching from background based on paper type
    workflow.add_conditional_edges(
        "analyze_background",
        route_from_background,
        {
            "analyze_related_work": "analyze_related_work",
            "analyze_innovation": "analyze_innovation"
        }
    )

    # Route from related work to innovation (survey papers only)
    workflow.add_conditional_edges(
        "analyze_related_work",
        route_from_related_work,
        {"analyze_innovation": "analyze_innovation"}
    )

    # Route from innovation based on paper type
    workflow.add_conditional_edges(
        "analyze_innovation",
        route_from_innovation,
        {
            "analyze_results": "analyze_results",
            "analyze_methodology": "analyze_methodology",
            "analyze_limitations": "analyze_limitations"
        }
    )

    # Route from methodology to results (experimental papers)
    workflow.add_conditional_edges(
        "analyze_methodology",
        route_from_methodology,
        {"analyze_results": "analyze_results"}
    )

    # Route from limitations to results (theoretical/unknown papers)
    workflow.add_conditional_edges(
        "analyze_limitations",
        route_from_limitations,
        {"analyze_results": "analyze_results"}
    )

    # All analysis nodes converge to report generation
    workflow.add_conditional_edges(
        "analyze_results",
        route_to_report,
        {"generate_report": "generate_report"}
    )

    # Final edge to save report
    workflow.add_edge("generate_report", "save_report")
    workflow.add_edge("save_report", END)

    # Compile the graph
    app = workflow.compile()

    return app


def run_paper_analysis(source: str,
                      output_format: str = "markdown",
                      language: str = "zh",
                      detail_level: str = "standard",
                      checkpoint_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the complete paper analysis workflow.

    Args:
        source: Path to local PDF file or URL to download from
        output_format: Output format (markdown, html, pdf, json)
        language: Language for analysis (zh, en)
        detail_level: Detail level (brief, standard, detailed)
        checkpoint_path: Optional path to resume from checkpoint

    Returns:
        The final state with the analysis results
    """
    # Check if resuming from checkpoint
    if checkpoint_path:
        from .checkpoint import get_checkpoint_manager
        checkpoint_mgr = get_checkpoint_manager()
        initial_state = checkpoint_mgr.load_checkpoint(checkpoint_path)

        if initial_state:
            print(f"📋 从检查点恢复: {checkpoint_path}")
            print(f"   已完成节点: {initial_state.get('completed_nodes', [])}")
        else:
            print(f"⚠️  检查点无效，从头开始分析")
            initial_state = None
    else:
        initial_state = None

    # If no checkpoint, create initial state
    if initial_state is None:
        initial_state = {
            "source": source,
            "pdf_path": "",
            "content": "",
            "background": "",
            "innovation": "",
            "results": "",
            "report": "",
            "title": "",
            "chapters": [],
            "paper_type": "",
            "methodology": "",
            "related_work": "",
            "limitations": "",
            # Output configuration
            "output_format": output_format,
            "language": language,
            "detail_level": detail_level,
            # New extraction dimensions
            "citations": "",
            "figures": "",
            "code": "",
            "reproducibility": "",
            "citations_list": [],
            "figures_list": [],
            "code_snippets": [],
            "reproducibility_score": 0.0,
            # Progress and checkpoint fields
            "completed_nodes": [],
            "checkpoint_path": "",
            "cache_key": ""
        }

    app = create_paper_agent_graph()

    # Run the workflow
    final_state = app.invoke(initial_state)

    # Save to history if analysis completed successfully
    if final_state.get("report"):
        try:
            from .history import get_history_manager
            history_mgr = get_history_manager()
            history_mgr.add_entry(final_state)
        except Exception:
            # History saving is optional, don't fail the workflow
            pass

    return final_state


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        result = run_paper_analysis(sys.argv[1])
        print(f"\n=== Analysis Complete ===")
        print(f"Source: {result['source']}")
        print(f"Title: {result['title']}")
        print(f"Background: {result['background'][:100]}...")
    else:
        print("Usage: python graph.py <pdf_path_or_url>")