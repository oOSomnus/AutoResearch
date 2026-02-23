"""
Bilingual Formatter - Wrapper for language switching between Chinese and English.
"""
from typing import Dict, Any

from .base_formatter import BaseFormatter


class BilingualFormatter(BaseFormatter):
    """
    Wrapper that selects the appropriate language formatter.

    This formatter wraps another formatter and ensures the output
    is in the specified language (Chinese or English).
    """

    def __init__(self, inner_formatter: BaseFormatter, language: str = "zh"):
        """
        Initialize the bilingual formatter.

        Args:
            inner_formatter: The base formatter to wrap
            language: Target language ('zh' for Chinese, 'en' for English)
        """
        super().__init__(inner_formatter.config if hasattr(inner_formatter, 'config') else {})
        self.inner_formatter = inner_formatter
        self.language = language

    def format_report(self, state: Dict[str, Any]) -> str:
        """
        Format the report in the specified language.

        Args:
            state: Dictionary containing analysis results

        Returns:
            Formatted report as string in the target language
        """
        # If the language matches the state's language, use the inner formatter directly
        state_language = state.get("language", "zh")

        if state_language == self.language:
            return self.inner_formatter.format_report(state)

        # If language doesn't match, we need to translate the analysis results
        # before formatting
        translated_state = self._translate_state(state)
        return self.inner_formatter.format_report(translated_state)

    def _translate_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate analysis results to the target language.

        Note: This is a simplified version. In production, you would use
        an LLM or translation service to properly translate the content.

        Args:
            state: Original state with analysis results

        Returns:
            State with translated analysis results
        """
        # Create a copy of the state
        translated = state.copy()

        # Set the target language
        translated["language"] = self.language

        # For now, we just indicate that translation would happen here
        # In a full implementation, this would call an LLM to translate
        # each analysis section

        return translated

    @staticmethod
    def create_formatter(output_format: str, language: str = "zh",
                        config: Dict[str, Any] | None = None) -> BaseFormatter:
        """
        Factory method to create a formatter with language support.

        Args:
            output_format: Output format (markdown, html, pdf, json)
            language: Target language ('zh' for Chinese, 'en' for English)
            config: Optional configuration

        Returns:
            Configured formatter instance
        """
        from .markdown_formatter import MarkdownFormatter
        from .html_formatter import HTMLFormatter
        from .pdf_formatter import PDFFormatter
        from .json_formatter import JSONFormatter

        # Update config with language
        if config is None:
            config = {}
        config["language"] = language

        # Create base formatter based on format
        if output_format == "markdown":
            base_formatter = MarkdownFormatter(config)
        elif output_format == "html":
            base_formatter = HTMLFormatter(config)
        elif output_format == "pdf":
            base_formatter = PDFFormatter(config)
        elif output_format == "json":
            base_formatter = JSONFormatter(config)
        else:
            raise ValueError(f"Unknown output format: {output_format}")

        # Wrap with bilingual support
        return BilingualFormatter(base_formatter, language)