"""
Figure Extractor - Extract and analyze figures and tables from papers.
"""
import re
from typing import List, Dict, Any

from ..types import FigureInfo, TableInfo
from ..pdf_reader import extract_pdf_text


class FigureExtractor:
    """Extract and analyze figures and tables from paper content."""

    def __init__(self):
        """Initialize the figure extractor."""
        # Figure caption patterns
        self.figure_patterns = [
            r'Figure\s+\d+[:\.\-]\s*(.+)',
            r'图\s+\d+[:\.\-]\s*(.+)',
            r'Fig\.\s*\d+[:\.\-]\s*(.+)',
        ]

        # Table caption patterns
        self.table_patterns = [
            r'Table\s+\d+[:\.\-]\s*(.+)',
            r'表\s+\d+[:\.\-]\s*(.+)',
            r'Tab\.\s*\d+[:\.\-]\s*(.+)',
        ]

    def extract_figures(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract figures from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted figures and analysis
        """
        content = extract_pdf_text(pdf_path)

        # Find figures and tables
        figures = self._find_figures(content)
        tables = self._find_tables(content)

        # Generate analysis text
        analysis_text = self._generate_analysis_text(figures, tables)

        return {
            "figures": analysis_text,
            "figures_list": figures,
            "tables_list": tables,
            "figure_count": len(figures),
            "table_count": len(tables)
        }

    def _find_figures(self, content: str) -> List[FigureInfo]:
        """Find figures in the content."""
        figures = []

        for pattern in self.figure_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                caption = match.group(1).strip()

                # Determine figure type
                figure_type = self._determine_figure_type(caption)

                # Extract description (text around the figure)
                start = max(0, match.start() - 200)
                end = min(len(content), match.end() + 300)
                description = content[start:end].strip()

                figures.append(FigureInfo(
                    page_num=0,  # Would need PDF parsing for accurate page numbers
                    caption=caption,
                    figure_type=figure_type,
                    description=description[:200]
                ))

        return figures

    def _find_tables(self, content: str) -> List[TableInfo]:
        """Find tables in the content."""
        tables = []

        for pattern in self.table_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                caption = match.group(1).strip()

                # Try to extract table content
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 500)
                content_section = content[start:end]

                # Extract headers (look for tab-separated or pipe-separated text)
                lines = content_section.split('\n')
                headers = []
                table_content = ""

                if len(lines) > 2:
                    # Second line might be headers
                    potential_headers = re.split(r'[|\t]+', lines[1].strip())
                    headers = [h.strip() for h in potential_headers if h.strip()][:10]

                    # Rest is table content
                    table_content = '\n'.join(lines[2:6])

                tables.append(TableInfo(
                    page_num=0,
                    caption=caption,
                    content=table_content[:200],
                    headers=headers,
                    row_count=0,
                    col_count=len(headers)
                ))

        return tables

    def _determine_figure_type(self, caption: str) -> str:
        """Determine the type of figure based on caption."""
        caption_lower = caption.lower()

        if any(kw in caption_lower for kw in ["plot", "graph", "curve", "趋势图", "曲线", "折线"]):
            return "graph"
        elif any(kw in caption_lower for kw in ["chart", "bar", "柱状图", "条形"]):
            return "chart"
        elif any(kw in caption_lower for kw in ["diagram", "architecture", "结构图", "架构"]):
            return "diagram"
        elif any(kw in caption_lower for kw in ["image", "photo", "图片", "照片"]):
            return "image"
        else:
            return "figure"

    def _generate_analysis_text(self, figures: List[FigureInfo],
                                tables: List[TableInfo]) -> str:
        """Generate analysis text from figures and tables."""
        parts = ["## 图表分析"]

        if not figures and not tables:
            parts.append("\n未在论文中找到显著的图表信息。")
            return "\n".join(parts)

        # Figure analysis
        if figures:
            parts.append(f"\n### 图表 ({len(figures)} 个)")

            # Group by type
            figure_types = {}
            for fig in figures:
                f_type = fig.figure_type
                figure_types[f_type] = figure_types.get(f_type, 0) + 1

            type_names = {
                "graph": "趋势图",
                "chart": "柱状图/图表",
                "diagram": "结构图",
                "image": "图片",
                "figure": "其他图表"
            }

            for f_type, count in figure_types.items():
                parts.append(f"- **{type_names.get(f_type, f_type)}**: {count} 个")

            # List key figures
            if figures:
                parts.append("\n**主要图表：**")
                for fig in figures[:5]:
                    parts.append(f"- {fig.caption}")

        # Table analysis
        if tables:
            parts.append(f"\n### 数据表 ({len(tables)} 个)")

            parts.append("\n**主要数据表：**")
            for table in tables[:5]:
                parts.append(f"- {table.caption}")
                if table.headers:
                    parts.append(f"  列: {', '.join(table.headers[:5])}")

        return "\n".join(parts)