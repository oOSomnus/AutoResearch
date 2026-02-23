"""
Code Extractor - Extract code and algorithms from papers.
"""
import re
from typing import List, Dict, Any

from ..types import CodeSnippet
from ..pdf_reader import extract_pdf_text


class CodeExtractor:
    """Extract code and algorithms from paper content."""

    def __init__(self):
        """Initialize the code extractor."""
        # Algorithm patterns
        self.algorithm_patterns = [
            r'Algorithm\s+\d+[:\.\-]\s*(.+)',
            r'算法\s+\d+[:\.\-]\s*(.+)',
            r'Alg\.\s*\d+[:\.\-]\s*(.+)',
        ]

        # Code block patterns
        self.code_patterns = [
            r'```(\w+)?\n([\s\S]+?)```',
            r'```([\s\S]+?)```',
        ]

        # Common programming languages
        self.language_keywords = {
            "python": ["python", "def ", "import ", "class ", "elif "],
            "pseudocode": ["pseudocode", "伪代码"],
            "algorithm": ["algorithm", "算法"],
            "java": ["java", "public class"],
            "cpp": ["c++", "cpp", "include <", "std::"],
            "javascript": ["javascript", "function ", "const "],
            "sql": ["sql", "select ", "from "],
        }

    def extract_code(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract code from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted code and analysis
        """
        content = extract_pdf_text(pdf_path)

        # Find algorithms and code blocks
        algorithms = self._find_algorithms(content)
        code_blocks = self._find_code_blocks(content)

        # Combine all code snippets
        all_snippets = algorithms + code_blocks

        # Generate analysis text
        analysis_text = self._generate_analysis_text(all_snippets)

        return {
            "code": analysis_text,
            "code_snippets": all_snippets,
            "algorithm_count": len(algorithms),
            "code_block_count": len(code_blocks)
        }

    def _find_algorithms(self, content: str) -> List[CodeSnippet]:
        """Find algorithms in the content."""
        snippets = []

        for pattern in self.algorithm_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()

                # Extract algorithm content (text after the algorithm header)
                start = match.end()
                end = min(len(content), match.end() + 1000)
                algorithm_content = content[start:end].strip()

                # Clean up the content
                algorithm_content = self._clean_code_content(algorithm_content)

                if algorithm_content:
                    snippets.append(CodeSnippet(
                        page_num=0,
                        language="algorithm",
                        code=algorithm_content[:500],
                        description=name,
                        is_algorithm=True,
                        algorithm_name=name
                    ))

        return snippets

    def _find_code_blocks(self, content: str) -> List[CodeSnippet]:
        """Find code blocks in the content."""
        snippets = []

        # Try markdown-style code blocks
        for pattern in self.code_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                language = match.group(1) or "unknown"
                code_content = match.group(2).strip()

                # Determine actual language
                detected_lang = self._detect_language(code_content)
                if detected_lang != "unknown":
                    language = detected_lang

                if code_content and len(code_content) > 20:  # Minimum meaningful length
                    # Extract context
                    start = max(0, match.start() - 200)
                    context = content[start:match.start()].strip()

                    # Extract description from context
                    description = self._extract_description(context)

                    snippets.append(CodeSnippet(
                        page_num=0,
                        language=language,
                        code=code_content[:500],
                        description=description,
                        is_algorithm=False
                    ))

        return snippets

    def _detect_language(self, code: str) -> str:
        """Detect the programming language from code content."""
        code_lower = code.lower()

        for language, keywords in self.language_keywords.items():
            for keyword in keywords:
                if keyword.lower() in code_lower:
                    return language

        return "unknown"

    def _extract_description(self, context: str) -> str:
        """Extract description from context text."""
        # Look for sentences ending with colon or period
        sentences = re.split(r'[。.:；:]', context[-100:])
        if sentences:
            return sentences[-1].strip()
        return ""

    def _clean_code_content(self, content: str) -> str:
        """Clean up code content."""
        # Remove excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Remove non-printable characters
        content = ''.join(c for c in content if c.isprintable() or c in '\n\t ')

        return content.strip()

    def _generate_analysis_text(self, snippets: List[CodeSnippet]) -> str:
        """Generate analysis text from code snippets."""
        parts = ["## 代码片段"]

        if not snippets:
            parts.append("\n未在论文中找到显著的代码或算法描述。")
            return "\n".join(parts)

        # Separate algorithms and code
        algorithms = [s for s in snippets if s.is_algorithm]
        code = [s for s in snippets if not s.is_algorithm]

        # Algorithm analysis
        if algorithms:
            parts.append(f"\n### 算法 ({len(algorithms)} 个)")

            parts.append("\n**主要算法：**")
            for alg in algorithms:
                name = alg.algorithm_name or "未命名算法"
                parts.append(f"- **{name}**")
                if alg.description:
                    parts.append(f"  {alg.description}")

                # Show first few lines
                lines = alg.code.split('\n')[:3]
                for line in lines:
                    if line.strip():
                        parts.append(f"  `{line.strip()}`")
                parts.append("")

        # Code analysis
        if code:
            parts.append(f"\n### 代码 ({len(code)} 个)")

            # Group by language
            lang_counts = {}
            for snippet in code:
                lang = snippet.language
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

            for lang, count in lang_counts.items():
                parts.append(f"- **{lang}**: {count} 段代码")

            # List key code snippets
            if code:
                parts.append("\n**主要代码片段：**")
                for snippet in code[:5]:
                    if snippet.description:
                        parts.append(f"- {snippet.description}")

        return "\n".join(parts)