"""
UI Module - Rich terminal UI for the paper agent.
"""
from typing import List, Dict, Any, Optional

# Optional rich import
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, TaskID
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback to simple print
    Console = None
    Table = None
    Panel = None
    Progress = None


class UI:
    """Rich terminal UI for the paper agent."""

    def __init__(self):
        """Initialize the UI."""
        if RICH_AVAILABLE:
            self.console = Console()
            self._progress: Optional[Progress] = None
            self._progress_task_id: Optional[TaskID] = None
            self._current_step = ""
            self._current_detail = ""
        else:
            self.console = None
            self._progress = None
            self._progress_task_id = None
            self._current_step = ""
            self._current_detail = ""

    def print_banner(self) -> None:
        """Print a welcome banner."""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         📚 论文阅读 Agent - Paper Reading Agent          ║
║                                                           ║
║     快速理解论文核心内容：背景、创新、结果                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        if self.console:
            self.console.print(banner)
        else:
            print(banner)

    def print_help(self) -> None:
        """Print usage help."""
        help_text = """用法:
  python main.py [选项] <文件路径或URL>     # 直接分析指定文件
  python main.py                            # 交互式模式

支持:
  - 本地PDF文件路径 (例: ./paper.pdf 或 /path/to/paper.pdf)
  - PDF URL链接 (例: https://arxiv.org/pdf/xxxx.pdf)

输出格式选项:
  --format FORMAT      输出格式: markdown, html, pdf, json (默认: markdown)
  --language LANG      语言: zh (中文), en (英文) (默认: zh)
  --detail LEVEL       详细程度: brief, standard, detailed (默认: standard)

示例:
  python main.py ./my_paper.pdf
  python main.py --format html --language en ./my_paper.pdf
  python main.py --format pdf --detail detailed ./my_paper.pdf
  python main.py https://arxiv.org/pdf/2301.xxxxx.pdf

环境变量:
  需要在 .env 文件中配置 OPENAI_API_BASE 和 OPENAI_API_KEY
"""
        if self.console:
            self.console.print(help_text)
        else:
            print(help_text)

    def print_paper_info(self, title: str, source: str, paper_type: str = "unknown") -> None:
        """Print paper information."""
        info = f"📄 论文信息\n标题: {title}\n来源: {source}\n类型: {self._get_paper_type_label(paper_type)}"
        if self.console:
            info_panel = Panel(
                f"[bold]标题:[/bold] {title}\n"
                f"[bold]来源:[/bold] {source}\n"
                f"[bold]类型:[/bold] {self._get_paper_type_label(paper_type)}",
                title="📄 论文信息",
                border_style="blue"
            )
            self.console.print(info_panel)
        else:
            print(info)

    def print_summary(self, state: Dict[str, Any], output_format: str = "markdown",
                     language: str = "zh", detail_level: str = "standard") -> None:
        """Print analysis summary."""
        summary = f"""📊 分析完成!
📄 标题: {state.get("title", "未知")[:50]}
📁 来源: {state.get("source", "")[:50]}
🔬 类型: {self._get_paper_type_label(state.get("paper_type", "unknown"))}
📋 格式: {output_format}
🌐 语言: {language}
📊 详细程度: {detail_level}"""
        if self.console:
            self.console.print(summary)
        else:
            print(summary)

    def print_history(self, entries: List[Dict[str, Any]]) -> None:
        """Print analysis history."""
        if not entries:
            msg = "[yellow]暂无历史记录[/yellow]" if self.console else "📚 暂无历史记录"
            if self.console:
                self.console.print(msg)
            else:
                print(msg)
            return

        if self.console:
            table = Table(title="📚 分析历史", box=box.ROUNDED)
            table.add_column("ID", style="dim", width=6)
            table.add_column("标题", style="cyan")
            table.add_column("类型", style="green")
            table.add_column("语言", style="magenta")
            table.add_column("格式", style="blue")
            table.add_column("分析时间", style="yellow")

            for entry in entries:
                table.add_row(
                    str(entry.get("id", "")),
                    entry.get("title", "未知")[:30] + ("..." if len(entry.get("title", "")) > 30 else ""),
                    self._get_paper_type_label(entry.get("paper_type", "unknown")),
                    entry.get("language", "zh"),
                    entry.get("output_format", "markdown"),
                    entry.get("analyzed_at", "")[:19]
                )

            self.console.print(table)
        else:
            print("📚 分析历史")
            for entry in entries[:5]:
                print(f"  {entry.get('id', '')}: {entry.get('title', '')}")

    def print_checkpoints(self, checkpoints: List[Dict[str, Any]]) -> None:
        """Print available checkpoints."""
        if not checkpoints:
            msg = "[yellow]暂无检查点[/yellow]" if self.console else "💾 暂无检查点"
            if self.console:
                self.console.print(msg)
            else:
                print(msg)
            return

        if self.console:
            table = Table(title="💾 可用检查点", box=box.ROUNDED)
            table.add_column("#", style="dim", width=4)
            table.add_column("标题", style="cyan")
            table.add_column("类型", style="green")
            table.add_column("完成节点", style="yellow")
            table.add_column("保存时间", style="blue")

            for i, checkpoint in enumerate(checkpoints, 1):
                completed = ", ".join(checkpoint.get("completed_nodes", []))
                table.add_row(
                    str(i),
                    checkpoint.get("title", "未知")[:30] + ("..." if len(checkpoint.get("title", "")) > 30 else ""),
                    self._get_paper_type_label(checkpoint.get("paper_type", "unknown")),
                    completed[:30] + ("..." if len(completed) > 30 else ""),
                    checkpoint.get("saved_at", "")[:19]
                )

            self.console.print(table)
        else:
            print("💾 可用检查点")
            for checkpoint in checkpoints[:5]:
                nodes = ', '.join(checkpoint.get("completed_nodes", []))
                print(f"  {checkpoint.get('title', '')}: {nodes}")

    def print_batch_summary(self, total: int, successful: int, failed: int) -> None:
        """Print batch processing summary."""
        summary = f"""📊 批量处理完成!
✅ 成功: {successful}
❌ 失败: {failed}
📁 总计: {total}"""
        if self.console:
            self.console.print(summary)
        else:
            print(summary)

    def print_cache_stats(self, stats: Dict[str, Any]) -> None:
        """Print cache statistics."""
        info = f"""🗄️  缓存统计
状态: {'已启用' if stats.get('enabled') else '已禁用'}
内存条目: {stats.get('memory_entries', 0)}
磁盘条目: {stats.get('disk_entries', 0)}
TTL (小时): {stats.get('ttl_hours', 0)}"""
        if self.console:
            self.console.print(info)
        else:
            print(info)

    def print_qa_header(self, paper_id: str) -> None:
        """Print Q&A mode header."""
        msg = "💬 问答模式\n\n请输入您的问题，系统将基于论文分析内容回答。\n输入 'q' 或 'quit' 退出问答模式。"
        if self.console:
            header = Panel(
                "[bold]💬 问答模式[/bold]\n\n"
                "请输入您的问题，系统将基于论文分析内容回答。\n"
                "输入 'q' 或 'quit' 退出问答模式。",
                border_style="blue"
            )
            self.console.print(header)
        else:
            print(msg)

    def print_qa_result(self, question: str, answer: str, source_sections: List[str]) -> None:
        """Print Q&A result."""
        result = f"""🤖 回答
问题: {question}
回答: {answer}
来源: {', '.join(source_sections)}"""
        if self.console:
            result_panel = Panel(
                f"[bold]问题:[/bold] {question}\n\n"
                f"[bold]回答:[/bold] {answer}\n\n"
                f"[dim]来源: {', '.join(source_sections)}[/dim]",
                title="🤖 回答",
                border_style="green"
            )
            self.console.print(result_panel)
        else:
            print(result)

    def print_error(self, message: str) -> None:
        """Print error message."""
        msg = f"[red]❌ 错误: {message}[/red]" if self.console else f"❌ 错误: {message}"
        if self.console:
            self.console.print(msg)
        else:
            print(msg)

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        msg = f"[yellow]⚠️  警告: {message}[/yellow]" if self.console else f"⚠️  警告: {message}"
        if self.console:
            self.console.print(msg)
        else:
            print(msg)

    def print_success(self, message: str) -> None:
        """Print success message."""
        msg = f"[green]✅ {message}[/green]" if self.console else f"✅ {message}"
        if self.console:
            self.console.print(msg)
        else:
            print(msg)

    def print_info(self, message: str) -> None:
        """Print info message."""
        msg = f"[blue]ℹ️  {message}[/blue]" if self.console else f"ℹ️  {message}"
        if self.console:
            self.console.print(msg)
        else:
            print(msg)

    # Progress tracking methods

    def create_progress_tracker(self, steps: List[str], description: str = "分析进度") -> Optional[TaskID]:
        """
        Create a progress tracker for analysis steps.

        Args:
            steps: List of step names
            description: Description for the progress bar

        Returns:
            TaskID for the progress task (None if rich is not available)
        """
        if not RICH_AVAILABLE:
            return None

        self._progress = Progress(
            *Progress.get_default_columns(),
            console=self.console,
            expand=True,
        )

        # Create a task for the overall progress
        total_steps = len(steps)
        self._progress_task_id = self._progress.add_task(
            description,
            total=total_steps,
        )

        # Also track individual steps if rich is available
        self._progress_steps = steps
        self._progress.start()

        return self._progress_task_id

    def update_progress(self, completed: int, total: int, step_name: str = "", detail: str = "") -> None:
        """
        Update the progress bar.

        Args:
            completed: Number of completed steps
            total: Total number of steps
            step_name: Name of current step
            detail: Additional detail about current step
        """
        if not RICH_AVAILABLE or self._progress is None:
            # Fallback: print simple progress
            if step_name:
                self.print_info(f"正在处理: {step_name}")
                if detail:
                    print(f"  {detail}")
            return

        if self._progress_task_id is not None:
            self._progress.update(
                self._progress_task_id,
                completed=completed,
                total=total,
                description=f"正在分析: {step_name}" if step_name else "分析进度",
            )

        self._current_step = step_name
        self._current_detail = detail

    def display_live_status(self, step_name: str, step_detail: str = "") -> None:
        """
        Display live status during analysis.

        Args:
            step_name: Name of the current step
            step_detail: Additional detail about the step
        """
        if not RICH_AVAILABLE:
            self.print_info(f"正在处理: {step_name}")
            if step_detail:
                print(f"  {step_detail}")
            return

        # Update console with live status
        if step_name != self._current_step or step_detail != self._current_detail:
            self.console.print(f"[dim]⏳ {step_name}[/dim]")
            if step_detail:
                self.console.print(f"    {step_detail}", style="dim italic")
            self._current_step = step_name
            self._current_detail = step_detail

    def finish_progress(self) -> None:
        """Complete the progress tracking."""
        if not RICH_AVAILABLE or self._progress is None:
            self.print_success("分析完成!")
            return

        if self._progress_task_id is not None:
            # Ensure progress is at 100%
            self._progress.update(
                self._progress_task_id,
                completed=self._progress.tasks[0].total,
            )

        self._progress.stop()
        self._progress = None
        self._progress_task_id = None
        self.print_success("分析完成!")

    # Token statistics display methods

    def display_token_stats(self, token_tracker, show_cost: bool = True) -> None:
        """
        Display token usage statistics.

        Args:
            token_tracker: TokenTracker instance with usage data
            show_cost: Whether to show estimated cost
        """
        if token_tracker is None or token_tracker.api_calls == 0:
            self.print_info("未记录到令牌使用信息")
            return

        try:
            from .token_tracker import TokenTracker
        except ImportError:
            self.print_info("未记录到令牌使用信息")
            return

        stats = token_tracker.get_summary()

        if self.console:
            table = Table(title="📊 令牌使用统计", box=box.ROUNDED)
            table.add_column("指标", style="cyan")
            table.add_column("数值", style="green")

            table.add_row("API 调用次数", f"{stats['api_calls']:,}")
            table.add_row("输入令牌", f"{stats['input_tokens']:,}")
            table.add_row("输出令牌", f"{stats['output_tokens']:,}")
            table.add_row("总令牌数", f"{stats['total_tokens']:,}")

            if stats['api_calls'] > 0:
                avg_tokens = stats['total_tokens'] // stats['api_calls']
                table.add_row("平均令牌/调用", f"{avg_tokens:,}")

            if show_cost:
                # Estimate cost (default GPT-4 pricing)
                cost = token_tracker.estimate_cost()
                table.add_row("预估成本 (USD)", f"${cost:.4f}")

            self.console.print(table)

            # Show breakdown by operation if available
            if token_tracker.by_operation:
                self.console.print("\n[bold]按操作细分:[/bold]")
                op_table = Table(box=box.SIMPLE)
                op_table.add_column("操作", style="cyan")
                op_table.add_column("输入", style="green")
                op_table.add_column("输出", style="yellow")
                op_table.add_column("总计", style="magenta")

                sorted_ops = sorted(
                    token_tracker.by_operation.items(),
                    key=lambda x: x[1].total_tokens,
                    reverse=True,
                )

                for op, usage in sorted_ops[:10]:  # Show top 10
                    op_table.add_row(
                        op,
                        f"{usage.input_tokens:,}",
                        f"{usage.output_tokens:,}",
                        f"{usage.total_tokens:,}",
                    )

                self.console.print(op_table)
        else:
            # Fallback to simple print
            print(f"\n📊 令牌使用统计")
            print(f"  API 调用次数: {stats['api_calls']:,}")
            print(f"  输入令牌: {stats['input_tokens']:,}")
            print(f"  输出令牌: {stats['output_tokens']:,}")
            print(f"  总令牌数: {stats['total_tokens']:,}")
            if stats['api_calls'] > 0:
                avg_tokens = stats['total_tokens'] // stats['api_calls']
                print(f"  平均令牌/调用: {avg_tokens:,}")
            if show_cost:
                cost = token_tracker.estimate_cost()
                print(f"  预估成本: ${cost:.4f}")

            if token_tracker.by_operation:
                print("\n按操作细分:")
                for op, usage in sorted(
                    token_tracker.by_operation.items(),
                    key=lambda x: x[1].total_tokens,
                    reverse=True,
                ):
                    print(f"  {op}: {usage.input_tokens:,} + {usage.output_tokens:,} = {usage.total_tokens:,}")

    def _get_paper_type_label(self, paper_type: str) -> str:
        """Get human-readable label for paper type."""
        labels = {
            "survey": "综述",
            "experimental": "实验",
            "theoretical": "理论",
            "unknown": "未知"
        }
        return labels.get(paper_type, paper_type)

    def input(self, prompt: str = "") -> str:
        """Get user input."""
        if self.console:
            return self.console.input(prompt).strip()
        else:
            return input(prompt).strip()


# Global UI instance
_global_ui: Optional[UI] = None


def get_ui() -> UI:
    """Get or create the global UI instance."""
    global _global_ui
    if _global_ui is None:
        _global_ui = UI()
    return _global_ui