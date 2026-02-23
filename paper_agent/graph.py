"""
Graph Module - LangGraph workflow definition for the paper reading agent.
Supports checkpoint recovery, caching, and output configuration.
"""
from langgraph.graph import StateGraph, END, MessagesState
from typing import Dict, Any, Optional, List, Union
import os
import hashlib
from langchain_openai import ChatOpenAI

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
    save_report,
    plan_analysis,
    assess_quality,
    gather_user_feedback,
    extract_citations,
    analyze_figures,
    extract_code,
    assess_reproducibility
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


# ============================================================================
# Phase 5: Adaptive Analysis Graph
# ============================================================================

def route_after_planning(state: AgentState) -> str:
    """
    Route after planning: decide which dimension to analyze next.

    Returns the next node to execute based on the analysis plan.
    """
    plan = state.get("analysis_plan", {})
    dimensions = plan.get("dimensions", [])

    if not dimensions:
        # All dimensions analyzed, proceed to report generation
        return "generate_report"

    # Get the first dimension to analyze
    next_dim = dimensions[0]
    state["current_dimension"] = next_dim

    # Increment iteration count for this dimension
    iteration_count = state.get("iteration_count", {})
    iteration_count[next_dim] = iteration_count.get(next_dim, 0) + 1
    state["iteration_count"] = iteration_count

    # Map dimension to node name
    dim_to_node = {
        "background": "analyze_background",
        "innovation": "analyze_innovation",
        "results": "analyze_results",
        "methodology": "analyze_methodology",
        "related_work": "analyze_related_work",
        "limitations": "analyze_limitations",
        "citations": "extract_citations",
        "figures": "analyze_figures",
        "code": "extract_code",
        "reproducibility": "assess_reproducibility"
    }

    return dim_to_node.get(next_dim, "analyze_background")


def route_after_analysis(state: AgentState) -> str:
    """
    Route after analysis: quality assessment -> refinement or next dimension.

    After completing an analysis, route to quality assessment.
    """
    current_dim = state.get("current_dimension", "")
    plan = state.get("analysis_plan", {})
    dimensions = plan.get("dimensions", [])

    # Remove the completed dimension from the plan
    if current_dim and current_dim in dimensions:
        dimensions.remove(current_dim)
        plan["dimensions"] = dimensions
        state["analysis_plan"] = plan

    # Set dimension to assess
    state["dimension_to_assess"] = current_dim

    return "assess_quality"


def route_after_assessment(state: AgentState) -> str:
    """
    Route after quality assessment: decide whether to refine or continue.

    If refinement is needed and iteration count < max, return to analysis.
    Otherwise, proceed to the next dimension.
    """
    needs_refinement = state.get("needs_refinement", [])
    current_dim = state.get("current_dimension", "")

    # Clear refinement flag for this dimension
    if current_dim in needs_refinement:
        needs_refinement.remove(current_dim)
        state["needs_refinement"] = needs_refinement

        # Check if we should refine or continue
        iteration_count = state.get("iteration_count", {}).get(current_dim, 0)
        max_iterations = state.get("max_iterations", 3)

        if iteration_count < max_iterations:
            # Return to refine the current dimension
            dim_to_node = {
                "background": "analyze_background",
                "innovation": "analyze_innovation",
                "results": "analyze_results",
                "methodology": "analyze_methodology",
                "related_work": "analyze_related_work",
                "limitations": "analyze_limitations",
                "citations": "extract_citations",
                "figures": "analyze_figures",
                "code": "extract_code",
                "reproducibility": "assess_reproducibility"
            }
            print(f"   🔄 第 {iteration_count} 次精炼 {current_dim}...")
            return dim_to_node.get(current_dim, "analyze_background")
        else:
            print(f"   ⏭️  已达到最大迭代次数，继续下一个维度")

    # Continue to next dimension
    return "route_after_planning"


def route_after_results(state: AgentState) -> str:
    """
    Route after results analysis: check if extraction nodes are needed.

    This function checks if any optional extraction dimensions (citations,
    figures, code, reproducibility) are still in the analysis plan.
    """
    plan = state.get("analysis_plan", {})
    dimensions = plan.get("dimensions", [])

    # Check if any extraction dimensions remain
    extraction_dims = {"citations", "figures", "code", "reproducibility"}
    remaining_extractions = [d for d in dimensions if d in extraction_dims]

    if remaining_extractions:
        # Continue with extraction dimensions
        return "route_after_planning"
    else:
        # All done, generate report
        return "generate_report"


def create_adaptive_paper_agent_graph(
    max_iterations: int = 3,
    quality_threshold: float = 0.75,
    enable_quality_check: bool = True
) -> StateGraph:
    """
    Create and return the adaptive LangGraph workflow for paper analysis.

    The adaptive workflow uses intelligent planning and quality assessment:
    1. Plan analysis based on paper content and type
    2. Execute analysis dimensions in priority order
    3. Assess quality after each analysis
    4. Refine if quality is below threshold (up to max_iterations)
    5. Dynamically include optional extractions based on content

    Args:
        max_iterations: Maximum refinement iterations per dimension
        quality_threshold: Minimum quality score (0-1) to accept
        enable_quality_check: Whether to enable quality assessment

    Returns:
        Compiled StateGraph ready for execution
    """
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("fetch_pdf", fetch_pdf)
    workflow.add_node("extract_content", extract_content)
    workflow.add_node("detect_paper_type", detect_paper_type)
    workflow.add_node("plan_analysis", plan_analysis)
    workflow.add_node("analyze_background", analyze_background)
    workflow.add_node("analyze_innovation", analyze_innovation)
    workflow.add_node("analyze_methodology", analyze_methodology)
    workflow.add_node("analyze_results", analyze_results)
    workflow.add_node("analyze_related_work", analyze_related_work)
    workflow.add_node("analyze_limitations", analyze_limitations)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("save_report", save_report)
    workflow.add_node("assess_quality", assess_quality)
    workflow.add_node("gather_user_feedback", gather_user_feedback)

    # Add extraction nodes
    workflow.add_node("extract_citations", extract_citations)
    workflow.add_node("analyze_figures", analyze_figures)
    workflow.add_node("extract_code", extract_code)
    workflow.add_node("assess_reproducibility", assess_reproducibility)

    # Entry point
    workflow.set_entry_point("fetch_pdf")

    # Initial sequential edges
    workflow.add_edge("fetch_pdf", "extract_content")
    workflow.add_edge("extract_content", "detect_paper_type")
    workflow.add_edge("detect_paper_type", "plan_analysis")

    # Dynamic routing after planning
    workflow.add_conditional_edges(
        "plan_analysis",
        route_after_planning,
        {
            "analyze_background": "analyze_background",
            "analyze_innovation": "analyze_innovation",
            "analyze_results": "analyze_results",
            "analyze_methodology": "analyze_methodology",
            "analyze_related_work": "analyze_related_work",
            "analyze_limitations": "analyze_limitations",
            "extract_citations": "extract_citations",
            "analyze_figures": "analyze_figures",
            "extract_code": "extract_code",
            "assess_reproducibility": "assess_reproducibility",
            "generate_report": "generate_report"
        }
    )

    # After any analysis node, go to quality assessment or directly to routing
    for node in [
        "analyze_background", "analyze_innovation", "analyze_methodology",
        "analyze_results", "analyze_related_work", "analyze_limitations",
        "extract_citations", "analyze_figures", "extract_code",
        "assess_reproducibility"
    ]:
        if enable_quality_check:
            workflow.add_edge(node, "assess_quality")
        else:
            # Skip quality check, route to next dimension
            workflow.add_conditional_edges(
                node,
                route_after_planning,
                {
                    "analyze_background": "analyze_background",
                    "analyze_innovation": "analyze_innovation",
                    "analyze_results": "analyze_results",
                    "analyze_methodology": "analyze_methodology",
                    "analyze_related_work": "analyze_related_work",
                    "analyze_limitations": "analyze_limitations",
                    "extract_citations": "extract_citations",
                    "analyze_figures": "analyze_figures",
                    "extract_code": "extract_code",
                    "assess_reproducibility": "assess_reproducibility",
                    "generate_report": "generate_report"
                }
            )

    # After quality assessment, decide to refine or continue
    workflow.add_conditional_edges(
        "assess_quality",
        route_after_assessment,
        {
            "analyze_background": "analyze_background",
            "analyze_innovation": "analyze_innovation",
            "analyze_results": "analyze_results",
            "analyze_methodology": "analyze_methodology",
            "analyze_related_work": "analyze_related_work",
            "analyze_limitations": "analyze_limitations",
            "extract_citations": "extract_citations",
            "analyze_figures": "analyze_figures",
            "extract_code": "extract_code",
            "assess_reproducibility": "assess_reproducibility",
            "generate_report": "generate_report"
        }
    )

    # Final edges
    workflow.add_edge("generate_report", "save_report")
    workflow.add_edge("save_report", END)

    # Compile the graph
    app = workflow.compile()

    return app


def run_adaptive_paper_analysis(
    source: str,
    output_format: str = "markdown",
    language: str = "zh",
    detail_level: str = "standard",
    checkpoint_path: Optional[str] = None,
    max_iterations: int = 3,
    quality_threshold: float = 0.75,
    enable_quality_check: bool = True,
    research_mode: str = "auto"
) -> Dict[str, Any]:
    """
    Run the adaptive paper analysis workflow.

    Args:
        source: Path to local PDF file or URL to download from
        output_format: Output format (markdown, html, pdf, json)
        language: Language for analysis (zh, en)
        detail_level: Detail level (brief, standard, detailed)
        checkpoint_path: Optional path to resume from checkpoint
        max_iterations: Maximum refinement iterations per dimension
        quality_threshold: Minimum quality score (0-1) to accept
        enable_quality_check: Whether to enable quality assessment
        research_mode: Research mode (auto, interactive, manual)

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
            "cache_key": "",
            # Adaptive analysis fields
            "analysis_plan": {},
            "quality_scores": {},
            "iteration_count": {},
            "needs_refinement": [],
            "current_dimension": "",
            "research_mode": research_mode,
            "should_exit": False,
            "max_iterations": max_iterations,
            "quality_threshold": quality_threshold
        }

    app = create_adaptive_paper_agent_graph(
        max_iterations=max_iterations,
        quality_threshold=quality_threshold,
        enable_quality_check=enable_quality_check
    )

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

    # Print quality summary
    quality_scores = final_state.get("quality_scores", {})
    if quality_scores:
        print("\n" + "=" * 60)
        print("📊 分析质量评估汇总")
        print("=" * 60)
        for dim, scores in quality_scores.items():
            overall = scores.get("overall", 0)
            print(f"  {dim}: {overall:.2f} (完整度: {scores.get('completeness', 0):.2f}, "
                  f"深度: {scores.get('depth', 0):.2f}, 清晰度: {scores.get('clarity', 0):.2f})")

    return final_state


# ============================================================================
# Phase 5: Interactive Q&A Graph
# ============================================================================

class InteractiveAgentState(MessagesState):
    """
    Interactive agent state for Q&A mode.

    Extends MessagesState to include paper analysis data.
    """
    pdf_path: str
    content: str
    title: str
    paper_type: str
    background: str
    innovation: str
    results: str
    methodology: str
    related_work: str
    limitations: str
    citations: str
    figures: str
    code: str
    reproducibility: str
    report: str
    source: str
    chapters: list
    output_format: str
    language: str
    detail_level: str
    analysis_complete: bool = False
    analysis_plan: dict = {}
    quality_scores: dict = {}


def get_llm_for_interactive():
    """Get configured LLM instance for interactive mode."""
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


def run_initial_analysis(state: InteractiveAgentState) -> InteractiveAgentState:
    """
    Run initial paper analysis before entering Q&A mode.

    This reuses the adaptive analysis workflow to build a complete
    understanding of the paper before allowing user questions.
    """
    print("📚 正在完成初始论文分析...")

    # Convert to regular AgentState and run adaptive analysis
    agent_state = {
        "source": state.get("source", ""),
        "pdf_path": state.get("pdf_path", ""),
        "content": state.get("content", ""),
        "title": state.get("title", ""),
        "chapters": state.get("chapters", []),
        "paper_type": state.get("paper_type", "unknown"),
        "output_format": state.get("output_format", "markdown"),
        "language": state.get("language", "zh"),
        "detail_level": state.get("detail_level", "standard"),
        "research_mode": "interactive",
        "max_iterations": 2,  # Fewer iterations for interactive mode
        "quality_threshold": 0.7
    }

    # Run the analysis
    final_state = run_adaptive_paper_analysis(
        source=state.get("source", ""),
        output_format=state.get("output_format", "markdown"),
        language=state.get("language", "zh"),
        detail_level=state.get("detail_level", "standard"),
        max_iterations=2,
        quality_threshold=0.7,
        research_mode="interactive"
    )

    # Copy results back to interactive state
    state.update({
        "background": final_state.get("background", ""),
        "innovation": final_state.get("innovation", ""),
        "results": final_state.get("results", ""),
        "methodology": final_state.get("methodology", ""),
        "related_work": final_state.get("related_work", ""),
        "limitations": final_state.get("limitations", ""),
        "citations": final_state.get("citations", ""),
        "figures": final_state.get("figures", ""),
        "code": final_state.get("code", ""),
        "reproducibility": final_state.get("reproducibility", ""),
        "report": final_state.get("report", ""),
        "analysis_complete": True,
        "analysis_plan": final_state.get("analysis_plan", {}),
        "quality_scores": final_state.get("quality_scores", {})
    })

    return state


def answer_user_question(state: InteractiveAgentState) -> InteractiveAgentState:
    """
    Answer a user question about the paper.

    Uses the completed analysis to provide accurate answers.
    """
    messages = state.get("messages", [])
    if not messages:
        return state

    # Get the latest user message
    user_message = messages[-1]
    question = user_message.content if hasattr(user_message, "content") else str(user_message)

    # Build analysis summary for context
    analysis_summary = f"""
论文标题: {state.get('title', '')}
论文类型: {state.get('paper_type', '')}

背景分析:
{state.get('background', '')[:500]}...

创新点:
{state.get('innovation', '')[:500]}...

主要结果:
{state.get('results', '')[:500]}...
"""

    # Build conversation history
    history = ""
    for msg in messages[:-1]:
        role = "User" if msg.type == "human" else "Assistant"
        history += f"{role}: {msg.content}\n"

    # Generate answer
    try:
        llm = get_llm_for_interactive()

        prompt = f"""你是一个论文阅读助手，正在与用户对话。

论文标题：{state.get('title', '')}
已完成的分析：
{analysis_summary}

用户问题：{question}

历史对话：
{history}

请基于论文分析内容回答用户的问题。如果用户要求重新分析某个维度，
请在回答中明确指出。

回答要求：
1. 准确、简洁
2. 基于已分析的论文内容
3. 如果需要更多信息，请说明
"""

        from langchain_core.messages import AIMessage
        response = llm.invoke(prompt)
        ai_message = AIMessage(content=response.content)

        # Add AI response to messages
        state["messages"] = messages + [ai_message]

    except Exception as e:
        print(f"❌ 回答问题时出错: {e}")
        from langchain_core.messages import AIMessage
        ai_message = AIMessage(content=f"抱歉，回答问题时出现错误: {str(e)}")
        state["messages"] = messages + [ai_message]

    return state


def should_continue_qa(state: InteractiveAgentState) -> str:
    """
    Decide whether to continue Q&A or end the conversation.

    Returns "continue" to answer more questions, "end" to stop.
    """
    messages = state.get("messages", [])
    if not messages:
        return "continue"

    # Check the last user message for exit commands
    user_message = messages[-1]
    if hasattr(user_message, "content"):
        content = user_message.content.lower()
        if any(cmd in content for cmd in ["退出", "exit", "quit", "结束", "end", "bye"]):
            return "end"

    return "continue"


def create_interactive_paper_agent_graph() -> StateGraph:
    """
    Create an interactive Q&A graph for paper analysis.

    The workflow:
    1. Complete initial analysis
    2. Enter conversation loop for Q&A
    3. User can ask questions or request refinements

    Returns:
        Compiled StateGraph ready for execution
    """
    workflow = StateGraph(InteractiveAgentState)

    # Add nodes
    workflow.add_node("initial_analysis", run_initial_analysis)
    workflow.add_node("answer_question", answer_user_question)

    # Entry point
    workflow.set_entry_point("initial_analysis")

    # After initial analysis, go to answer loop
    workflow.add_conditional_edges(
        "initial_analysis",
        lambda state: "answer_question" if state.get("analysis_complete") else END,
        {
            "answer_question": "answer_question",
            END: END
        }
    )

    # After answering, check if we should continue
    workflow.add_conditional_edges(
        "answer_question",
        should_continue_qa,
        {
            "continue": "answer_question",
            "end": END
        }
    )

    # Compile the graph
    app = workflow.compile()

    return app