"""
Test Quality Assessment - Tests for quality assessment functionality.
"""
import pytest
from unittest.mock import Mock, patch
from paper_agent.nodes import assess_quality
from paper_agent.types import QualityAssessment


class TestQualityAssessment:
    """Test cases for quality assessment."""

    @patch('paper_agent.nodes.get_llm')
    def test_assess_quality_high_completeness(self, mock_get_llm):
        """Test quality assessment with high completeness score."""
        mock_response = Mock()
        mock_response.content = '''{
            "completeness": 0.95,
            "depth": 0.85,
            "clarity": 0.9,
            "accuracy": 0.92,
            "overall_score": 0.91,
            "issues": [],
            "needs_refinement": false,
            "suggestion": "Analysis is comprehensive and well-structured"
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "background",
            "background": "The research addresses a critical gap in the field...",
            "language": "zh",
            "quality_threshold": 0.75,
            "iteration_count": {"background": 1},
            "max_iterations": 3
        }

        result = assess_quality(state)

        assert "quality_scores" in result
        assert "background" in result["quality_scores"]
        scores = result["quality_scores"]["background"]
        assert scores["completeness"] == 0.95
        assert scores["depth"] == 0.85
        assert scores["clarity"] == 0.9
        assert scores["accuracy"] == 0.92
        assert scores["overall"] == 0.91

    @patch('paper_agent.nodes.get_llm')
    def test_assess_quality_low_depth(self, mock_get_llm):
        """Test quality assessment with low depth score."""
        mock_response = Mock()
        mock_response.content = '''{
            "completeness": 0.8,
            "depth": 0.5,
            "clarity": 0.85,
            "accuracy": 0.75,
            "overall_score": 0.73,
            "issues": ["Analysis lacks depth", "Does not explore core concepts"],
            "needs_refinement": true,
            "suggestion": "Add more detailed analysis of the core methodology"
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "innovation",
            "innovation": "The paper introduces a new method.",
            "language": "zh",
            "quality_threshold": 0.75,
            "iteration_count": {"innovation": 1},
            "max_iterations": 3
        }

        result = assess_quality(state)

        assert "quality_scores" in result
        assert "innovation" in result["quality_scores"]
        scores = result["quality_scores"]["innovation"]
        assert scores["depth"] == 0.5
        assert scores["overall"] == 0.73

    @patch('paper_agent.nodes.get_llm')
    def test_assess_quality_below_threshold(self, mock_get_llm):
        """Test that assessment below threshold triggers refinement."""
        mock_response = Mock()
        mock_response.content = '''{
            "completeness": 0.6,
            "depth": 0.5,
            "clarity": 0.7,
            "accuracy": 0.65,
            "overall_score": 0.61,
            "issues": ["Missing key information", "Brief analysis"],
            "needs_refinement": true,
            "suggestion": "Expand on the main contributions"
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "results",
            "results": "Results show improvement.",
            "language": "zh",
            "quality_threshold": 0.75,
            "iteration_count": {"results": 1},
            "max_iterations": 3,
            "needs_refinement": []
        }

        result = assess_quality(state)

        assert "results" in result["needs_refinement"]

    @patch('paper_agent.nodes.get_llm')
    def test_assess_quality_max_iterations_reached(self, mock_get_llm):
        """Test that no refinement happens when max iterations reached."""
        mock_response = Mock()
        mock_response.content = '''{
            "completeness": 0.5,
            "depth": 0.4,
            "clarity": 0.6,
            "accuracy": 0.55,
            "overall_score": 0.51,
            "issues": ["Multiple issues detected"],
            "needs_refinement": true,
            "suggestion": "Complete rewrite needed"
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "methodology",
            "methodology": "Method is described briefly.",
            "language": "zh",
            "quality_threshold": 0.75,
            "iteration_count": {"methodology": 3},
            "max_iterations": 3,
            "needs_refinement": []
        }

        result = assess_quality(state)

        # Should not add to needs_refinement when max iterations reached
        assert "methodology" not in result["needs_refinement"]

    @patch('paper_agent.nodes.get_llm')
    def test_assess_quality_json_parsing_error(self, mock_get_llm):
        """Test handling of JSON parsing errors."""
        # Return invalid JSON
        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "limitations",
            "limitations": "Some limitations mentioned.",
            "language": "zh",
            "quality_threshold": 0.75,
            "needs_refinement": []
        }

        result = assess_quality(state)

        # Should gracefully handle the error and not crash
        assert result is not None
        assert "dimension_to_assess" in result

    @patch('paper_agent.nodes.get_llm')
    def test_assess_quality_multiple_dimensions(self, mock_get_llm):
        """Test quality assessment across multiple dimensions."""
        mock_response = Mock()
        mock_response.content = '''{
            "completeness": 0.85,
            "depth": 0.8,
            "clarity": 0.9,
            "accuracy": 0.88,
            "overall_score": 0.86,
            "issues": [],
            "needs_refinement": false,
            "suggestion": ""
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        dimensions = ["background", "innovation", "results", "methodology"]
        state = {
            "quality_scores": {},
            "needs_refinement": [],
            "quality_threshold": 0.75,
            "max_iterations": 3,
            "language": "zh"
        }

        for dim in dimensions:
            state["dimension_to_assess"] = dim
            state[dim] = f"Analysis for {dim}."
            state["iteration_count"] = {dim: 1}
            state = assess_quality(state)

        # All dimensions should be scored
        for dim in dimensions:
            assert dim in state["quality_scores"]
            assert state["quality_scores"][dim]["overall"] >= 0.75


class TestQualityAssessmentDataClass:
    """Test cases for QualityAssessment dataclass."""

    def test_quality_assessment_creation(self):
        """Test creating a QualityAssessment object."""
        assessment = QualityAssessment(
            dimension="innovation",
            score=0.85,
            completeness=0.9,
            depth=0.8,
            clarity=0.88,
            accuracy=0.85,
            issues=[],
            needs_refinement=False,
            suggestion=""
        )

        assert assessment.dimension == "innovation"
        assert assessment.score == 0.85
        assert assessment.completeness == 0.9
        assert assessment.depth == 0.8
        assert assessment.clarity == 0.88
        assert assessment.accuracy == 0.85
        assert not assessment.needs_refinement

    def test_quality_assessment_with_issues(self):
        """Test QualityAssessment with issues."""
        assessment = QualityAssessment(
            dimension="results",
            score=0.6,
            completeness=0.5,
            depth=0.6,
            clarity=0.7,
            accuracy=0.6,
            issues=["Missing specific numbers", "Insufficient detail"],
            needs_refinement=True,
            suggestion="Add more quantitative data"
        )

        assert assessment.dimension == "results"
        assert assessment.score == 0.6
        assert len(assessment.issues) == 2
        assert assessment.needs_refinement
        assert assessment.suggestion == "Add more quantitative data"


class TestQualityThresholds:
    """Test cases for quality threshold behavior."""

    @patch('paper_agent.nodes.get_llm')
    def test_high_threshold_strict_evaluation(self, mock_get_llm):
        """Test that higher threshold requires better quality."""
        mock_response = Mock()
        # Score is 0.8, which would pass 0.75 but fail 0.9
        mock_response.content = '''{
            "completeness": 0.85,
            "depth": 0.8,
            "clarity": 0.85,
            "accuracy": 0.8,
            "overall_score": 0.82,
            "issues": ["Could be more detailed"],
            "needs_refinement": true,
            "suggestion": "Expand on key points"
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "background",
            "background": "Analysis content.",
            "language": "zh",
            "quality_threshold": 0.9,  # High threshold
            "iteration_count": {"background": 1},
            "max_iterations": 3,
            "needs_refinement": []
        }

        result = assess_quality(state)

        # With 0.82 score and 0.9 threshold, should trigger refinement
        assert "background" in result["needs_refinement"]

    @patch('paper_agent.nodes.get_llm')
    def test_low_threshold_forgiving_evaluation(self, mock_get_llm):
        """Test that lower threshold is more forgiving."""
        mock_response = Mock()
        # Score is 0.65, which would fail 0.75 but pass 0.6
        mock_response.content = '''{
            "completeness": 0.7,
            "depth": 0.6,
            "clarity": 0.7,
            "accuracy": 0.65,
            "overall_score": 0.66,
            "issues": ["Some areas brief"],
            "needs_refinement": false,
            "suggestion": ""
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "innovation",
            "innovation": "Innovation content.",
            "language": "zh",
            "quality_threshold": 0.6,  # Low threshold
            "iteration_count": {"innovation": 1},
            "max_iterations": 3,
            "needs_refinement": []
        }

        result = assess_quality(state)

        # With 0.66 score and 0.6 threshold, should NOT trigger refinement
        # The needs_refinement flag in the response is false
        assert "innovation" not in result["needs_refinement"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])