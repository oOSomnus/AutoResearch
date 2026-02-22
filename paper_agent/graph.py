"""
Graph Module - LangGraph workflow definition for the paper reading agent.
"""
from langgraph.graph import StateGraph, END

from .nodes import (
    AgentState,
    fetch_pdf,
    extract_content,
    analyze_background,
    analyze_innovation,
    analyze_results,
    generate_report,
    save_report
)


def create_paper_agent_graph():
    """
    Create and return the LangGraph workflow for paper analysis.

    The workflow consists of 7 sequential nodes:
    1. fetch_pdf - Get/download the PDF file
    2. extract_content - Extract text from PDF
    3. analyze_background - Analyze background & motivation
    4. analyze_innovation - Analyze innovation & core theory
    5. analyze_results - Analyze results & conclusions
    6. generate_report - Generate Markdown report
    7. save_report - Save report to file

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the workflow graph
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("fetch_pdf", fetch_pdf)
    workflow.add_node("extract_content", extract_content)
    workflow.add_node("analyze_background", analyze_background)
    workflow.add_node("analyze_innovation", analyze_innovation)
    workflow.add_node("analyze_results", analyze_results)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("save_report", save_report)

    # Define the entry point
    workflow.set_entry_point("fetch_pdf")

    # Define edges between nodes (sequential workflow)
    workflow.add_edge("fetch_pdf", "extract_content")
    workflow.add_edge("extract_content", "analyze_background")
    workflow.add_edge("analyze_background", "analyze_innovation")
    workflow.add_edge("analyze_innovation", "analyze_results")
    workflow.add_edge("analyze_results", "generate_report")
    workflow.add_edge("generate_report", "save_report")
    workflow.add_edge("save_report", END)

    # Compile the graph
    app = workflow.compile()

    return app


def run_paper_analysis(source: str):
    """
    Run the complete paper analysis workflow.

    Args:
        source: Path to local PDF file or URL to download from

    Returns:
        The final state with the analysis results
    """
    app = create_paper_agent_graph()

    # Initial state
    initial_state = {
        "source": source,
        "pdf_path": "",
        "content": "",
        "background": "",
        "innovation": "",
        "results": "",
        "report": "",
        "title": ""
    }

    # Run the workflow
    final_state = app.invoke(initial_state)

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