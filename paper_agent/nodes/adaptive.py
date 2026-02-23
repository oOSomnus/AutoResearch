"""
Adaptive analysis nodes for intelligent planning and quality assessment.

Contains nodes that plan analysis dimensions, assess quality of results,
and gather user feedback for iterative refinement.
"""
import json
from typing import Dict, Any

from .base import AgentState, get_llm
from ..prompts import (
    get_analysis_planning_prompt,
    get_quality_assessment_prompt
)


def plan_analysis(state: AgentState) -> AgentState:
    """
    Node: Intelligent analysis planning based on paper content.

    Decides which dimensions to analyze based on:
    - Paper type (survey/experimental/theoretical)
    - Presence of figures/tables
    - Presence of code/algorithms
    - Citation patterns
    - Content complexity
    """
    title = state.get("title", "")
    paper_type = state.get("paper_type", "unknown")
    content = state.get("content", "")
    chapters = state.get("chapters", [])
    language = state.get("language", "zh")

    print("📋 正在制定智能分析计划...")

    try:
        llm = get_llm()

        # Build chapter info for the prompt
        chapters_info = ""
        if chapters:
            chapters_info = "\n".join([
                f"- {ch.title} ({ch.chapter_type if ch.chapter_type else 'unknown'})"
                for ch in chapters[:10]
            ])

        # Build content preview
        content_preview = content[:3000] if len(content) > 3000 else content

        prompt = get_analysis_planning_prompt(
            title=title,
            paper_type=paper_type,
            content_preview=content_preview,
            chapters_info=chapters_info,
            language=language
        )
        response = llm.invoke(prompt)

        # Parse the response
        plan_result = {}
        if hasattr(response, 'content'):
            try:
                # Try to extract JSON from the response
                response_text = str(response.content).strip()
                # Find JSON object in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx]
                    plan_result = json.loads(json_text)
                else:
                    # Fallback to default plan
                    plan_result = _get_default_plan(paper_type)
            except json.JSONDecodeError:
                # Fallback to default plan
                plan_result = _get_default_plan(paper_type)
        else:
            plan_result = _get_default_plan(paper_type)

        # Ensure required fields exist
        dimensions = plan_result.get("dimensions", [])
        priority = plan_result.get("priority", dimensions[:])

        # Validate dimensions
        valid_dimensions = {
            "background", "innovation", "results",
            "methodology", "related_work", "limitations",
            "citations", "figures", "code", "reproducibility"
        }
        dimensions = [d for d in dimensions if d in valid_dimensions]
        priority = [d for d in priority if d in valid_dimensions]

        # Build analysis plan
        analysis_plan = {
            "dimensions": dimensions,
            "priority": priority,
            "reason": plan_result.get("reason", ""),
            "notes": plan_result.get("notes", []),
            "suggested_detail_level": plan_result.get("suggested_detail_level", "standard")
        }

        state["analysis_plan"] = analysis_plan

        print(f"✅ 分析计划完成")
        print(f"   待分析维度: {', '.join(dimensions)}")
        print(f"   优先级顺序: {', '.join(priority)}")
        if plan_result.get("reason"):
            print(f"   规划理由: {plan_result.get('reason')[:100]}...")

    except Exception as e:
        print(f"❌ 分析计划制定失败，使用默认计划: {e}")
        # Fallback to default plan
        default_plan = _get_default_plan(paper_type)
        state["analysis_plan"] = default_plan

    # Initialize adaptive analysis fields
    state.setdefault("quality_scores", {})
    state.setdefault("iteration_count", {})
    state.setdefault("needs_refinement", [])
    state.setdefault("current_dimension", "")
    state.setdefault("research_mode", "auto")
    state.setdefault("should_exit", False)
    state.setdefault("max_iterations", state.get("max_iterations", 3))
    state.setdefault("quality_threshold", state.get("quality_threshold", 0.75))

    return state


def _get_default_plan(paper_type: str) -> Dict[str, Any]:
    """Get default analysis plan based on paper type."""
    if paper_type == "survey":
        dimensions = ["background", "related_work", "innovation", "results"]
        priority = ["innovation", "background", "related_work", "results"]
        reason = "默认综述论文分析计划"
    elif paper_type == "experimental":
        dimensions = ["background", "innovation", "methodology", "results"]
        priority = ["innovation", "methodology", "results", "background"]
        reason = "默认实验论文分析计划"
    elif paper_type == "theoretical":
        dimensions = ["background", "innovation", "limitations", "results"]
        priority = ["innovation", "background", "limitations", "results"]
        reason = "默认理论论文分析计划"
    else:  # unknown
        dimensions = ["background", "innovation", "results"]
        priority = ["innovation", "background", "results"]
        reason = "默认未知类型论文分析计划"

    return {
        "dimensions": dimensions,
        "priority": priority,
        "reason": reason,
        "notes": [],
        "suggested_detail_level": "standard"
    }


def assess_quality(state: AgentState) -> AgentState:
    """
    Node: Assess the quality of analysis for a specific dimension.

    Evaluates:
    - Completeness: Does it cover key content?
    - Depth: Is it detailed enough?
    - Clarity: Is the language clear?
    - Accuracy: Is it accurate based on the original content?

    If quality is below threshold, adds dimension to needs_refinement.
    """
    dimension = state.get("dimension_to_assess", "")
    content_key = dimension

    # Map dimension to state key
    dim_to_key = {
        "background": "background",
        "innovation": "innovation",
        "results": "results",
        "methodology": "methodology",
        "related_work": "related_work",
        "limitations": "limitations",
        "citations": "citations",
        "figures": "figures",
        "code": "code",
        "reproducibility": "reproducibility"
    }

    content_key = dim_to_key.get(dimension, dimension)
    content = state.get(content_key, "")
    language = state.get("language", "zh")
    threshold = state.get("quality_threshold", 0.75)

    print(f"🔍 正在评估 {dimension} 的分析质量...")

    try:
        llm = get_llm()

        prompt = get_quality_assessment_prompt(
            dimension=dimension,
            content=content,
            language=language
        )
        response = llm.invoke(prompt)

        # Parse quality assessment
        assessment = {}
        if hasattr(response, 'content'):
            try:
                response_text = str(response.content).strip()
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx]
                    assessment = json.loads(json_text)
            except json.JSONDecodeError:
                pass

        # Extract scores
        overall_score = assessment.get("overall_score", 0.8)
        completeness = assessment.get("completeness", 0.8)
        depth = assessment.get("depth", 0.8)
        clarity = assessment.get("clarity", 0.8)
        accuracy = assessment.get("accuracy", 0.8)

        # Update quality scores
        state.setdefault("quality_scores", {})
        state["quality_scores"][dimension] = {
            "overall": overall_score,
            "completeness": completeness,
            "depth": depth,
            "clarity": clarity,
            "accuracy": accuracy
        }

        # Check if refinement is needed
        needs_refinement = assessment.get("needs_refinement", False) and overall_score < threshold

        if needs_refinement:
            # Check iteration count
            iteration_count = state.get("iteration_count", {}).get(dimension, 0)
            max_iterations = state.get("max_iterations", 3)

            if iteration_count < max_iterations:
                state.setdefault("needs_refinement", [])
                if dimension not in state["needs_refinement"]:
                    state["needs_refinement"].append(dimension)
                print(f"   ⚠️  质量不足 (得分: {overall_score:.2f}/{threshold:.2f})，需要精炼")
                if assessment.get("issues"):
                    print(f"   问题: {', '.join(assessment.get('issues', []))}")
                if assessment.get("suggestion"):
                    print(f"   建议: {assessment.get('suggestion', '')}")
            else:
                print(f"   ℹ️  质量不足但已达最大迭代次数 ({iteration_count}), 继续下一步")
        else:
            print(f"   ✅ 质量合格 (得分: {overall_score:.2f}/{threshold:.2f})")

    except Exception as e:
        print(f"❌ 质量评估失败，默认接受分析结果: {e}")
        # Accept the result by default
        pass

    # Clear the dimension to assess
    state["dimension_to_assess"] = ""

    return state


def gather_user_feedback(state: AgentState) -> AgentState:
    """
    Node: Collect user feedback on key decisions.

    This is a placeholder for future interactive feedback collection.
    In the current implementation, it's a no-op for non-interactive mode.
    """
    research_mode = state.get("research_mode", "auto")

    if research_mode == "auto":
        # Auto mode: no user feedback collection
        return state

    # For interactive mode, this would collect feedback
    # Currently just a placeholder
    print("📝 (用户反馈节点 - 非交互模式跳过)")

    return state