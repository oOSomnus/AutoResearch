"""
Reproducibility Analyzer - Assess paper reproducibility.
"""
import re
from typing import List, Dict, Any

from ..types import ReproducibilityAssessment
from ..pdf_reader import extract_pdf_text


class ReproducibilityAnalyzer:
    """Analyze and assess paper reproducibility."""

    def __init__(self):
        """Initialize the reproducibility analyzer."""
        # Keywords indicating code availability
        self.code_keywords = [
            "code", "github", "github.com", "source code", "implementation",
            "代码", "源码", "实现", "github"
        ]

        # Keywords indicating data availability
        self.data_keywords = [
            "dataset", "data available", "public dataset", "open data",
            "数据集", "数据公开", "公开数据"
        ]

        # Keywords indicating environment specification
        self.env_keywords = [
            "environment", "requirements", "dependencies", "docker",
            "环境", "依赖", "配置", "容器"
        ]

        # Keywords indicating metrics
        self.metrics_keywords = [
            "accuracy", "precision", "recall", "f1", "roc", "auc",
            "指标", "准确率", "精确率", "召回率"
        ]

    def assess_reproducibility(self, pdf_path: str) -> Dict[str, Any]:
        """
        Assess the reproducibility of a paper.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with reproducibility assessment
        """
        content = extract_pdf_text(pdf_path).lower()

        # Check each criterion
        code_available = self._check_criterion(content, self.code_keywords)
        data_available = self._check_criterion(content, self.data_keywords)
        environment_specified = self._check_criterion(content, self.env_keywords)
        metrics_reported = self._check_criterion(content, self.metrics_keywords)

        # Calculate overall score (simple weighted average)
        score = self._calculate_score(
            code_available, data_available, environment_specified, metrics_reported
        )

        # Generate notes and suggestions
        notes = self._generate_notes(
            code_available, data_available, environment_specified, metrics_reported
        )

        suggestions = self._generate_suggestions(
            code_available, data_available, environment_specified, metrics_reported
        )

        assessment = ReproducibilityAssessment(
            score=score,
            code_available=code_available,
            data_available=data_available,
            environment_specified=environment_specified,
            metrics_reported=metrics_reported,
            results_reproducible=self._assess_results_reproducibility(content),
            notes=notes,
            suggestions=suggestions
        )

        # Generate analysis text
        analysis_text = self._generate_analysis_text(assessment)

        return {
            "reproducibility": analysis_text,
            "reproducibility_score": score,
            "assessment": assessment
        }

    def _check_criterion(self, content: str, keywords: List[str]) -> bool:
        """Check if any keyword is present in content."""
        content_lower = content.lower()
        for keyword in keywords:
            if keyword.lower() in content_lower:
                return True
        return False

    def _calculate_score(self, code: bool, data: bool, env: bool, metrics: bool) -> float:
        """Calculate overall reproducibility score."""
        # Weight: code (0.3), data (0.3), env (0.2), metrics (0.2)
        score = 0.0
        if code:
            score += 0.3
        if data:
            score += 0.3
        if env:
            score += 0.2
        if metrics:
            score += 0.2

        return score

    def _assess_results_reproducibility(self, content: str) -> bool:
        """Assess if results are reproducible based on content."""
        # Look for statistical information, error bars, confidence intervals
        reproducibility_indicators = [
            r"±\s*\d+",  # ± symbol with numbers
            r"confidence", r"ci", r"std", r"std\.", r"error bar",
            "置信区间", "标准差", "误差"
        ]

        for indicator in reproducibility_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True

        return False

    def _generate_notes(self, code: bool, data: bool, env: bool, metrics: bool) -> List[str]:
        """Generate notes about the assessment."""
        notes = []

        if code:
            notes.append("论文提到了代码或实现细节。")
        else:
            notes.append("论文未明确提及代码可用性。")

        if data:
            notes.append("论文提到了数据集或数据可用性。")
        else:
            notes.append("论文未明确提及数据集细节。")

        if env:
            notes.append("论文提到了实验环境或依赖配置。")
        else:
            notes.append("论文未提供详细的实验环境信息。")

        if metrics:
            notes.append("论文报告了评估指标。")
        else:
            notes.append("论文未提供充分的评估指标。")

        return notes

    def _generate_suggestions(self, code: bool, data: bool, env: bool, metrics: bool) -> List[str]:
        """Generate suggestions for improving reproducibility."""
        suggestions = []

        if not code:
            suggestions.append("建议作者公开源代码和实现细节。")

        if not data:
            suggestions.append("建议作者提供数据集访问方式或生成脚本。")

        if not env:
            suggestions.append("建议作者提供完整的环境配置文件。")

        if not metrics:
            suggestions.append("建议作者报告更全面的评估指标和统计信息。")

        if code and data and env and metrics:
            suggestions.append("论文在可复现性方面表现良好，建议作者持续维护代码和数据仓库。")

        return suggestions

    def _generate_analysis_text(self, assessment: ReproducibilityAssessment) -> str:
        """Generate analysis text from assessment."""
        score_percentage = int(assessment.score * 100)

        parts = [f"## 可复现性评估"]

        # Score
        parts.append(f"\n**可复现性评分**: {score_percentage}/100")

        # Score visualization
        score_bar = "█" * int(assessment.score * 10)
        parts.append(f"[{score_bar:<10}] {score_percentage}%")

        # Criteria breakdown
        parts.append("\n**评估标准：**")
        parts.append(f"- {'✅' if assessment.code_available else '❌'} 代码可用性")
        parts.append(f"- {'✅' if assessment.data_available else '❌'} 数据可用性")
        parts.append(f"- {'✅' if assessment.environment_specified else '❌'} 环境配置")
        parts.append(f"- {'✅' if assessment.metrics_reported else '❌'} 评估指标")

        # Notes
        if assessment.notes:
            parts.append("\n**评估说明：**")
            for note in assessment.notes:
                parts.append(f"- {note}")

        # Suggestions
        if assessment.suggestions:
            parts.append("\n**改进建议：**")
            for suggestion in assessment.suggestions:
                parts.append(f"- {suggestion}")

        return "\n".join(parts)