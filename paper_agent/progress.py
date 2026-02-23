"""
Progress Module - Progress tracking for paper analysis.
"""
from typing import Optional, List
from tqdm import tqdm


class ProgressTracker:
    """Tracks progress of paper analysis."""

    def __init__(self, total_steps: int, description: str = "分析进度"):
        """
        Initialize the progress tracker.

        Args:
            total_steps: Total number of steps to track
            description: Description for the progress bar
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self._pbar: Optional[tqdm] = None
        self._step_names: List[str] = []
        self._completed_steps: List[str] = []

    def start(self) -> None:
        """Start the progress tracker."""
        self._pbar = tqdm(
            total=self.total_steps,
            desc=self.description,
            unit="step"
        )

    def update(self, step_name: str, increment: int = 1) -> None:
        """
        Update progress.

        Args:
            step_name: Name of the step being completed
            increment: Number of steps to increment (default: 1)
        """
        if self._pbar:
            self._pbar.set_postfix_str(step_name)
            self._pbar.update(increment)

        self.current_step += increment
        self._step_names.append(step_name)
        self._completed_steps.append(step_name)

    def close(self) -> None:
        """Close the progress tracker."""
        if self._pbar:
            self._pbar.close()
            self._pbar = None

    def get_completed_steps(self) -> List[str]:
        """Get list of completed step names."""
        return self._completed_steps.copy()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Default workflow steps for paper analysis
DEFAULT_WORKFLOW_STEPS = [
    "获取PDF",
    "提取内容",
    "检测论文类型",
    "分析背景",
    "分析创新",
    "分析结果",
    "生成报告",
    "保存报告"
]


def get_workflow_steps(paper_type: Optional[str] = None) -> List[str]:
    """
    Get workflow steps based on paper type.

    Args:
        paper_type: Type of paper (survey, experimental, theoretical, unknown)

    Returns:
        List of step names for the workflow
    """
    base_steps = [
        "获取PDF",
        "提取内容",
        "检测论文类型",
        "分析背景"
    ]

    if paper_type == "survey":
        base_steps.extend(["分析相关工作"])
    elif paper_type == "experimental":
        base_steps.extend(["分析创新", "分析实验方法"])
    else:  # theoretical or unknown
        base_steps.extend(["分析创新"])

    base_steps.extend(["分析结果", "生成报告", "保存报告"])
    return base_steps


# Convenience function for creating a workflow progress tracker
def create_workflow_progress(paper_type: Optional[str] = None) -> ProgressTracker:
    """
    Create a progress tracker for the paper analysis workflow.

    Args:
        paper_type: Type of paper (survey, experimental, theoretical, unknown)

    Returns:
        ProgressTracker instance configured for the workflow
    """
    steps = get_workflow_steps(paper_type)
    return ProgressTracker(len(steps), "分析进度")