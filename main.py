#!/usr/bin/env python3
"""
Main Entry Point - Interactive CLI for the Paper Reading Agent.
Supports multiple output formats, languages, and detail levels.
"""
import os
import sys
import argparse

from paper_agent.graph import run_paper_analysis


def print_banner():
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
    print(banner)


def print_help():
    """Print usage help."""
    help_text = """
用法:
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
    print(help_text)


def interactive_mode():
    """Run the agent in interactive mode."""
    print_banner()

    while True:
        print("\n" + "=" * 60)
        print("请输入PDF文件路径或URL (输入 'q' 退出, 'h' 查看帮助):")
        user_input = input("> ").strip()

        # Handle commands
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("\n👋 感谢使用，再见！")
            break

        if user_input.lower() in ['h', 'help']:
            print_help()
            continue

        if not user_input:
            print("⚠️  请输入有效的文件路径或URL")
            continue

        # Check if it's a URL or local file
        if user_input.startswith(('http://', 'https://')):
            print(f"📎 检测到URL: {user_input}")
        else:
            # Check if file exists
            if not os.path.exists(user_input):
                print(f"❌ 文件不存在: {user_input}")
                continue
            print(f"📎 本地文件: {user_input}")

        # Run analysis with default settings
        try:
            print("\n" + "-" * 60)
            print("🚀 开始分析论文...")
            print("-" * 60)

            # Ask for output format preference
            print("\n输出格式选项:")
            print("1. Markdown (默认)")
            print("2. HTML")
            print("3. PDF")
            print("4. JSON")
            format_choice = input("请选择 (1-4, 按Enter使用默认): ").strip()

            format_map = {"1": "markdown", "2": "html", "3": "pdf", "4": "json"}
            output_format = format_map.get(format_choice, "markdown")

            # Ask for language preference
            print("\n语言选项:")
            print("1. 中文 (默认)")
            print("2. English")
            lang_choice = input("请选择 (1-2, 按Enter使用默认): ").strip()

            language = "en" if lang_choice == "2" else "zh"

            # Ask for detail level
            print("\n详细程度选项:")
            print("1. Brief - 简洁")
            print("2. Standard (默认)")
            print("3. Detailed - 详细")
            detail_choice = input("请选择 (1-3, 按Enter使用默认): ").strip()

            detail_map = {"1": "brief", "2": "standard", "3": "detailed"}
            detail_level = detail_map.get(detail_choice, "standard")

            final_state = run_paper_analysis(
                user_input,
                output_format=output_format,
                language=language,
                detail_level=detail_level
            )

            # Summary
            print("\n" + "=" * 60)
            print("📊 分析完成!")
            print("=" * 60)
            print(f"📄 标题: {final_state.get('title', '未知')}")
            print(f"📁 来源: {final_state.get('source', '')}")
            print(f"📋 格式: {output_format}")
            print(f"🌐 语言: {language}")
            print(f"📊 详细程度: {detail_level}")
            print(f"\n📝 报告已生成")

        except KeyboardInterrupt:
            print("\n\n⏸️  分析已取消")
        except Exception as e:
            print(f"\n❌ 分析过程中出错: {e}")
            import traceback
            traceback.print_exc()


def direct_mode(source: str, output_format: str = "markdown",
               language: str = "zh", detail_level: str = "standard",
               checkpoint_path: str | None = None,
               extract_citations: bool = False,
               analyze_figures: bool = False,
               extract_code: bool = False,
               assess_reproducibility: bool = False,
               qa_mode: bool = False):
    """Run the agent in direct mode with a specified source."""
    print_banner()
    print(f"📎 分析源: {source}")
    print(f"📋 输出格式: {output_format}")
    print(f"🌐 语言: {language}")
    print(f"📊 详细程度: {detail_level}")

    if checkpoint_path:
        print(f"📋 从检查点恢复: {checkpoint_path}")

    extraction_features = []
    if extract_citations:
        extraction_features.append("引用分析")
    if analyze_figures:
        extraction_features.append("图表分析")
    if extract_code:
        extraction_features.append("代码提取")
    if assess_reproducibility:
        extraction_features.append("可复现性评估")
    if qa_mode:
        extraction_features.append("问答模式")

    if extraction_features:
        print(f"🔧 启用功能: {', '.join(extraction_features)}")

    print("-" * 60)

    try:
        final_state = run_paper_analysis(
            source,
            output_format=output_format,
            language=language,
            detail_level=detail_level,
            checkpoint_path=checkpoint_path
        )

        # If QA mode is enabled, run interactive Q&A
        if qa_mode and final_state.get("report"):
            from paper_agent.qa_mode import interactive_qa_loop
            # Index the paper for Q&A
            from paper_agent.qa_mode import QAMode
            qa = QAMode()
            paper_id = qa.index_paper(final_state)
            if paper_id:
                print("\n" + "=" * 60)
                interactive_qa_loop(paper_id)

        # Summary
        print("\n" + "=" * 60)
        print("📊 分析完成!")
        print("=" * 60)
        print(f"📄 标题: {final_state.get('title', '未知')}")
        print(f"📁 来源: {final_state.get('source', '')}")
        print(f"📋 格式: {output_format}")
        print(f"🌐 语言: {language}")
        print(f"📊 详细程度: {detail_level}")
        print(f"\n📝 报告已生成")

    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="论文阅读 Agent - 快速理解论文核心内容",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Positional argument for paper source
    parser.add_argument(
        'source',
        nargs='?',
        help='PDF文件路径或URL'
    )

    # Output format options
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html', 'pdf', 'json'],
        default='markdown',
        help='输出格式 (默认: markdown)'
    )

    parser.add_argument(
        '--language', '-l',
        choices=['zh', 'en'],
        default='zh',
        help='语言 (默认: zh)'
    )

    parser.add_argument(
        '--detail', '-d',
        choices=['brief', 'standard', 'detailed'],
        default='standard',
        help='详细程度 (默认: standard)'
    )

    # Checkpoint and resume options
    parser.add_argument(
        '--resume',
        metavar='PATH',
        help='从检查点恢复分析'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='清除缓存'
    )

    # Batch processing options
    parser.add_argument(
        '--batch',
        metavar='FILE',
        help='批量处理文件 (每行一个PDF路径或URL)'
    )

    # History options
    parser.add_argument(
        '--history',
        action='store_true',
        help='查看分析历史'
    )

    # Q&A mode
    parser.add_argument(
        '--qa-mode',
        action='store_true',
        help='启用交互式问答模式'
    )

    # Phase 4: New extraction options
    parser.add_argument(
        '--extract-citations',
        action='store_true',
        help='启用引用提取和分析'
    )

    parser.add_argument(
        '--analyze-figures',
        action='store_true',
        help='启用图表分析'
    )

    parser.add_argument(
        '--extract-code',
        action='store_true',
        help='启用代码提取'
    )

    parser.add_argument(
        '--assess-reproducibility',
        action='store_true',
        help='启用可复现性评估'
    )

    # Multi-paper comparison
    parser.add_argument(
        '--compare',
        nargs='+',
        metavar='PDF',
        help='对比多个论文'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Handle clear cache
    if args.clear_cache:
        from paper_agent.cache import get_cache_manager
        cache_mgr = get_cache_manager()
        cache_mgr.clear()
        print("✅ 缓存已清除")
        if not args.source and not args.history and not args.batch:
            return

    # Handle history
    if args.history:
        from paper_agent.history import get_history_manager
        history_mgr = get_history_manager()
        entries = history_mgr.list_entries(limit=20)
        print_history(entries)
        return

    # Handle batch processing
    if args.batch:
        from paper_agent.batch import BatchProcessor
        processor = BatchProcessor(max_workers=2)
        sources = load_batch_file(args.batch)
        if not sources:
            print("❌ 批量文件为空或无效")
            return
        results = processor.process(sources)
        for result in results:
            if result.success:
                print(f"✅ {os.path.basename(result.source)}")
            else:
                print(f"❌ {os.path.basename(result.source)}: {result.error}")
        return

    # Handle comparison
    if args.compare:
        from paper_agent.comparison import PaperComparison
        if len(args.compare) < 2:
            print("❌ 至少需要2篇论文才能进行对比")
            return
        comparator = PaperComparison()
        comparison_result = comparator.compare_papers(args.compare)
        print("\n" + comparison_result["comparison"])
        return

    # Handle single paper analysis or resume
    if args.source or args.resume:
        source = args.source if args.source else ""

        # If resume, the source will come from the checkpoint
        checkpoint_path = args.resume if args.resume else None

        direct_mode(
            source,
            output_format=args.format,
            language=args.language,
            detail_level=args.detail,
            checkpoint_path=checkpoint_path,
            extract_citations=args.extract_citations,
            analyze_figures=args.analyze_figures,
            extract_code=args.extract_code,
            assess_reproducibility=args.assess_reproducibility,
            qa_mode=args.qa_mode
        )
    else:
        interactive_mode()


def print_history(entries):
    """Print analysis history entries."""
    if not entries:
        print("📝 暂无历史记录")
        return

    print("\n" + "=" * 80)
    print(f"📚 分析历史 (最近{len(entries)}条)")
    print("=" * 80)
    print(f"{'ID':<5} {'标题':<35} {'类型':<10} {'语言':<5} {'时间':<20}")
    print("-" * 80)

    for entry in entries:
        title = entry.get("title", "未知")[:34]
        paper_type = entry.get("paper_type", "unknown")[:10]
        language = entry.get("language", "zh")[:5]
        analyzed_at = entry.get("analyzed_at", "")[:19]
        print(f"{str(entry.get('id', '')):<5} {title:<35} {paper_type:<10} {language:<5} {analyzed_at:<20}")


def load_batch_file(file_path):
    """Load paper sources from batch file."""
    sources = []
    if not os.path.exists(file_path):
        print(f"❌ 批量文件不存在: {file_path}")
        return sources

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                sources.append(line)

    return sources


if __name__ == "__main__":
    main()