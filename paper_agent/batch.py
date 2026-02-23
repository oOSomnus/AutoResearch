"""
Batch Module - Batch processing coordination for multiple papers.
"""
import os
import asyncio
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .graph import run_paper_analysis
from .history import HistoryManager
from .progress import ProgressTracker, get_workflow_steps


@dataclass
class BatchResult:
    """Result of processing a single paper in batch."""
    source: str
    success: bool
    state: Optional[Dict[str, Any]]
    error: Optional[str]
    report_path: Optional[str]


class BatchProcessor:
    """Coordinates batch processing of multiple papers."""

    def __init__(self, max_workers: int = 2, delay: float = 1.0,
                 save_history: bool = True):
        """
        Initialize the batch processor.

        Args:
            max_workers: Maximum number of parallel workers
            delay: Delay between starting each batch item (seconds)
            save_history: Whether to save results to history
        """
        self.max_workers = max_workers
        self.delay = delay
        self.save_history = save_history
        self._history_manager: Optional[HistoryManager] = None

    def process(self, sources: List[str],
               output_format: str = "markdown",
               language: str = "zh",
               detail_level: str = "standard",
               progress_callback: Optional[Callable[[int, int], None]] = None
              ) -> List[BatchResult]:
        """
        Process multiple papers in batch.

        Args:
            sources: List of file paths or URLs
            output_format: Output format for reports
            language: Language for analysis
            detail_level: Detail level for analysis
            progress_callback: Optional callback for progress updates (completed, total)

        Returns:
            List of BatchResult objects
        """
        results = []
        total = len(sources)

        if total == 0:
            return results

        print(f"\n📦 批量处理 {total} 个论文...")
        print(f"👥 并行工作数: {self.max_workers}")
        print(f"⏱️  间隔延迟: {self.delay}秒\n")

        # Create progress tracker
        progress = ProgressTracker(total, "批量处理进度")
        progress.start()

        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_source = {}
                for i, source in enumerate(sources):
                    # Add delay between submissions if requested
                    if i > 0 and self.delay > 0:
                        import time
                        time.sleep(self.delay)

                    future = executor.submit(
                        self._process_single,
                        source,
                        output_format,
                        language,
                        detail_level
                    )
                    future_to_source[future] = source

                # Collect results as they complete
                for future in as_completed(future_to_source):
                    source = future_to_source[future]
                    try:
                        result = future.result()
                        results.append(result)

                        # Update progress
                        progress.update(f"完成: {os.path.basename(source)[:30]}")

                        # Call progress callback if provided
                        if progress_callback:
                            progress_callback(len(results), total)

                    except Exception as e:
                        # Handle failed tasks
                        error_result = BatchResult(
                            source=source,
                            success=False,
                            state=None,
                            error=str(e),
                            report_path=None
                        )
                        results.append(error_result)
                        progress.update(f"失败: {os.path.basename(source)[:30]}")

        finally:
            progress.close()

        # Sort results by original order
        results.sort(key=lambda r: sources.index(r.source))

        # Print summary
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        print(f"\n{'=' * 60}")
        print(f"📊 批量处理完成")
        print(f"{'=' * 60}")
        print(f"✅ 成功: {successful}")
        print(f"❌ 失败: {failed}")
        print(f"📁 总计: {total}\n")

        return results

    def _process_single(self, source: str, output_format: str,
                       language: str, detail_level: str) -> BatchResult:
        """
        Process a single paper.

        Args:
            source: File path or URL
            output_format: Output format
            language: Language
            detail_level: Detail level

        Returns:
            BatchResult object
        """
        try:
            state = run_paper_analysis(
                source,
                output_format=output_format,
                language=language,
                detail_level=detail_level
            )

            # Save to history if enabled
            if self.save_history:
                self._get_history_manager().add_entry(state)

            # Get report path from state
            report_path = state.get("report_path", "")

            return BatchResult(
                source=source,
                success=True,
                state=state,
                error=None,
                report_path=report_path
            )

        except Exception as e:
            return BatchResult(
                source=source,
                success=False,
                state=None,
                error=str(e),
                report_path=None
            )

    def _get_history_manager(self) -> HistoryManager:
        """Get or create history manager."""
        if self._history_manager is None:
            self._history_manager = HistoryManager()
        return self._history_manager


def load_batch_file(file_path: str) -> List[str]:
    """
    Load paper sources from a batch file.

    Args:
        file_path: Path to the batch file (one source per line)

    Returns:
        List of paper sources (file paths or URLs)
    """
    sources = []

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"批量文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                sources.append(line)

    return sources


def save_batch_file(sources: List[str], file_path: str) -> None:
    """
    Save paper sources to a batch file.

    Args:
        sources: List of paper sources
        file_path: Path to save the batch file
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# AutoResearch 批量处理文件\n")
        f.write("# 每行一个PDF文件路径或URL\n")
        f.write("# 空行和以#开头的行将被忽略\n\n")
        for source in sources:
            f.write(f"{source}\n")