"""
Test Adaptive Graph - Tests for the adaptive paper analysis workflow.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from paper_agent.graph import (
    create_adaptive_paper_agent_graph,
    run_adaptive_paper_analysis,
    route_after_planning,
    route_after_assessment
)
from paper_agent.nodes import plan_analysis, assess_quality


class TestAdaptiveGraph:
    """Test cases for the adaptive graph workflow."""

    def test_route_after_planning_with_dimensions(self):
        """Test routing when there are dimensions to analyze."""
        state = {
            "analysis_plan": {
                "dimensions": ["background", "innovation", "results"],
                "priority": ["innovation", "background", "results"]
            },
            "iteration_count": {}
        }

        result = route_after_planning(state)

        assert result == "analyze_innovation"
        assert state["current_dimension"] == "innovation"
        assert state["iteration_count"]["innovation"] == 1

    def test_route_after_planning_no_dimensions(self):
        """Test routing when all dimensions are analyzed."""
        state = {
            "analysis_plan": {"dimensions": []},
            "iteration_count": {}
        }

        result = route_after_planning(state)

        assert result == "generate_report"

    def test_route_after_planning_citations(self):
        """Test routing to extraction node."""
        state = {
            "analysis_plan": {"dimensions": ["citations"]},
            "iteration_count": {}
        }

        result = route_after_planning(state)

        assert result == "extract_citations"

    def test_route_after_assessment_needs_refinement(self):
        """Test routing when refinement is needed."""
        state = {
            "current_dimension": "background",
            "needs_refinement": ["background"],
            "iteration_count": {"background": 1}
        }

        result = route_after_assessment(state)

        assert result == "analyze_background"
        assert "background" not in state["needs_refinement"]

    def test_route_after_assessment_max_iterations_reached(self):
        """Test routing when max iterations is reached."""
        state = {
            "current_dimension": "background",
            "needs_refinement": ["background"],
            "iteration_count": {"background": 3},
            "max_iterations": 3
        }

        result = route_after_assessment(state)

        assert result == "route_after_planning"
        assert "background" not in state["needs_refinement"]

    def test_route_after_assessment_no_refinement(self):
        """Test routing when no refinement is needed."""
        state = {
            "current_dimension": "background",
            "needs_refinement": []
        }

        result = route_after_assessment(state)

        assert result == "route_after_planning"

    @patch('paper_agent.nodes.get_llm')
    def test_plan_analysis_basic(self, mock_get_llm):
        """Test basic analysis planning."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = '''{
            "dimensions": ["background", "innovation", "results"],
            "priority": ["innovation", "background", "results"],
            "reason": "Experimental paper with novel approach",
            "notes": ["Focus on methodology"],
            "suggested_detail_level": "standard"
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "title": "Test Paper",
            "paper_type": "experimental",
            "content": "This is a test paper content.",
            "chapters": [],
            "language": "zh"
        }

        result = plan_analysis(state)

        assert "analysis_plan" in result
        assert result["analysis_plan"]["dimensions"] == ["background", "innovation", "results"]
        assert result["current_dimension"] == ""
        assert result["max_iterations"] == 3
        assert result["quality_threshold"] == 0.75

    @patch('paper_agent.nodes.get_llm')
    def test_assess_quality_high_score(self, mock_get_llm):
        """Test quality assessment with high score."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = '''{
            "completeness": 0.9,
            "depth": 0.85,
            "clarity": 0.95,
            "accuracy": 0.9,
            "overall_score": 0.9,
            "issues": [],
            "needs_refinement": false,
            "suggestion": ""
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "background",
            "background": "Good analysis content here.",
            "language": "zh",
            "quality_threshold": 0.75
        }

        result = assess_quality(state)

        assert "quality_scores" in result
        assert "background" in result["quality_scores"]
        assert result["quality_scores"]["background"]["overall"] == 0.9
        assert "dimension_to_assess" not in result or result["dimension_to_assess"] == ""

    @patch('paper_agent.nodes.get_llm')
    def test_assess_quality_low_score(self, mock_get_llm):
        """Test quality assessment with low score."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = '''{
            "completeness": 0.5,
            "depth": 0.4,
            "clarity": 0.7,
            "accuracy": 0.6,
            "overall_score": 0.55,
            "issues": ["Missing details", "Unclear explanation"],
            "needs_refinement": true,
            "suggestion": "Add more specific examples"
        }'''
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "dimension_to_assess": "innovation",
            "innovation": "Brief analysis.",
            "language": "zh",
            "quality_threshold": 0.75,
            "iteration_count": {"innovation": 1},
            "max_iterations": 3
        }

        result = assess_quality(state)

        assert "background" in result.get("needs_refinement", [])


class TestAdaptiveGraphCreation:
    """Test cases for adaptive graph creation."""

    def test_create_adaptive_graph(self):
        """Test that the adaptive graph can be created."""
        graph = create_adaptive_paper_agent_graph()

        assert graph is not None
        # Verify that the graph has the expected structure
        nodes = list(graph.nodes.keys())
        expected_nodes = [
            "fetch_pdf", "extract_content", "detect_paper_type",
            "plan_analysis", "analyze_background", "analyze_innovation",
            "analyze_methodology", "analyze_results",
            "analyze_related_work", "analyze_limitations",
            "generate_report", "save_report", "assess_quality",
            "extract_citations", "analyze_figures", "extract_code",
            "assess_reproducibility"
        ]

        for expected_node in expected_nodes:
            assert expected_node in nodes, f"Node {expected_node} not found in graph"

    def test_create_adaptive_graph_with_custom_params(self):
        """Test creating adaptive graph with custom parameters."""
        graph = create_adaptive_paper_agent_graph(
            max_iterations=5,
            quality_threshold=0.8,
            enable_quality_check=False
        )

        assert graph is not None
        # Graph should be created successfully


class TestAdaptiveAnalysisExecution:
    """Test cases for running adaptive analysis."""

    @patch('paper_agent.graph.fetch_pdf')
    @patch('paper_agent.graph.extract_content')
    @patch('paper_agent.graph.detect_paper_type')
    @patch('paper_agent.graph.plan_analysis')
    @patch('paper_agent.graph.analyze_background')
    @patch('paper_agent.graph.analyze_innovation')
    @patch('paper_agent.graph.analyze_results')
    @patch('paper_agent.graph.assess_quality')
    @patch('paper_agent.graph.generate_report')
    @patch('paper_agent.graph.save_report')
    @patch('paper_agent.history.get_history_manager')
    def test_run_adaptive_analysis_full_workflow(
        self, mock_history, mock_save, mock_generate, mock_assess,
        mock_results, mock_innovation, mock_background, mock_plan,
        mock_detect, mock_extract, mock_fetch
    ):
        """Test running the full adaptive analysis workflow."""
        # Mock the node functions
        def mock_state_update(state):
            return state

        mock_fetch.side_effect = lambda s: mock_state_update({"pdf_path": "test.pdf", "title": "Test"})
        mock_extract.side_effect = lambda s: mock_state_update({"content": "content", "chapters": []})
        mock_detect.side_effect = lambda s: mock_state_update({"paper_type": "experimental"})
        mock_plan.side_effect = lambda s: mock_state_update({
            "analysis_plan": {
                "dimensions": ["background", "innovation", "results"],
                "priority": ["background", "innovation", "results"]
            }
        })
        mock_background.side_effect = lambda s: mock_state_update({"background": "bg"})
        mock_innovation.side_effect = lambda s: mock_state_update({"innovation": "inn"})
        mock_results.side_effect = lambda s: mock_state_update({"results": "res"})
        mock_assess.side_effect = lambda s: mock_state_update({"quality_scores": {"background": {"overall": 0.9}}})
        mock_generate.side_effect = lambda s: mock_state_update({"report": "report"})

        # Mock history manager
        mock_history_mgr = Mock()
        mock_history.return_value = mock_history_mgr

        # Run the analysis
        result = run_adaptive_paper_analysis(
            source="test.pdf",
            output_format="markdown",
            language="zh",
            detail_level="standard",
            max_iterations=3,
            quality_threshold=0.75
        )

        assert result is not None
        assert result.get("report") == "report"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])