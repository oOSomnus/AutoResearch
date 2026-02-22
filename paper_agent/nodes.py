"""
Node Functions - Individual processing functions for the LangGraph workflow.
"""
import os
import hashlib
from typing import TypedDict

from langchain_openai import ChatOpenAI

from .pdf_reader import get_pdf_path, extract_pdf_text, extract_title, is_url
from .prompts import (
    get_background_prompt,
    get_innovation_prompt,
    get_results_prompt,
    get_report_prompt
)


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
    Node 2: Extract text content from PDF.
    """
    pdf_path = state["pdf_path"]

    print("📖 正在提取PDF内容...")

    try:
        content = extract_pdf_text(pdf_path)
        # Limit content length to avoid token limits
        max_chars = 30000  # Approx 10k tokens
        if len(content) > max_chars:
            content = content[:max_chars]
            print(f"⚠️  内容过长，截取前 {max_chars} 字符")

        print(f"✅ 提取了 {len(content)} 个字符")
    except Exception as e:
        print(f"❌ 提取内容失败: {e}")
        raise

    state["content"] = content
    return state


def analyze_background(state: AgentState) -> AgentState:
    """
    Node 3: Analyze the background and motivation of the research.
    """
    content = state["content"]

    print("🔍 正在分析背景&原因...")

    try:
        llm = get_llm()
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
    Node 5: Analyze the results and conclusions of the research.
    """
    content = state["content"]

    print("📊 正在分析结果...")

    try:
        llm = get_llm()
        prompt = get_results_prompt(content)
        response = llm.invoke(prompt)
        results = response.content.strip()

        print("✅ 结果分析完成")
    except Exception as e:
        print(f"❌ 结果分析失败: {e}")
        results = f"分析失败: {str(e)}"

    state["results"] = results
    return state


def generate_report(state: AgentState) -> AgentState:
    """
    Node 6: Generate the final Markdown report.
    """
    title = state["title"]
    source = state["source"]
    background = state["background"]
    innovation = state["innovation"]
    results = state["results"]

    print("📝 正在生成报告...")

    try:
        llm = get_llm()
        prompt = get_report_prompt(title, source, background, innovation, results)
        response = llm.invoke(prompt)
        report = response.content.strip()

        print("✅ 报告生成完成")
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        # Fallback: generate a simple report without LLM
        report = f"""# 论文分析报告

## 原始信息
- 来源: {source}
- 标题: {title}

## 一、背景&原因
{background}

## 二、创新&核心理论
{innovation}

## 三、结果
{results}
"""

    state["report"] = report
    return state


def save_report(state: AgentState) -> AgentState:
    """
    Node 7: Save the report to a Markdown file.
    """
    source = state["source"]
    title = state["title"]
    report = state["report"]

    # Generate filename based on source or title
    if is_url(source):
        filename = hashlib.md5(source.encode()).hexdigest()[:8] + "_report.md"
    else:
        # Use the base filename from path
        base_name = os.path.basename(source)
        filename = os.path.splitext(base_name)[0] + "_report.md"

    # Save to current working directory
    report_path = os.path.join(os.getcwd(), filename)

    print(f"💾 正在保存报告到: {report_path}")

    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ 报告已保存: {report_path}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        raise

    return state