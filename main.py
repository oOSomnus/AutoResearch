#!/usr/bin/env python3
"""
Main Entry Point - Interactive CLI for the Paper Reading Agent.
"""
import os
import sys

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
  python main.py                    # 交互式模式
  python main.py <文件路径或URL>     # 直接分析指定文件

支持:
  - 本地PDF文件路径 (例: ./paper.pdf 或 /path/to/paper.pdf)
  - PDF URL链接 (例: https://arxiv.org/pdf/xxxx.pdf)

示例:
  python main.py ./my_paper.pdf
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

        # Run analysis
        try:
            print("\n" + "-" * 60)
            print("🚀 开始分析论文...")
            print("-" * 60)

            final_state = run_paper_analysis(user_input)

            # Summary
            print("\n" + "=" * 60)
            print("📊 分析完成!")
            print("=" * 60)
            print(f"📄 标题: {final_state['title']}")
            print(f"📁 来源: {final_state['source']}")
            print(f"\n📝 报告已生成 (Markdown格式)")

        except KeyboardInterrupt:
            print("\n\n⏸️  分析已取消")
        except Exception as e:
            print(f"\n❌ 分析过程中出错: {e}")
            import traceback
            traceback.print_exc()


def direct_mode(source: str):
    """Run the agent in direct mode with a specified source."""
    print_banner()
    print(f"📎 分析源: {source}")
    print("-" * 60)

    try:
        final_state = run_paper_analysis(source)

        # Summary
        print("\n" + "=" * 60)
        print("📊 分析完成!")
        print("=" * 60)
        print(f"📄 标题: {final_state['title']}")
        print(f"📁 来源: {final_state['source']}")
        print(f"\n📝 报告已生成 (Markdown格式)")

    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg in ['-h', '--help', 'help']:
            print_help()
            sys.exit(0)

        direct_mode(arg)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()