"""
Prompt Templates - Templates for analyzing paper content in simple, accessible language.
"""

BACKGROUND_ANALYSIS_PROMPT = """你是一个擅长用简单易懂的语言解释学术研究的助手。请仔细阅读下面的论文内容，然后回答：**为什么做这个研究？背景是什么？**

论文内容：
{content}

要求：
1. 用非常简单、口语化的语言解释，就像给高中毕业生讲解一样
2. 避免使用过于专业的术语，如果必须使用，要给出简单的解释
3. 突出研究者面临的"问题"或"痛点"
4. 说明为什么这个问题值得研究
5. 用1-3段话总结，不要太长
6. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

INNOVATION_ANALYSIS_PROMPT = """你是一个擅长用简单易懂的语言解释学术创新的助手。请仔细阅读下面的论文内容，然后回答：**有什么新的贡献或创新点？核心理论是什么？**

论文内容：
{content}

要求：
1. 用非常简单、口语化的语言解释，就像给高中毕业生讲解一样
2. 避免使用过于专业的术语，如果必须使用，要给出简单的解释或举例子
3. 用简单的比喻或类比来帮助理解核心思想（如果适用）
4. 说明这个方法和已有方法的主要区别
5. **详细展开**：这部分需要比背景和结果更详细，可以分成多个小节来说明
6. 用列表或分段的方式组织内容，便于阅读
7. 涵盖以下方面（如果论文中有）：
   - 核心算法/方法的原理（用通俗语言）
   - 模型架构的关键组件
   - 训练策略或数据集设计
   - 与现有方法的对比优势
8. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

RESULTS_ANALYSIS_PROMPT = """你是一个擅长用简单易懂的语言总结研究结果的助手。请仔细阅读下面的论文内容，然后回答：**结论是什么？得到了什么结果？**

论文内容：
{content}

要求：
1. 用非常简单、口语化的语言总结，就像给高中毕业生讲解一样
2. 清晰地说明主要发现和结论
3. 避免列出大量数字，用定性的方式描述趋势和结果
4. 说明这些结果有什么实际意义或价值
5. 用1-3段话总结，不要太长
6. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

REPORT_GENERATION_PROMPT = """你是一个擅长撰写简洁清晰报告的助手。根据以下关于论文的三部分分析，生成一份Markdown格式的易懂报告。

论文标题：{title}
来源：{source}

背景分析：
{background}

创新分析：
{innovation}

结果分析：
{results}

要求：
1. 使用Markdown格式
2. 长度要求差异化：
   - **背景&原因**：保持简洁，100-200字即可
   - **创新&核心理论**：详细展开，400-800字，这是报告的核心
   - **结果**：保持简洁，100-200字即可
3. 语言要非常易懂，避免学术化表达
4. 使用适当的格式（加粗、列表、小标题等）增强可读性
5. 创新部分可以使用小标题或列表来组织内容
6. 报告结构如下：

# 论文分析报告

## 原始信息
- 来源: [来源]
- 标题: [标题]

## 一、背景&原因
[简洁说明研究背景和动机]

## 二、创新&核心理论
[详细展开，可以包含多个小节]

## 三、结果
[简洁总结主要发现]

请直接输出完整的Markdown报告，不要输出任何其他内容。
"""

def get_background_prompt(content: str) -> str:
    """Get the background analysis prompt with content filled in."""
    return BACKGROUND_ANALYSIS_PROMPT.format(content=content)

def get_innovation_prompt(content: str) -> str:
    """Get the innovation analysis prompt with content filled in."""
    return INNOVATION_ANALYSIS_PROMPT.format(content=content)

def get_results_prompt(content: str) -> str:
    """Get the results analysis prompt with content filled in."""
    return RESULTS_ANALYSIS_PROMPT.format(content=content)

def get_report_prompt(title: str, source: str, background: str, innovation: str, results: str) -> str:
    """Get the report generation prompt with all information filled in."""
    return REPORT_GENERATION_PROMPT.format(
        title=title or "未知",
        source=source,
        background=background,
        innovation=innovation,
        results=results
    )