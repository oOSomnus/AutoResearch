"""
Comparison Module - Compare multiple papers.
"""
from typing import List, Dict, Any, Optional

from .types import ComparisonResult
from .pdf_reader import extract_pdf_text
from .prompts import get_prompt_template


class PaperComparison:
    """Compare multiple papers."""

    def __init__(self):
        """Initialize the paper comparison."""
        pass

    def compare_papers(self, pdf_paths: List[str],
                      comparison_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Compare multiple papers.

        Args:
            pdf_paths: List of PDF file paths
            comparison_type: Type of comparison (methodology, results, comprehensive)

        Returns:
            Dictionary with comparison results
        """
        if len(pdf_paths) < 2:
            raise ValueError("至少需要2篇论文才能进行对比")

        # Extract basic info from each paper
        paper_info = []
        for i, pdf_path in enumerate(pdf_paths):
            try:
                content = extract_pdf_text(pdf_path)
                paper_info.append({
                    "id": f"paper_{i+1}",
                    "path": pdf_path,
                    "content": content[:5000],  # Limit content for comparison
                    "title": self._extract_title(content)
                })
            except Exception as e:
                print(f"警告: 无法读取论文 {pdf_path}: {e}")
                continue

        if len(paper_info) < 2:
            raise ValueError("能够成功读取的论文少于2篇")

        # Generate comparison using LLM
        comparison_text = self._generate_llm_comparison(paper_info, comparison_type)

        # Create comparison result
        result = ComparisonResult(
            paper_ids=[p["id"] for p in paper_info],
            comparison_type=comparison_type,
            similarities=[],
            differences=[],
            ranking=[],
            summary=comparison_text
        )

        return {
            "comparison": comparison_text,
            "comparison_result": result,
            "paper_info": paper_info
        }

    def _extract_title(self, content: str) -> str:
        """Extract title from content."""
        lines = content.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if line and len(line) > 5 and len(line) < 200:
                if not line.lower().startswith(('abstract', 'introduction')):
                    return line
        return "未知标题"

    def _generate_llm_comparison(self, paper_info: List[Dict],
                                 comparison_type: str) -> str:
        """Generate comparison using LLM."""
        from langchain_openai import ChatOpenAI
        from dotenv import load_dotenv
        import os

        load_dotenv()

        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("MODEL_NAME", "gpt-4")

        llm = ChatOpenAI(
            openai_api_base=api_base,
            openai_api_key=api_key,
            model=model_name,
            temperature=0.3
        )

        # Build comparison prompt
        prompt = self._build_comparison_prompt(paper_info, comparison_type)

        try:
            response = llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            # Fallback to simple comparison
            return self._generate_simple_comparison(paper_info)

    def _build_comparison_prompt(self, paper_info: List[Dict],
                                comparison_type: str) -> str:
        """Build the comparison prompt for LLM."""
        # Format paper info for the prompt
        paper_descriptions = []
        for p in paper_info:
            paper_descriptions.append(
                f"论文 {p['id']}: {p['title']}\n"
                f"内容概要: {p['content'][:1500]}..."
            )

        papers_text = "\n\n".join(paper_descriptions)

        comparison_guides = {
            "comprehensive": """
请从以下方面进行全面对比：
1. 研究背景和动机的相似性与差异
2. 方法论和核心算法的区别
3. 实验设置和数据集的对比
4. 结果和结论的异同
5. 各自的优势和局限性
""",
            "methodology": """
请重点对比以下方面：
1. 核心方法和算法的差异
2. 模型架构或流程的区别
3. 关键技术的异同
""",
            "results": """
请重点对比以下方面：
1. 实验结果的差异
2. 评估指标和性能对比
3. 结论的异同
"""
        }

        guide = comparison_guides.get(comparison_type, comparison_guides["comprehensive"])

        prompt = f"""你是一个擅长对比分析的助手。请仔细阅读以下几篇论文的内容，然后进行对比分析。

{papers_text}

对比要求：
1. 用简单易懂的语言进行对比
2. 突出每篇论文的独特之处
3. 指出相似之处和差异
4. 给出客观的评价
5. 用列表和分段组织内容，便于阅读

{guide}

请直接输出对比分析结果，不要输出任何其他内容。
"""

        return prompt

    def _generate_simple_comparison(self, paper_info: List[Dict]) -> str:
        """Generate a simple comparison without LLM."""
        parts = ["## 多论文对比分析"]

        parts.append("\n### 论文列表")
        for p in paper_info:
            parts.append(f"- **{p['id']}**: {p['title']}")

        parts.append("\n### 对比说明")
        parts.append("由于无法访问LLM服务，以下是基本信息对比：")
        parts.append("- 各论文的基本信息已列出")
        parts.append("- 建议手动阅读各论文进行详细对比")

        return "\n".join(parts)