"""
Extraction nodes for content extraction from papers.

Contains nodes that extract and analyze citations, figures, code snippets,
and assess reproducibility of research papers.
"""

from .base import AgentState


def extract_citations(state: AgentState) -> AgentState:
    """
    Node: Extract and analyze citations from the paper.
    """
    pdf_path = state["pdf_path"]
    language = state.get("language", "zh")

    print("📚 正在提取引用分析...")

    try:
        from ..extractors import CitationExtractor
        extractor = CitationExtractor()

        result = extractor.extract_citations(pdf_path)

        state["citations"] = result.get("citations", "")
        state["citations_list"] = result.get("citations_list", [])

        print("✅ 引用分析完成")
    except Exception as e:
        print(f"❌ 引用分析失败: {e}")
        state["citations"] = f"分析失败: {str(e)}"
        state["citations_list"] = []

    return state


def analyze_figures(state: AgentState) -> AgentState:
    """
    Node: Extract and analyze figures and tables from the paper.
    """
    pdf_path = state["pdf_path"]
    language = state.get("language", "zh")

    print("📊 正在分析图表...")

    try:
        from ..extractors import FigureExtractor
        extractor = FigureExtractor()

        result = extractor.extract_figures(pdf_path)

        state["figures"] = result.get("figures", "")
        state["figures_list"] = result.get("figures_list", [])
        state["tables_list"] = result.get("tables_list", [])

        print("✅ 图表分析完成")
    except Exception as e:
        print(f"❌ 图表分析失败: {e}")
        state["figures"] = f"分析失败: {str(e)}"
        state["figures_list"] = []
        state["tables_list"] = []

    return state


def extract_code(state: AgentState) -> AgentState:
    """
    Node: Extract code and algorithms from the paper.
    """
    pdf_path = state["pdf_path"]
    language = state.get("language", "zh")

    print("💻 正在提取代码...")

    try:
        from ..extractors import CodeExtractor
        extractor = CodeExtractor()

        result = extractor.extract_code(pdf_path)

        state["code"] = result.get("code", "")
        state["code_snippets"] = result.get("code_snippets", [])

        print("✅ 代码提取完成")
    except Exception as e:
        print(f"❌ 代码提取失败: {e}")
        state["code"] = f"分析失败: {str(e)}"
        state["code_snippets"] = []

    return state


def assess_reproducibility(state: AgentState) -> AgentState:
    """
    Node: Assess the reproducibility of the paper.
    """
    pdf_path = state["pdf_path"]
    language = state.get("language", "zh")

    print("🔬 正在评估可复现性...")

    try:
        from ..extractors import ReproducibilityAnalyzer
        analyzer = ReproducibilityAnalyzer()

        result = analyzer.assess_reproducibility(pdf_path)

        state["reproducibility"] = result.get("reproducibility", "")
        state["reproducibility_score"] = result.get("reproducibility_score", 0.0)

        print("✅ 可复现性评估完成")
    except Exception as e:
        print(f"❌ 可复现性评估失败: {e}")
        state["reproducibility"] = f"分析失败: {str(e)}"
        state["reproducibility_score"] = 0.0

    return state