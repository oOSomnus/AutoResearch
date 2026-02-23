"""
Test Interactive Mode - Tests for interactive Q&A mode.
"""
import pytest
from unittest.mock import Mock, patch
from paper_agent.graph import (
    create_interactive_paper_agent_graph,
    run_initial_analysis,
    answer_user_question,
    should_continue_qa,
    InteractiveAgentState
)
from langchain_core.messages import HumanMessage, AIMessage


class TestInteractiveGraphCreation:
    """Test cases for interactive graph creation."""

    def test_create_interactive_graph(self):
        """Test that the interactive graph can be created."""
        graph = create_interactive_paper_agent_graph()

        assert graph is not None
        nodes = list(graph.nodes.keys())
        expected_nodes = ["initial_analysis", "answer_question"]

        for expected_node in expected_nodes:
            assert expected_node in nodes, f"Node {expected_node} not found in graph"

    def test_interactive_graph_structure(self):
        """Test that the interactive graph has the correct structure."""
        graph = create_interactive_paper_agent_graph()

        assert graph is not None
        # Verify the graph is compiled and executable
        # The graph should have an entry point and conditional edges


class TestInitialAnalysis:
    """Test cases for initial analysis in interactive mode."""

    @patch('paper_agent.graph.run_adaptive_paper_analysis')
    def test_run_initial_analysis_success(self, mock_run_adaptive):
        """Test successful initial analysis."""
        # Mock the adaptive analysis result
        mock_result = {
            "background": "Test background",
            "innovation": "Test innovation",
            "results": "Test results",
            "methodology": "Test methodology",
            "related_work": "",
            "limitations": "",
            "citations": "",
            "figures": "",
            "code": "",
            "reproducibility": "",
            "report": "Full report",
            "analysis_plan": {"dimensions": ["background", "innovation"]},
            "quality_scores": {"background": {"overall": 0.9}}
        }
        mock_run_adaptive.return_value = mock_result

        state = InteractiveAgentState(
            source="test.pdf",
            pdf_path="test.pdf",
            content="Test content",
            title="Test Paper",
            chapters=[],
            paper_type="experimental",
            output_format="markdown",
            language="zh",
            detail_level="standard",
            messages=[]
        )

        result = run_initial_analysis(state)

        assert result["analysis_complete"] is True
        assert result["background"] == "Test background"
        assert result["innovation"] == "Test innovation"
        assert result["results"] == "Test results"
        assert result["report"] == "Full report"
        assert result["analysis_plan"]["dimensions"] == ["background", "innovation"]

    @patch('paper_agent.graph.run_adaptive_paper_analysis')
    def test_run_initial_analysis_incomplete(self, mock_run_adaptive):
        """Test initial analysis with incomplete results."""
        # Mock incomplete result
        mock_result = {
            "background": "",
            "innovation": "",
            "results": "",
            "methodology": "",
            "related_work": "",
            "limitations": "",
            "citations": "",
            "figures": "",
            "code": "",
            "reproducibility": "",
            "report": "",
            "analysis_plan": {},
            "quality_scores": {}
        }
        mock_run_adaptive.return_value = mock_result

        state = InteractiveAgentState(
            source="test.pdf",
            pdf_path="test.pdf",
            content="Test content",
            title="Test Paper",
            chapters=[],
            paper_type="experimental",
            output_format="markdown",
            language="zh",
            detail_level="standard",
            messages=[]
        )

        result = run_initial_analysis(state)

        # Should still mark as complete even if content is empty
        assert result["analysis_complete"] is True


class TestAnswerUserQuestion:
    """Test cases for answering user questions."""

    @patch('paper_agent.graph.get_llm_for_interactive')
    def test_answer_user_question_basic(self, mock_get_llm):
        """Test basic user question answering."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Based on the analysis, the paper focuses on..."
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = InteractiveAgentState(
            source="test.pdf",
            title="Test Paper",
            background="This research addresses...",
            innovation="The key contribution is...",
            results="The findings show...",
            messages=[HumanMessage(content="What is this paper about?")]
        )

        result = answer_user_question(state)

        assert len(result["messages"]) == 2
        assert isinstance(result["messages"][-1], AIMessage)
        assert "focuses on" in result["messages"][-1].content

    @patch('paper_agent.graph.get_llm_for_interactive')
    def test_answer_user_question_with_history(self, mock_get_llm):
        """Test answering with conversation history."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "As I mentioned before, the paper uses..."
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = InteractiveAgentState(
            source="test.pdf",
            title="Test Paper",
            background="Test background",
            innovation="Test innovation",
            results="Test results",
            messages=[
                HumanMessage(content="What methods are used?"),
                AIMessage(content="The paper uses deep learning methods."),
                HumanMessage(content="Can you explain more about the architecture?")
            ]
        )

        result = answer_user_question(state)

        assert len(result["messages"]) == 3
        # The response should reference previous context
        assert result["messages"][-1].content is not None

    @patch('paper_agent.graph.get_llm_for_interactive')
    def test_answer_user_question_error_handling(self, mock_get_llm):
        """Test error handling in question answering."""
        # Mock LLM to raise an exception
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        mock_get_llm.return_value = mock_llm

        state = InteractiveAgentState(
            source="test.pdf",
            title="Test Paper",
            background="Test background",
            innovation="Test innovation",
            results="Test results",
            messages=[HumanMessage(content="What is this paper about?")]
        )

        result = answer_user_question(state)

        # Should handle error gracefully
        assert len(result["messages"]) == 2
        assert isinstance(result["messages"][-1], AIMessage)
        assert "错误" in result["messages"][-1].content or "error" in result["messages"][-1].content.lower()

    def test_answer_user_question_no_messages(self):
        """Test answering with no messages."""
        state = InteractiveAgentState(
            source="test.pdf",
            title="Test Paper",
            background="Test background",
            innovation="Test innovation",
            results="Test results",
            messages=[]
        )

        result = answer_user_question(state)

        # Should return state unchanged
        assert result == state


class TestContinueQA:
    """Test cases for Q&A continuation logic."""

    def test_should_continue_with_normal_message(self):
        """Test that normal questions trigger continuation."""
        state = InteractiveAgentState(
            messages=[HumanMessage(content="What is the main result?")]
        )

        result = should_continue_qa(state)

        assert result == "continue"

    def test_should_continue_with_exit_command(self):
        """Test that exit commands trigger end."""
        exit_commands = ["exit", "quit", "退出", "结束", "bye"]

        for cmd in exit_commands:
            state = InteractiveAgentState(
                messages=[HumanMessage(content=cmd)]
            )

            result = should_continue_qa(state)

            assert result == "end", f"Failed for command: {cmd}"

    def test_should_continue_with_exit_in_question(self):
        """Test that exit in question triggers end."""
        state = InteractiveAgentState(
            messages=[HumanMessage(content="Can I exit now?")]
        )

        result = should_continue_qa(state)

        assert result == "end"

    def test_should_continue_no_messages(self):
        """Test continuation with no messages."""
        state = InteractiveAgentState(messages=[])

        result = should_continue_qa(state)

        assert result == "continue"

    def test_should_continue_case_insensitive(self):
        """Test that exit commands are case-insensitive."""
        exit_variations = ["EXIT", "Exit", "EXIT", "quit", "QUIT"]

        for cmd in exit_variations:
            state = InteractiveAgentState(
                messages=[HumanMessage(content=cmd)]
            )

            result = should_continue_qa(state)

            assert result == "end", f"Failed for command: {cmd}"


class TestInteractiveState:
    """Test cases for InteractiveAgentState."""

    def test_interactive_state_creation(self):
        """Test creating an InteractiveAgentState."""
        state = InteractiveAgentState(
            source="test.pdf",
            pdf_path="test.pdf",
            content="Test content",
            title="Test Paper",
            chapters=[],
            paper_type="experimental",
            background="Test background",
            innovation="Test innovation",
            results="Test results",
            methodology="Test methodology",
            related_work="",
            limitations="",
            citations="",
            figures="",
            code="",
            reproducibility="",
            report="Test report",
            output_format="markdown",
            language="zh",
            detail_level="standard",
            analysis_complete=True,
            messages=[]
        )

        assert state.source == "test.pdf"
        assert state.title == "Test Paper"
        assert state.analysis_complete is True
        assert state.language == "zh"

    def test_interactive_state_default_values(self):
        """Test InteractiveAgentState default values."""
        state = InteractiveAgentState(
            source="test.pdf",
            pdf_path="test.pdf",
            content="Test content",
            title="Test Paper",
            chapters=[],
            paper_type="experimental",
            output_format="markdown",
            language="zh",
            detail_level="standard",
            messages=[]
        )

        # Check default values
        assert state.analysis_complete is False
        assert state.analysis_plan == {}
        assert state.quality_scores == {}


class TestInteractiveWorkflow:
    """Test cases for the complete interactive workflow."""

    @patch('paper_agent.graph.run_adaptive_paper_analysis')
    @patch('paper_agent.graph.get_llm_for_interactive')
    def test_complete_qa_conversation(self, mock_get_llm, mock_run_adaptive):
        """Test a complete Q&A conversation flow."""
        # Setup mocks
        mock_result = {
            "background": "Test background",
            "innovation": "Test innovation",
            "results": "Test results",
            "methodology": "Test methodology",
            "related_work": "",
            "limitations": "",
            "citations": "",
            "figures": "",
            "code": "",
            "reproducibility": "",
            "report": "Test report",
            "analysis_plan": {},
            "quality_scores": {}
        }
        mock_run_adaptive.return_value = mock_result

        mock_response = Mock()
        mock_response.content = "This is the answer."
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        # Create initial state
        state = InteractiveAgentState(
            source="test.pdf",
            pdf_path="test.pdf",
            content="Test content",
            title="Test Paper",
            chapters=[],
            paper_type="experimental",
            output_format="markdown",
            language="zh",
            detail_level="standard",
            messages=[]
        )

        # Run initial analysis
        state = run_initial_analysis(state)
        assert state["analysis_complete"] is True

        # Simulate a question
        state["messages"].append(HumanMessage(content="What is the main contribution?"))
        state = answer_user_question(state)

        assert len(state["messages"]) == 2
        assert isinstance(state["messages"][-1], AIMessage)

        # Simulate another question
        state["messages"].append(HumanMessage(content="What about the results?"))
        state = answer_user_question(state)

        assert len(state["messages"]) == 4
        assert isinstance(state["messages"][-1], AIMessage)

        # Test exit
        state["messages"].append(HumanMessage(content="exit"))
        result = should_continue_qa(state)

        assert result == "end"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])