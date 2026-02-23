"""
PDF Formatter - Generate PDF reports from analysis results.
"""
from typing import Dict, Any
from pathlib import Path

from .base_formatter import BaseFormatter
from .html_formatter import HTMLFormatter


class PDFFormatter(BaseFormatter):
    """Format analysis results as PDF using weasyprint."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self.html_formatter = HTMLFormatter(config)

    def format_report(self, state: Dict[str, Any]) -> str:
        """
        Format the report as PDF.

        Args:
            state: Dictionary containing analysis results

        Returns:
            Path to the generated PDF file
        """
        # First generate HTML
        html_content = self.html_formatter.format_report(state)

        # Generate filename
        source = self._get_field(state, "source", "")
        title = self._get_field(state, "title", "report")

        filename = self._generate_filename(source, title)

        # Convert HTML to PDF
        try:
            from weasyprint import HTML

            html = HTML(string=html_content, base_url="")
            html.write_pdf(filename)

            return filename
        except ImportError:
            raise ImportError(
                "weasyprint is required for PDF output. "
                "Install it with: pip install weasyprint>=60.0"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate PDF: {e}")

    def _generate_filename(self, source: str, title: str) -> str:
        """Generate filename for PDF output."""
        import os
        import hashlib

        # Clean title for filename
        clean_title = "".join(c for c in title if c.isalnum() or c in " -_")[:50]

        if source.startswith(("http://", "https://")):
            # Use hash for URL sources
            hash_part = hashlib.md5(source.encode()).hexdigest()[:8]
            filename = f"{hash_part}_report.pdf"
        else:
            # Use base filename for local sources
            base_name = os.path.basename(source)
            base_name = os.path.splitext(base_name)[0]
            filename = f"{base_name}_report.pdf"

        return os.path.join(os.getcwd(), filename)