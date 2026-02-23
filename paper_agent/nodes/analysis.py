"""
Analysis nodes for core paper analysis dimensions.

Contains nodes that analyze background, innovation, results, methodology,
related work, and limitations of research papers.
"""

from .base import AgentState, get_llm
from ..chunking import get_relevant_content_for_analysis
from ..prompts import (
    get_background_prompt,
    get_innovation_prompt,
    get_results_prompt,
    get_methodology_prompt,
    get_related_work_prompt,
    get_limitations_prompt
)


def analyze_background(state: AgentState) -> AgentState:
    """
    Node 4: Analyze the background and motivation of the research.
    Uses chapter-based content for more focused analysis.
    """
    chapters = state.get("chapters", [])
    content = state.get("content", "")

    print("🔍 正在分析背景&原因...")

    try:
        llm = get_llm()
        language = state.get("language", "zh")

        # Use improved chapter-based content if available
        figures_context = ""
        if chapters:
            relevant_content, figures = get_relevant_content_for_analysis(chapters, 'background')
            if relevant_content:
                content = relevant_content
                # Build figures context
                if figures:
                    figures_context = "\n\n**图表信息：**\n" + "\n".join([
                        f"- {f.identifier}: {f.caption[:200]}"
                        for f in figures[:5]
                    ])

        prompt = get_background_prompt(content, language=language, figures_context=figures_context)
        response = llm.invoke(prompt)
        background = response.content.strip()

        print("✅ 背景分析完成")
    except Exception as e:
        print(f"❌ 背景分析失败: {e}")
        background = f"分析失败: {str(e)}"

    state["background"] = background
    return state


def analyze_innovation(state: AgentState) -> AgentState:
    """
    Node 4: Analyze the innovation and core theory of the research.
    Uses improved content selection with figure/table context.
    """
    chapters = state.get("chapters", [])
    content = state.get("content", "")

    print("💡 正在分析创新&核心理论...")

    try:
        llm = get_llm()
        language = state.get("language", "zh")

        # Use improved chapter-based content if available
        figures_context = ""
        if chapters:
            relevant_content, figures = get_relevant_content_for_analysis(chapters, 'innovation')
            if relevant_content:
                content = relevant_content
                # Build figures context
                if figures:
                    figures_context = "\n\n**图表信息：**\n" + "\n".join([
                        f"- {f.identifier}: {f.caption[:200]}"
                        for f in figures[:10]
                    ])

        prompt = get_innovation_prompt(content, language=language, figures_context=figures_context)
        response = llm.invoke(prompt)
        innovation = response.content.strip()

        print("✅ 创新分析完成")
    except Exception as e:
        print(f"❌ 创新分析失败: {e}")
        innovation = f"分析失败: {str(e)}"

    state["innovation"] = innovation
    return state


def analyze_results(state: AgentState) -> AgentState:
    """
    Node 6: Analyze the results and conclusions of the research.
    Uses improved chapter-based content with figure/table context.
    """
    chapters = state.get("chapters", [])
    content = state.get("content", "")

    print("📊 正在分析结果...")

    try:
        llm = get_llm()
        language = state.get("language", "zh")

        # Use improved chapter-based content if available
        figures_context = ""
        if chapters:
            relevant_content, figures = get_relevant_content_for_analysis(chapters, 'results')
            if relevant_content:
                content = relevant_content
                # Build figures context (important for results)
                if figures:
                    figures_context = "\n\n**图表信息：**\n" + "\n".join([
                        f"- {f.identifier}: {f.caption[:200]}"
                        for f in figures[:10]
                    ])

        prompt = get_results_prompt(content, language=language, figures_context=figures_context)
        response = llm.invoke(prompt)
        results = response.content.strip()

        print("✅ 结果分析完成")
    except Exception as e:
        print(f"❌ 结果分析失败: {e}")
        results = f"分析失败: {str(e)}"

    state["results"] = results
    return state


def analyze_methodology(state: AgentState) -> AgentState:
    """
    Node: Analyze the experimental methodology of the research.
    """
    chapters = state.get("chapters", [])
    content = state.get("content", "")

    print("🔬 正在分析实验方法...")

    try:
        llm = get_llm()

        # Use chapter-based content if available
        if chapters:
            relevant_content = get_relevant_content_for_analysis(chapters, 'methodology')
            if relevant_content:
                content = relevant_content

        prompt = get_methodology_prompt(content)
        response = llm.invoke(prompt)
        methodology = response.content.strip()

        print("✅ 实验方法分析完成")
    except Exception as e:
        print(f"❌ 实验方法分析失败: {e}")
        methodology = f"分析失败: {str(e)}"

    state["methodology"] = methodology
    return state


def analyze_related_work(state: AgentState) -> AgentState:
    """
    Node: Analyze the related work of the research.
    """
    chapters = state.get("chapters", [])
    content = state.get("content", "")

    print("📚 正在分析相关工作...")

    try:
        llm = get_llm()

        # Use chapter-based content if available
        if chapters:
            relevant_content = get_relevant_content_for_analysis(chapters, 'related_work')
            if relevant_content:
                content = relevant_content

        prompt = get_related_work_prompt(content)
        response = llm.invoke(prompt)
        related_work = response.content.strip()

        print("✅ 相关工作分析完成")
    except Exception as e:
        print(f"❌ 相关工作分析失败: {e}")
        related_work = f"分析失败: {str(e)}"

    state["related_work"] = related_work
    return state


def analyze_limitations(state: AgentState) -> AgentState:
    """
    Node: Analyze the limitations of the research.
    """
    chapters = state.get("chapters", [])
    content = state.get("content", "")

    print("⚠️  正在分析局限性...")

    try:
        llm = get_llm()

        # Use chapter-based content if available
        if chapters:
            relevant_content = get_relevant_content_for_analysis(chapters, 'limitations')
            if relevant_content:
                content = relevant_content

        prompt = get_limitations_prompt(content)
        response = llm.invoke(prompt)
        limitations = response.content.strip()

        print("✅ 局限性分析完成")
    except Exception as e:
        print(f"❌ 局限性分析失败: {e}")
        limitations = f"分析失败: {str(e)}"

    state["limitations"] = limitations
    return state