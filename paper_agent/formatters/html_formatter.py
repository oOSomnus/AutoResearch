"""
HTML Formatter - Generate HTML reports from analysis results.
"""
from typing import Dict, Any
import re

from .base_formatter import BaseFormatter


class HTMLFormatter(BaseFormatter):
    """Format analysis results as HTML."""

    def format_report(self, state: Dict[str, Any]) -> str:
        """
        Format the report as HTML.

        Args:
            state: Dictionary containing analysis results

        Returns:
            Formatted HTML report as string
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

        # Generate HTML
        html_parts = [
            self._get_html_header(title),
            self._get_body_start(),
            self._get_hero_section(title, source, paper_type),
            self._get_content_section(background, innovation, results, methodology, related_work, limitations),
            self._get_extractions_section(citations, figures, code, reproducibility),
            self._get_html_footer(),
        ]

        return "\n".join(html_parts)

    def _get_html_header(self, title: str) -> str:
        """Get HTML header with CSS and MathJax."""
        return f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._escape_html(title)} - 论文分析报告</title>
    <!-- MathJax for LaTeX rendering -->
    {self._get_mathjax_script() if self.config.get("include_latex", True) else ""}
    <style>
        {self._get_css_styles()}
    </style>
</head>"""

    def _get_mathjax_script(self) -> str:
        """Get MathJax script for LaTeX rendering."""
        return """<script>
    MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']]
        }
    };
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>"""

    def _get_css_styles(self) -> str:
        """Get CSS styles for the report."""
        return """* {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .hero h1 {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }

        .meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .meta-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            border-radius: 5px;
        }

        .meta-label {
            font-size: 0.85rem;
            opacity: 0.8;
        }

        .meta-value {
            font-weight: 600;
            margin-top: 5px;
        }

        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .section h2 {
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        .section h3 {
            color: #764ba2;
            margin: 20px 0 10px 0;
        }

        .section p {
            margin-bottom: 15px;
        }

        .section ul, .section ol {
            margin-left: 30px;
            margin-bottom: 15px;
        }

        .section li {
            margin-bottom: 8px;
        }

        .section code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }

        .section pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
        }

        .tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 1.8rem;
            }
            .container {
                padding: 20px 10px;
            }
        }
    </style>"""

    def _get_body_start(self) -> str:
        """Get body start tag."""
        return "<body>\n<div class=\"container\">\n"

    def _get_hero_section(self, title: str, source: str, paper_type: str) -> str:
        """Get hero section with paper info."""
        escaped_title = self._escape_html(title)
        escaped_source = self._escape_html(source)
        type_label = self._escape_html(self._get_paper_type_label(paper_type))

        return f"""<div class="hero">
            <h1>{escaped_title}</h1>
            <div class="meta">
                <div class="meta-item">
                    <div class="meta-label">来源</div>
                    <div class="meta-value">{escaped_source}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">类型</div>
                    <div class="meta-value"><span class="tag">{type_label}</span></div>
                </div>
            </div>
        </div>"""

    def _get_content_section(self, background: str, innovation: str, results: str,
                            methodology: str, related_work: str, limitations: str) -> str:
        """Get main content sections."""
        sections = []

        if background:
            sections.append(f"""<div class="section">
                <h2>一、背景&原因</h2>
                {self._markdown_to_html(background)}
            </div>""")

        if innovation:
            sections.append(f"""<div class="section">
                <h2>二、创新&核心理论</h2>
                {self._markdown_to_html(innovation)}
            </div>""")

        if results:
            sections.append(f"""<div class="section">
                <h2>三、结果</h2>
                {self._markdown_to_html(results)}
            </div>""")

        if methodology:
            sections.append(f"""<div class="section">
                <h2>四、实验方法</h2>
                {self._markdown_to_html(methodology)}
            </div>""")

        if related_work:
            sections.append(f"""<div class="section">
                <h2>相关工作</h2>
                {self._markdown_to_html(related_work)}
            </div>""")

        if limitations:
            sections.append(f"""<div class="section">
                <h2>局限性</h2>
                {self._markdown_to_html(limitations)}
            </div>""")

        return "\n".join(sections)

    def _get_extractions_section(self, citations: str, figures: str, code: str, reproducibility: str) -> str:
        """Get new extraction sections."""
        sections = []

        if citations:
            sections.append(f"""<div class="section">
                <h2>引用分析</h2>
                {self._markdown_to_html(citations)}
            </div>""")

        if figures:
            sections.append(f"""<div class="section">
                <h2>图表分析</h2>
                {self._markdown_to_html(figures)}
            </div>""")

        if code:
            sections.append(f"""<div class="section">
                <h2>代码片段</h2>
                {self._markdown_to_html(code)}
            </div>""")

        if reproducibility:
            sections.append(f"""<div class="section">
                <h2>可复现性评估</h2>
                {self._markdown_to_html(reproducibility)}
            </div>""")

        return "\n".join(sections)

    def _get_html_footer(self) -> str:
        """Get HTML footer."""
        return """</div>
<div class="footer">
    <p>Generated by AutoResearch Paper Agent</p>
</div>
</body>
</html>"""

    def _markdown_to_html(self, markdown: str) -> str:
        """
        Convert simple Markdown to HTML.

        This is a basic converter. For more complex needs, consider using
        a library like markdown or mistletoe.
        """
        if not markdown:
            return ""

        html = markdown

        # Headers (### -> h3, etc.)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Code blocks
        html = re.sub(r'```(\w+)?\n([\s\S]+?)```', r'<pre><code class="\1">\2</code></pre>', html)

        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

        # Unordered lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', html)

        # Ordered lists
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>\n?)+', r'<ol>\g<0></ol>', html)

        # Paragraphs (lines that aren't already wrapped)
        html = re.sub(r'\n\n', r'</p><p>', html)
        html = f"<p>{html}</p>"

        # Clean up empty paragraphs
        html = re.sub(r'<p>\s*</p>', '', html)
        html = re.sub(r'<p>(<h[23]|<ul>|<ol>)', r'\1', html)
        html = re.sub(r'(</h[23]>|</ul>|</ol>)</p>', r'\1', html)

        # Clean up list nesting
        html = re.sub(r'<ul>\s*<ul>', '<ul>', html)
        html = re.sub(r'</ul>\s*</ul>', '</ul>', html)
        html = re.sub(r'<ol>\s*<ol>', '<ol>', html)
        html = re.sub(r'</ol>\s*</ol>', '</ol>', html)

        return html.strip()

    def _escape_html(self, text: str) -> str:
        """Escape special HTML characters."""
        if not text:
            return ""
        html_special = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
        }
        for char, escaped in html_special.items():
            text = text.replace(char, escaped)
        return text