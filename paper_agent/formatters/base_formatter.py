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
        # Normalize markdown list indentation
        content = self._normalize_markdown_lists(content)
        return content.strip()

    def _normalize_markdown_lists(self, content: str) -> str:
        """
        Normalize markdown list indentation to proper standard (2+ spaces per nesting level).
        This fixes issues where nested list items don't have sufficient indentation.
        """
        import re

        lines = content.split('\n')
        result_lines = []

        # Pattern for list items: optional leading spaces + bullet/number marker
        list_pattern = re.compile(r'^(\s*)([-*+]|\d+[.)])\s+(.*)$')

        # Track the actual indentation levels we've seen, in order
        # Each entry is the indentation value that represents a nesting level
        indent_levels = []  # Stack of actual indentation values from input

        for line in lines:
            match = list_pattern.match(line)

            if match:
                # This is a list item
                indent_str = match.group(1)
                list_marker = match.group(2)
                item_content = match.group(3)

                current_indent = len(indent_str)

                # Determine where this item fits in the nesting hierarchy
                # Pop from stack until we find a level that is strictly less than current
                while indent_levels and current_indent <= indent_levels[-1]:
                    indent_levels.pop()

                # Now check if this is a new nesting level
                if not indent_levels or current_indent > indent_levels[-1]:
                    # This is a new, deeper nesting level
                    indent_levels.append(current_indent)

                # Nesting level is the size of the stack
                nesting_level = len(indent_levels) - 1  # 0-indexed

                # Proper indentation: 0 spaces for level 0, 2 for level 1, 4 for level 2, etc.
                proper_indent = 2 * nesting_level

                # Rebuild line with correct indentation
                line = ' ' * proper_indent + list_marker + ' ' + item_content

            else:
                # Non-list line
                stripped = line.strip()
                # Reset stack for blank lines or headers
                if not stripped or stripped.startswith('#'):
                    indent_levels = []

            result_lines.append(line)

        return '\n'.join(result_lines)