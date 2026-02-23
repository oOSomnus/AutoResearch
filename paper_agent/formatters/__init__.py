"""
Formatters Package - Report output formatters for the paper agent.

This package provides various output formats for paper analysis reports:
- Markdown (default)
- HTML (with MathJax support)
- PDF (using weasyprint)
- JSON (structured data)
"""

from .base_formatter import BaseFormatter
from .markdown_formatter import MarkdownFormatter
from .html_formatter import HTMLFormatter
from .json_formatter import JSONFormatter
from .bilingual_formatter import BilingualFormatter

# Optional imports for features that require additional dependencies
try:
    from .pdf_formatter import PDFFormatter
    PDFFORMATTER_AVAILABLE = True
except ImportError:
    PDFFORMATTER_AVAILABLE = False

try:
    from .chart_generator import ChartGenerator, ChartData
    CHART_GENERATOR_AVAILABLE = True
except ImportError:
    CHART_GENERATOR_AVAILABLE = False

__all__ = [
    "BaseFormatter",
    "MarkdownFormatter",
    "HTMLFormatter",
    "JSONFormatter",
    "BilingualFormatter",
]

# Add optional items if available
if PDFFORMATTER_AVAILABLE:
    __all__.append("PDFFormatter")
if CHART_GENERATOR_AVAILABLE:
    __all__.extend(["ChartGenerator", "ChartData"])


def get_formatter(output_format: str, language: str = "zh",
                 config: dict | None = None) -> BaseFormatter:
    """
    Factory function to get a formatter instance.

    Args:
        output_format: Output format (markdown, html, pdf, json)
        language: Target language (zh, en)
        config: Optional configuration dictionary

    Returns:
        Configured formatter instance

    Raises:
        ValueError: If output format is not recognized
        ImportError: If required dependencies are missing
    """
    if config is None:
        config = {}
    config["language"] = language

    if output_format == "markdown":
        return MarkdownFormatter(config)
    elif output_format == "html":
        return HTMLFormatter(config)
    elif output_format == "pdf":
        if not PDFFORMATTER_AVAILABLE:
            raise ImportError(
                "weasyprint is required for PDF output. "
                "Install it with: pip install weasyprint>=60.0"
            )
        from .pdf_formatter import PDFFormatter
        return PDFFormatter(config)
    elif output_format == "json":
        return JSONFormatter(config)
    else:
        raise ValueError(f"Unknown output format: {output_format}")


def get_bilingual_formatter(output_format: str, language: str = "zh",
                            config: dict | None = None) -> BaseFormatter:
    """
    Factory function to get a bilingual formatter instance.

    Args:
        output_format: Output format (markdown, html, pdf, json)
        language: Target language (zh, en)
        config: Optional configuration dictionary

    Returns:
        Configured bilingual formatter instance
    """
    return BilingualFormatter.create_formatter(output_format, language, config)