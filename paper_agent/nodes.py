"""
Node Functions - Individual processing functions for the LangGraph workflow.
"""
import os
import hashlib
from typing import TypedDict, List, Optional

from langchain_openai import ChatOpenAI

from .pdf_reader import get_pdf_path, extract_pdf_text, extract_title, is_url
from .prompts import (
    get_background_prompt,
    get_innovation_prompt,
    get_results_prompt,
    get_report_prompt,
    get_paper_type_detection_prompt,
    get_methodology_prompt,
    get_related_work_prompt,
    get_limitations_prompt
)
from .chunking import extract_chapters, get_relevant_content_for_analysis


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


def fetch_pdf(state: AgentState) -> AgentState:
    """
    Node 1: Handle PDF fetching/downloading.
    Takes a file path or URL and ensures the file is available locally.
    """
    source = state.get("source", "")
    work_dir = os.getcwd()

    print(f"📥 正在获取PDF: {source}")

    try:
        pdf_path = get_pdf_path(source, work_dir)
        print(f"✅ PDF已准备好: {pdf_path}")
    except Exception as e:
        print(f"❌ 获取PDF失败: {e}")
        raise

    # Extract title from PDF
    title = extract_title(pdf_path)
    print(f"📄 论文标题: {title if title else '无法提取'}")

    state["pdf_path"] = pdf_path
    state["title"] = title or "未知标题"
    return state


def extract_content(state: AgentState) -> AgentState:
    """
    Node 2: Extract text content from PDF and extract chapters.
    """
    pdf_path = state["pdf_path"]

    print("📖 正在提取PDF内容和章节...")

    try:
        # Extract full content
        content = extract_pdf_text(pdf_path)

        # Extract chapters for intelligent chunking
        chapters = extract_chapters(pdf_path)

        print(f"✅ 提取了 {len(content)} 个字符")
        print(f"✅ 识别了 {len(chapters)} 个章节:")
        for chapter in chapters:
            chapter_info = f"  - {chapter.title}"
            if chapter.chapter_type:
                chapter_info += f" [{chapter.chapter_type}]"
            if chapter.page_range:
                chapter_info += f" (页码 {chapter.page_range[0]}-{chapter.page_range[1]})"
            print(chapter_info)

    except Exception as e:
        print(f"❌ 提取内容失败: {e}")
        content = ""
        chapters = []

    state["content"] = content
    state["chapters"] = chapters
    return state


def detect_paper_type(state: AgentState) -> AgentState:
    """
    Node 3: Detect paper type using LLM based on title and content.
    """
    title = state["title"]
    content = state["content"]

    print("🔬 正在检测论文类型...")

    try:
        llm = get_llm()
        prompt = get_paper_type_detection_prompt(title, content)
        response = llm.invoke(prompt)

        # Handle different response formats
        paper_type = None
        if hasattr(response, 'content'):
            paper_type = str(response.content).strip().lower()
        elif isinstance(response, str):
            paper_type = response.strip().lower()
        elif hasattr(response, 'to_string'):
            paper_type = response.to_string().strip().lower()

        # Validate and normalize the paper type
        valid_types = ['survey', 'experimental', 'theoretical', 'unknown']
        if not paper_type or paper_type not in valid_types:
            paper_type = 'unknown'

        print(f"✅ 论文类型检测完成: {paper_type}")
    except Exception as e:
        print(f"❌ 论文类型检测失败: {e}")
        paper_type = 'unknown'

    state["paper_type"] = paper_type
    return state


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

        # Use chapter-based content if available
        if chapters:
            relevant_content = get_relevant_content_for_analysis(chapters, 'background')
            if relevant_content:
                content = relevant_content

        prompt = get_background_prompt(content)
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
    """
    content = state["content"]

    print("💡 正在分析创新&核心理论...")

    try:
        llm = get_llm()
        prompt = get_innovation_prompt(content)
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
    Uses chapter-based content for more focused analysis.
    """
    chapters = state.get("chapters", [])
    content = state.get("content", "")

    print("📊 正在分析结果...")

    try:
        llm = get_llm()

        # Use chapter-based content if available
        if chapters:
            relevant_content = get_relevant_content_for_analysis(chapters, 'results')
            if relevant_content:
                content = relevant_content

        prompt = get_results_prompt(content)
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


def generate_report(state: AgentState) -> AgentState:
    """
    Node: Generate the final report.
    Dynamically generates report based on available analysis results.
    Uses formatters based on output_format configuration.
    """
    print("📝 正在生成报告...")

    # Get output configuration
    output_format = state.get("output_format", "markdown")
    language = state.get("language", "zh")
    detail_level = state.get("detail_level", "standard")

    # Get all analysis results
    title = state.get("title", "")
    source = state.get("source", "")
    paper_type = state.get("paper_type", "unknown")
    background = state.get("background", "")
    innovation = state.get("innovation", "")
    results = state.get("results", "")
    methodology = state.get("methodology", "")
    related_work = state.get("related_work", "")
    limitations = state.get("limitations", "")

    # New extraction sections
    citations = state.get("citations", "")
    figures = state.get("figures", "")
    code = state.get("code", "")
    reproducibility = state.get("reproducibility", "")

    try:
        # Import formatters
        from .formatters import get_formatter, get_bilingual_formatter

        # Get the appropriate formatter
        config = {
            "language": language,
            "detail_level": detail_level,
            "include_latex": True
        }

        formatter = get_bilingual_formatter(output_format, language, config)

        # Convert state to dict for formatter
        state_dict = {
            "title": title,
            "source": source,
            "paper_type": paper_type,
            "background": background,
            "innovation": innovation,
            "results": results,
            "methodology": methodology,
            "related_work": related_work,
            "limitations": limitations,
            "citations": citations,
            "figures": figures,
            "code": code,
            "reproducibility": reproducibility,
            "citations_list": state.get("citations_list", []),
            "figures_list": state.get("figures_list", []),
            "code_snippets": state.get("code_snippets", []),
            "reproducibility_score": state.get("reproducibility_score", 0.0),
        }

        # Generate report
        report = formatter.format_report(state_dict)

        print("✅ 报告生成完成")
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        # Fallback: generate a simple markdown report
        sections = [f"# 论文分析报告\n\n## 原始信息\n- 来源: {source}\n- 标题: {title}\n- 类型: {paper_type}"]
        sections.append(f"\n## 一、背景&原因\n{background}")
        sections.append(f"\n## 二、创新&核心理论\n{innovation}")
        sections.append(f"\n## 三、结果\n{results}")

        if methodology:
            sections.append(f"\n## 四、实验方法\n{methodology}")
        if related_work:
            sections.append(f"\n## 四、相关工作\n{related_work}")
        if limitations:
            sections.append(f"\n## 四、局限性\n{limitations}")

        report = "\n".join(sections)

    state["report"] = report
    return state


def save_report(state: AgentState) -> AgentState:
    """
    Node: Save the report to a file.
    Supports multiple output formats based on configuration.
    """
    source = state.get("source", "")
    title = state.get("title", "")
    report = state.get("report", "")
    output_format = state.get("output_format", "markdown")

    # Determine file extension based on format
    extension_map = {
        "markdown": ".md",
        "html": ".html",
        "pdf": ".pdf",
        "json": ".json"
    }
    extension = extension_map.get(output_format, ".md")

    # Generate filename based on source or title
    if is_url(source):
        filename = hashlib.md5(source.encode()).hexdigest()[:8] + f"_report{extension}"
    else:
        # Use the base filename from path
        base_name = os.path.basename(source)
        base_name = os.path.splitext(base_name)[0]
        filename = f"{base_name}_report{extension}"

    # Save to current working directory
    report_path = os.path.join(os.getcwd(), filename)

    print(f"💾 正在保存报告到: {report_path}")

    try:
        # For PDF format, the report is already the file path
        if output_format == "pdf" and os.path.exists(report):
            print(f"✅ PDF报告已生成: {report}")
        else:
            # Write content to file
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"✅ 报告已保存: {report_path}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        raise

    return state


# Phase 4: New extraction nodes

def extract_citations(state: AgentState) -> AgentState:
    """
    Node: Extract and analyze citations from the paper.
    """
    pdf_path = state["pdf_path"]
    language = state.get("language", "zh")

    print("📚 正在提取引用分析...")

    try:
        from .extractors import CitationExtractor
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
        from .extractors import FigureExtractor
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
        from .extractors import CodeExtractor
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
        from .extractors import ReproducibilityAnalyzer
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