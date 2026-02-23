"""
Input nodes for PDF fetching and content extraction.

Contains nodes that handle the initial processing of paper data.
"""
import os

from .base import AgentState, get_llm
from ..pdf_reader import get_pdf_path, extract_title
from ..prompts import get_paper_type_detection_prompt


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
    from ..pdf_reader import extract_pdf_text
    from ..chunking import extract_chapters

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