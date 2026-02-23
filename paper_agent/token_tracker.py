"""
Token Tracker - Track input/output token usage during LLM calls.

This module provides utilities for counting and tracking token usage
during LLM API calls, which is useful for monitoring API usage and costs.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import json


@dataclass
class TokenUsage:
    """Represents token usage for a single API call."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    model: Optional[str] = None
    operation: Optional[str] = None  # e.g., "analyze_background", "analyze_innovation"

    def __post_init__(self):
        """Calculate total tokens if not provided."""
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class TokenTracker:
    """
    Tracks token usage across multiple LLM API calls.

    This class accumulates token statistics and provides methods to
    display and summarize token usage information.
    """

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    api_calls: int = 0
    history: list[TokenUsage] = field(default_factory=list)
    by_operation: Dict[str, TokenUsage] = field(default_factory=dict)

    def record_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> TokenUsage:
        """
        Record token usage for a single API call.

        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            model: Model name (optional)
            operation: Operation type (optional, e.g., "analyze_background")

        Returns:
            TokenUsage object representing this call
        """
        total = input_tokens + output_tokens
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total,
            model=model,
            operation=operation,
        )

        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += total
        self.api_calls += 1
        self.history.append(usage)

        if operation:
            if operation not in self.by_operation:
                self.by_operation[operation] = TokenUsage(operation=operation)
            op_usage = self.by_operation[operation]
            op_usage.input_tokens += input_tokens
            op_usage.output_tokens += output_tokens
            op_usage.total_tokens += total
            if model:
                op_usage.model = model

        return usage

    def get_summary(self) -> Dict[str, int]:
        """
        Get summary statistics.

        Returns:
            Dictionary with summary statistics
        """
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "api_calls": self.api_calls,
        }

    def format_display(self, include_breakdown: bool = True) -> str:
        """
        Format token usage for display.

        Args:
            include_breakdown: Whether to include breakdown by operation

        Returns:
            Formatted string for display
        """
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("📊 Token Usage Summary")
        lines.append("=" * 60)
        lines.append(f"  Total API Calls:    {self.api_calls:,}")
        lines.append(f"  Input Tokens:       {self.input_tokens:,}")
        lines.append(f"  Output Tokens:      {self.output_tokens:,}")
        lines.append(f"  Total Tokens:       {self.total_tokens:,}")
        lines.append(f"  Avg Tokens/Call:    {self.total_tokens // self.api_calls if self.api_calls > 0 else 0:,}")

        if include_breakdown and self.by_operation:
            lines.append("\n  Breakdown by Operation:")
            # Sort by total tokens descending
            sorted_ops = sorted(
                self.by_operation.items(),
                key=lambda x: x[1].total_tokens,
                reverse=True,
            )
            for operation, usage in sorted_ops:
                lines.append(
                    f"    {operation:30s}: "
                    f"{usage.input_tokens:,} in + {usage.output_tokens:,} out "
                    f"= {usage.total_tokens:,} total"
                )

        lines.append("=" * 60)

        return "\n".join(lines)

    def estimate_cost(
        self,
        input_price_per_1k: float = 0.003,
        output_price_per_1k: float = 0.006,
    ) -> float:
        """
        Estimate cost based on token usage.

        Args:
            input_price_per_1k: Price per 1,000 input tokens (default for GPT-4)
            output_price_per_1k: Price per 1,000 output tokens (default for GPT-4)

        Returns:
            Estimated cost in USD
        """
        input_cost = (self.input_tokens / 1000) * input_price_per_1k
        output_cost = (self.output_tokens / 1000) * output_price_per_1k
        return input_cost + output_cost

    def reset(self):
        """Reset all statistics."""
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.api_calls = 0
        self.history = []
        self.by_operation = {}

    def save_to_file(self, filepath: str) -> None:
        """
        Save token usage history to a JSON file.

        Args:
            filepath: Path to save the JSON file
        """
        data = {
            "summary": self.get_summary(),
            "by_operation": {
                op: {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "total_tokens": usage.total_tokens,
                    "model": usage.model,
                }
                for op, usage in self.by_operation.items()
            },
            "history": [
                {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "total_tokens": usage.total_tokens,
                    "model": usage.model,
                    "operation": usage.operation,
                }
                for usage in self.history
            ],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> "TokenTracker":
        """
        Load token usage history from a JSON file.

        Args:
            filepath: Path to the JSON file

        Returns:
            TokenTracker with loaded data
        """
        tracker = cls()

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        tracker.input_tokens = data["summary"]["input_tokens"]
        tracker.output_tokens = data["summary"]["output_tokens"]
        tracker.total_tokens = data["summary"]["total_tokens"]
        tracker.api_calls = data["summary"]["api_calls"]

        for op, op_data in data.get("by_operation", {}).items():
            tracker.by_operation[op] = TokenUsage(
                input_tokens=op_data["input_tokens"],
                output_tokens=op_data["output_tokens"],
                total_tokens=op_data["total_tokens"],
                model=op_data.get("model"),
                operation=op,
            )

        for hist_data in data.get("history", []):
            tracker.history.append(
                TokenUsage(
                    input_tokens=hist_data["input_tokens"],
                    output_tokens=hist_data["output_tokens"],
                    total_tokens=hist_data["total_tokens"],
                    model=hist_data.get("model"),
                    operation=hist_data.get("operation"),
                )
            )

        return tracker


# Global token tracker instance
_global_tracker: Optional[TokenTracker] = None


def get_global_tracker() -> TokenTracker:
    """
    Get the global token tracker instance.

    Returns:
        Global TokenTracker instance
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = TokenTracker()
    return _global_tracker


def set_global_tracker(tracker: Optional[TokenTracker]) -> None:
    """
    Set the global token tracker instance.

    Args:
        tracker: TokenTracker instance to set, or None to clear
    """
    global _global_tracker
    _global_tracker = tracker


def reset_global_tracker() -> None:
    """Reset the global token tracker."""
    global _global_tracker
    if _global_tracker is not None:
        _global_tracker.reset()