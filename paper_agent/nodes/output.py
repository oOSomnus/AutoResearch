"""
Output nodes for report generation and saving.

Contains nodes that generate the final report in various formats
and save it to disk.
"""
import hashlib
import os

from .base import AgentState
from ..prompts import get_report_prompt


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
        from ..formatters import get_formatter, get_bilingual_formatter

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
    from ..pdf_reader import is_url

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