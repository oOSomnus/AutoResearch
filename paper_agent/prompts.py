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

PAPER_TYPE_DETECTION_PROMPT = """你是一个论文分类助手。请根据以下论文的标题和内容摘要，判断论文的类型。

论文标题：{title}
内容摘要：{content}

请从以下四个类型中选择最合适的一个，**仅输出类型名称**：

1. **survey** - 综述类论文：主要总结和梳理已有研究，分析领域发展脉络和趋势
2. **experimental** - 实验类论文：通过实验验证新方法的有效性，包含详细的实验设置、结果对比和数据分析
3. **theoretical** - 理论类论文：提出新的理论框架、数学证明或算法分析，侧重理论推导而非实验验证
4. **unknown** - 其他或无法确定类型

请直接输出以下类型之一：survey, experimental, theoretical, unknown
"""

METHODOLOGY_ANALYSIS_PROMPT = """你是一个擅长用简单易懂的语言解释实验方法的助手。请仔细阅读下面的论文内容，然后回答：**他们是怎么做的？实验方法是什么？**

论文内容：
{content}

要求：
1. 用非常简单、口语化的语言解释实验设计和分析方法
2. 说明使用了哪些数据集、评价指标、对比方法
3. 解释实验设置的关键参数和条件
4. 用1-3段话总结，不要太长
5. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

RELATED_WORK_ANALYSIS_PROMPT = """你是一个擅长用简单易懂的语言解释相关研究的助手。请仔细阅读下面的论文内容，然后回答：**这个研究与已有研究有什么关系？相关工作有哪些？**

论文内容：
{content}

要求：
1. 用非常简单、口语化的语言说明该研究在学术脉络中的位置
2. 提及几个重要的相关工作或方法
3. 说明这些相关工作的不足或局限性
4. 说明当前研究如何改进或超越这些工作
5. 用2-3段话总结，不要太长
6. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

LIMITATIONS_ANALYSIS_PROMPT = """你是一个擅长识别研究局限性的助手。请仔细阅读下面的论文内容，然后回答：**这个研究有什么不足？有什么限制？**

论文内容：
{content}

要求：
1. 用非常简单、口语化的语言说明研究可能存在的局限性
2. 指出方法、实验或结论的不足之处
3. 提及作者自己讨论的局限性或未来工作方向
4. 用1-2段话总结，简洁明了
5. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

REPORT_GENERATION_PROMPT = """你是一个擅长撰写简洁清晰报告的助手。根据以下关于论文的分析，生成一份Markdown格式的易懂报告。

论文标题：{title}
来源：{source}
论文类型：{paper_type}

背景分析：
{background}

创新分析：
{innovation}

结果分析：
{results}

{methodology_section}

{related_work_section}

{limitations_section}

要求：
1. 使用Markdown格式
2. 长度要求差异化：
   - **背景&原因**：保持简洁，100-200字即可
   - **创新&核心理论**：详细展开，400-800字，这是报告的核心
   - **结果**：保持简洁，100-200字即可
   - **其他章节**：根据实际内容调整长度
3. 语言要非常易懂，避免学术化表达
4. 使用适当的格式（加粗、列表、小标题等）增强可读性
5. 创新部分可以使用小标题或列表来组织内容
6. 根据论文类型和分析结果动态调整报告结构：
   - 实验论文包含"实验方法"章节
   - 综述论文包含"相关工作"章节
   - 理论论文包含"局限性"章节
7. 报告结构如下：

# 论文分析报告

## 原始信息
- 来源: [来源]
- 标题: [标题]
- 类型: [类型]

## 一、背景&原因
[简洁说明研究背景和动机]

## 二、创新&核心理论
[详细展开，可以包含多个小节]

## 三、结果
[简洁总结主要发现]

{additional_sections}

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

def get_paper_type_detection_prompt(title: str, content: str) -> str:
    """Get the paper type detection prompt with content filled in."""
    # Slice content to first 2000 chars before formatting
    content_preview = content[:2000] if len(content) > 2000 else content
    return PAPER_TYPE_DETECTION_PROMPT.format(title=title or "未知", content=content_preview)

def get_methodology_prompt(content: str) -> str:
    """Get the methodology analysis prompt with content filled in."""
    return METHODOLOGY_ANALYSIS_PROMPT.format(content=content)

def get_related_work_prompt(content: str) -> str:
    """Get the related work analysis prompt with content filled in."""
    return RELATED_WORK_ANALYSIS_PROMPT.format(content=content)

def get_limitations_prompt(content: str) -> str:
    """Get the limitations analysis prompt with content filled in."""
    return LIMITATIONS_ANALYSIS_PROMPT.format(content=content)

def get_report_prompt(
    title: str,
    source: str,
    background: str,
    innovation: str,
    results: str,
    paper_type: str = "unknown",
    methodology: str = "",
    related_work: str = "",
    limitations: str = ""
) -> str:
    """Get the report generation prompt with all information filled in."""
    # Build additional sections dynamically
    additional_sections = []

    if methodology:
        additional_sections.append("\n## 四、实验方法\n" + methodology)

    if related_work:
        additional_sections.append("\n## 四、相关工作\n" + related_work)

    if limitations:
        additional_sections.append("\n## 四、局限性\n" + limitations)

    additional_sections_text = "".join(additional_sections)

    return REPORT_GENERATION_PROMPT.format(
        title=title or "未知",
        source=source,
        paper_type=paper_type,
        background=background,
        innovation=innovation,
        results=results,
        methodology_section=methodology if methodology else "",
        related_work_section=related_work if related_work else "",
        limitations_section=limitations if limitations else "",
        additional_sections=additional_sections_text
    )