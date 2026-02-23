"""
Base Formatter - Abstract base class for all report formatters.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseFormatter(ABC):
    """Abstract base class for report formatters."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the formatter.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    def format_report(self, state: Dict[str, Any]) -> str:
        """
        Format the report from the given state.

        Args:
            state: Dictionary containing analysis results

        Returns:
            Formatted report as string
        """
        pass

    def _get_field(self, state: Dict[str, Any], key: str, default: str = "") -> str:
        """Get a field from state with default value."""
        return state.get(key, default)

    def _get_paper_type_label(self, paper_type: str) -> str:
        """Get human-readable label for paper type."""
        labels = {
            "survey": "综述",
            "experimental": "实验",
            "theoretical": "理论",
            "unknown": "未知"
        }
        return labels.get(paper_type, paper_type)

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        latex_special = {
            "&": "\\&",
            "%": "\\%",
            "$": "\\$",
            "#": "\\#",
            "_": "\\_",
            "{": "\\{",
            "}": "\\}",
            "~": "\\textasciitilde{}",
            "^": "\\textasciicircum{}",
        }
        # Only escape if not already a LaTeX command
        result = text
        for char, escaped in latex_special.items():
            # Simple heuristic: don't escape if preceded by backslash
            result = result.replace(f"\\{char}", char)  # Unescape first
            result = result.replace(char, escaped)
        return result

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        if not content:
            return ""
        # Remove excessive whitespace
        import re
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        return content.strip()