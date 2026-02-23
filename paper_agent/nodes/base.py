"""
Base definitions for node functions.

Contains the AgentState TypedDict and common utilities used across all nodes.
"""
import os
from typing import TypedDict, List, Optional, Dict, Any, TYPE_CHECKING

from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult

if TYPE_CHECKING:
    from paper_agent.token_tracker import TokenTracker


class TokenTrackingCallbackHandler(BaseCallbackHandler):
    """
    Callback handler for tracking token usage in LangChain calls.

    This handler captures token usage from LLM calls and records it
    in a TokenTracker instance.
    """

    def __init__(self, tracker: Optional["TokenTracker"] = None, operation: Optional[str] = None):
        """
        Initialize the token tracking callback.

        Args:
            tracker: TokenTracker instance to record usage (None for no tracking)
            operation: Operation name for categorizing the usage (e.g., "analyze_background")
        """
        super().__init__()
        self._tracker = tracker
        self._operation = operation

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Called when LLM starts processing."""
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """
        Called when LLM finishes processing.

        Args:
            response: LLM result containing token usage information
        """
        if self._tracker is None:
            return

        # Try to extract token usage from the response
        for generation in response.generations:
            for gen in generation:
                # Get token usage info if available
                llm_output = response.llm_output or {}

                # OpenAI format
                token_usage = llm_output.get("token_usage", {})
                input_tokens = token_usage.get("prompt_tokens", 0)
                output_tokens = token_usage.get("completion_tokens", 0)

                # Record the usage
                if input_tokens > 0 or output_tokens > 0:
                    # Try to get model name from llm_output or kwargs
                    model = llm_output.get("model_name")
                    self._tracker.record_usage(
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        model=model,
                        operation=self._operation,
                    )


class AgentState(TypedDict):
    """State object passed between nodes in the workflow."""
    pdf_path: str
    content: str
    background: str
    innovation: str
    results: str
    report: str
    title: str
    source: str
    # New fields for enhanced analysis
    chapters: List  # Extracted chapters list
    paper_type: str  # 'survey', 'experimental', 'theoretical', 'unknown'
    methodology: str  # Experimental methodology analysis
    related_work: str  # Related work analysis
    limitations: str  # Limitations analysis

    # Output configuration fields (Phase 1)
    output_format: str  # 'markdown', 'html', 'pdf', 'json'
    language: str  # 'zh', 'en'
    detail_level: str  # 'brief', 'standard', 'detailed'

    # New extraction dimensions (Phase 4)
    citations: str  # Citation analysis
    figures: str  # Figure analysis
    code: str  # Code extraction
    reproducibility: str  # Reproducibility assessment

    # Structured extraction data
    citations_list: List[dict]  # List of citation info
    figures_list: List[dict]  # List of figure info
    code_snippets: List[dict]  # List of code snippets
    reproducibility_score: float  # Reproducibility score (0-1)

    # Progress and checkpoint fields (Phase 2)
    completed_nodes: List[str]  # List of completed node names
    checkpoint_path: str  # Path to checkpoint file
    cache_key: str  # Cache key for the analysis

    # Adaptive analysis fields (Phase 5)
    analysis_plan: Dict[str, Any]  # Analysis plan with dimensions and priority
    quality_scores: Dict[str, float]  # Quality scores for each dimension
    iteration_count: Dict[str, int]  # Iteration count for each dimension
    pending_questions: List[str]  # Questions pending user confirmation
    user_feedback: Dict[str, Any]  # User feedback on analysis
    conversation_history: List[Dict]  # Conversation history for interactive mode
    needs_refinement: List[str]  # Dimensions needing refinement
    should_exit: bool  # Whether to exit early
    research_mode: str  # Current mode: 'auto', 'interactive', 'manual'
    current_dimension: str  # Current dimension being analyzed
    dimension_to_assess: str  # Dimension to assess for quality
    max_iterations: int  # Maximum iterations per dimension
    quality_threshold: float  # Quality threshold for acceptance

    # Token tracker (Phase 6)
    token_tracker: Optional[Any]  # TokenTracker instance for tracking API usage


def get_llm(token_tracker: Optional["TokenTracker"] = None, operation: Optional[str] = None):
    """
    Get configured LLM instance from environment variables.

    Args:
        token_tracker: Optional TokenTracker instance for tracking token usage
        operation: Optional operation name for categorizing token usage

    Returns:
        Configured ChatOpenAI instance
    """
    from dotenv import load_dotenv
    load_dotenv()

    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gpt-4")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")

    # Create LLM instance
    llm = ChatOpenAI(
        openai_api_base=api_base,
        openai_api_key=api_key,
        model=model_name,
        temperature=0.3
    )

    # Store token tracker as attribute for later use during invocation
    if token_tracker is not None:
        llm.token_tracker = token_tracker
        llm.operation = operation

    return llm


def invoke_with_token_tracking(llm: ChatOpenAI, prompt: str, operation: Optional[str] = None) -> str:
    """
    Invoke LLM with optional token tracking.

    Args:
        llm: ChatOpenAI instance
        prompt: Prompt to send to LLM
        operation: Optional operation name (overrides the one set on the LLM instance)

    Returns:
        LLM response string
    """
    token_tracker = getattr(llm, "token_tracker", None)
    op_name = operation or getattr(llm, "operation", None)

    if token_tracker is not None:
        # Create callback handler for this invocation
        callback = TokenTrackingCallbackHandler(tracker=token_tracker, operation=op_name)
        response = llm.invoke(prompt, config={"callbacks": [callback]})
    else:
        response = llm.invoke(prompt)

    return response.content