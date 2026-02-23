"""
JSON Formatter - Generate structured JSON reports from analysis results.
"""
import json
from typing import Dict, Any
from datetime import datetime

from .base_formatter import BaseFormatter


class JSONFormatter(BaseFormatter):
    """Format analysis results as structured JSON."""

    def format_report(self, state: Dict[str, Any]) -> str:
        """
        Format the report as JSON.

        Args:
            state: Dictionary containing analysis results

        Returns:
            Formatted JSON report as string
        """
        # Build structured output
        output = {
            "metadata": self._get_metadata(state),
            "analysis": self._get_analysis_sections(state),
            "extractions": self._get_extractions(state),
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

        # Pretty print JSON
        return json.dumps(output, indent=2, ensure_ascii=False)

    def _get_metadata(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from state."""
        return {
            "title": self._get_field(state, "title", ""),
            "source": self._get_field(state, "source", ""),
            "paper_type": self._get_field(state, "paper_type", "unknown"),
            "language": self.config.get("language", "zh"),
            "detail_level": self.config.get("detail_level", "standard")
        }

    def _get_analysis_sections(self, state: Dict[str, Any]) -> Dict[str, str]:
        """Extract main analysis sections."""
        return {
            "background": self._clean_content(self._get_field(state, "background", "")),
            "innovation": self._clean_content(self._get_field(state, "innovation", "")),
            "results": self._clean_content(self._get_field(state, "results", "")),
            "methodology": self._clean_content(self._get_field(state, "methodology", "")),
            "related_work": self._clean_content(self._get_field(state, "related_work", "")),
            "limitations": self._clean_content(self._get_field(state, "limitations", ""))
        }

    def _get_extractions(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional analysis dimensions."""
        extractions = {}

        # Text extractions
        citations = self._clean_content(self._get_field(state, "citations", ""))
        if citations:
            extractions["citations"] = citations

        figures = self._clean_content(self._get_field(state, "figures", ""))
        if figures:
            extractions["figures"] = figures

        code = self._clean_content(self._get_field(state, "code", ""))
        if code:
            extractions["code"] = code

        reproducibility = self._clean_content(self._get_field(state, "reproducibility", ""))
        if reproducibility:
            extractions["reproducibility"] = reproducibility

        # Structured extractions (if available)
        if "citations_list" in state and state["citations_list"]:
            extractions["citations_list"] = state["citations_list"]

        if "figures_list" in state and state["figures_list"]:
            extractions["figures_list"] = [
                {
                    "page_num": f.get("page_num"),
                    "caption": f.get("caption"),
                    "figure_type": f.get("figure_type"),
                    "description": f.get("description")
                }
                for f in state["figures_list"]
            ]

        if "code_snippets" in state and state["code_snippets"]:
            extractions["code_snippets"] = [
                {
                    "page_num": c.get("page_num"),
                    "language": c.get("language"),
                    "code": c.get("code"),
                    "description": c.get("description")
                }
                for c in state["code_snippets"]
            ]

        if "reproducibility_score" in state:
            extractions["reproducibility_score"] = state["reproducibility_score"]

        return extractions