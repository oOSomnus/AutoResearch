"""
Markdown Formatter - Generate Markdown reports from analysis results.
"""
from typing import Dict, Any

from .base_formatter import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """Format analysis results as Markdown."""

    def format_report(self, state: Dict[str, Any]) -> str:
        """
        Format the report as Markdown.

        Args:
            state: Dictionary containing analysis results

        Returns:
            Formatted Markdown report as string
        """
        title = self._get_field(state, "title", "未知标题")
        source = self._get_field(state, "source", "")
        paper_type = self._get_field(state, "paper_type", "unknown")

        # Get all analysis sections
        background = self._clean_content(self._get_field(state, "background", ""))
        innovation = self._clean_content(self._get_field(state, "innovation", ""))
        results = self._clean_content(self._get_field(state, "results", ""))
        methodology = self._clean_content(self._get_field(state, "methodology", ""))
        related_work = self._clean_content(self._get_field(state, "related_work", ""))
        limitations = self._clean_content(self._get_field(state, "limitations", ""))

        # New extraction sections
        citations = self._clean_content(self._get_field(state, "citations", ""))
        figures = self._clean_content(self._get_field(state, "figures", ""))
        code = self._clean_content(self._get_field(state, "code", ""))
        reproducibility = self._clean_content(self._get_field(state, "reproducibility", ""))

        # Build report sections
        sections = []
        sections.append(f"# 论文分析报告\n")
        sections.append("## 原始信息\n")
        sections.append(f"- **来源**: {source}\n")
        sections.append(f"- **标题**: {title}\n")
        sections.append(f"- **类型**: {self._get_paper_type_label(paper_type)}\n")

        # Main analysis sections
        sections.append(f"\n## 一、背景&原因\n{background}\n")
        sections.append(f"\n## 二、创新&核心理论\n{innovation}\n")
        sections.append(f"\n## 三、结果\n{results}\n")

        # Conditional sections based on paper type and available content
        section_number = 4
        if methodology:
            sections.append(f"\n## 四、实验方法\n{methodology}\n")
            section_number += 1

        if related_work:
            sections.append(f"\n## {section_number}、相关工作\n{related_work}\n")
            section_number += 1

        if limitations:
            sections.append(f"\n## {section_number}、局限性\n{limitations}\n")
            section_number += 1

        # New extraction sections (if enabled)
        if citations:
            sections.append(f"\n## {section_number}、引用分析\n{citations}\n")
            section_number += 1

        if figures:
            sections.append(f"\n## {section_number}、图表分析\n{figures}\n")
            section_number += 1

        if code:
            sections.append(f"\n## {section_number}、代码片段\n{code}\n")
            section_number += 1

        if reproducibility:
            sections.append(f"\n## {section_number}、可复现性评估\n{reproducibility}\n")

        return "\n".join(sections)