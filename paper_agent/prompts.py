"""
Prompt Templates - Templates for analyzing paper content in simple, accessible language.
Supports both Chinese (zh) and English (en) languages.
"""

# Chinese Prompts (Default)

# Title extraction prompt (new)
TITLE_EXTRACTION_PROMPT_ZH = """你是一个擅长识别论文标题的助手。请从以下论文第一页内容中提取论文标题。

内容（前3000字）：
{first_page_content}

要求：
1. 仔细识别标题，标题通常在页面的顶部中央或左侧
2. 标题会比其他文字更醒目（虽然无法看到格式，但可以通过位置判断）
3. 排除作者姓名、单位、"Abstract"、"Introduction"等非标题内容
4. 如果多行看起来是标题，提取完整的标题
5. 如果无法确定，返回空字符串

只输出标题文本，不要输出任何其他内容。
"""

TITLE_EXTRACTION_PROMPT_EN = """Extract the paper title from the following first page content.

Content (first 3000 chars):
{first_page_content}

Requirements:
1. Carefully identify the title, which is typically at the top center or left of the page
2. The title is usually more prominent (though we can't see formatting, use position as a clue)
3. Exclude author names, affiliations, "Abstract", "Introduction", and other non-title content
4. If multiple lines appear to be the title, extract the complete title
5. If you cannot determine the title, return an empty string

Output ONLY the title text, nothing else.
"""

# Content with figures prompt (new)
CONTENT_WITH_FIGURES_PROMPT_ZH = """你是一个论文分析助手。请基于以下论文内容和图表信息进行分析。

论文内容：
{content}

图表信息：
{figures_info}

要求：
1. 在分析中引用相关的图表（例如："如图1所示"、"表2中的数据显示..."）
2. 说明图表的关键信息对结论的支持作用
3. 如果公式存在，用自然语言解释公式的含义
4. 如果需要，可以引用图表中的具体数值或趋势
"""

CONTENT_WITH_FIGURES_PROMPT_EN = """You are a paper analysis assistant. Please analyze based on the following paper content and figure/table information.

Paper content:
{content}

Figure/table information:
{figures_info}

Requirements:
1. Reference relevant figures/tables in your analysis (e.g., "As shown in Figure 1", "The data in Table 2 shows...")
2. Explain how key information from figures supports the conclusions
3. If formulas exist, explain their meaning in natural language
4. If needed, reference specific values or trends from figures
"""

# Chinese Prompts (Default)

BACKGROUND_ANALYSIS_PROMPT_ZH = """你是一个擅长用简单易懂的语言解释学术研究的助手。请仔细阅读下面的论文内容，然后回答：**为什么做这个研究？背景是什么？**

论文内容：
{content}

要求：
1. 用非常简单、口语化的语言解释，就像给高中毕业生讲解一样
2. 避免使用过于专业的术语，如果必须使用，要给出简单的解释
3. 突出研究者面临的"问题"或"痛点"
4. 说明为什么这个问题值得研究
5. **具体说明**：提及论文中提到的具体问题陈述、数据或统计信息（如果存在）
6. 用1-3段话总结，不要太长
7. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

INNOVATION_ANALYSIS_PROMPT_ZH = """你是一个擅长用简单易懂的语言解释学术创新的助手。请仔细阅读下面的论文内容，然后回答：**有什么新的贡献或创新点？核心理论是什么？**

论文内容：
{content}
{figures_context}

要求：
1. **首先用简单、口语化的语言介绍核心思想**（1-2段），就像给高中毕业生讲解一样
2. **然后详细展开具体实现**：
   - 逐步说明算法或方法的实现步骤
   - 描述模型架构的关键组件
   - 说明训练策略或数据集设计
3. 使用简单的比喻或类比来帮助理解核心思想（如果适用）
4. 说明这个方法和已有方法的主要区别
5. **引用具体细节**：
   - 如果有公式，用自然语言解释公式的含义
   - 如果有图表，在分析中引用（例如："如图1所示"、"表2中的数据显示..."）
   - 提及关键参数、设计选择或技术细节
6. 用列表或分段的方式组织内容，便于阅读
7. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

RESULTS_ANALYSIS_PROMPT_ZH = """你是一个擅长用简单易懂的语言总结研究结果的助手。请仔细阅读下面的论文内容，然后回答：**结论是什么？得到了什么结果？**

论文内容：
{content}
{figures_context}

要求：
1. 用非常简单、口语化的语言总结，就像给高中毕业生讲解一样
2. 清晰地说明主要发现和结论
3. **包含具体定量数据**：
   - 提及关键性能指标（准确率、F1分数、召回率等）
   - 引用对比数据（比基线方法提升X%）
   - 引用具体数字（例如："在X数据集上达到Y%的准确率"）
4. **引用图表**：在结果中引用相关的表或图（例如："如表1所示"、"图2展示了..."）
5. 说明这些结果有什么实际意义或价值
6. 用1-3段话总结，不要太长
7. 如果内容信息不足，如实说明

请直接输出分析结果，不要输出任何其他内容。
"""

PAPER_TYPE_DETECTION_PROMPT_ZH = """你是一个论文分类助手。请根据以下论文的标题和内容摘要，判断论文的类型。

论文标题：{title}
内容摘要：{content}

请从以下四个类型中选择最合适的一个，**仅输出类型名称**：

1. **survey** - 综述类论文：主要总结和梳理已有研究，分析领域发展脉络和趋势
2. **experimental** - 实验类论文：通过实验验证新方法的有效性，包含详细的实验设置、结果对比和数据分析
3. **theoretical** - 理论类论文：提出新的理论框架、数学证明或算法分析，侧重理论推导而非实验验证
4. **unknown** - 其他或无法确定类型

请直接输出以下类型之一：survey, experimental, theoretical, unknown
"""

METHODOLOGY_ANALYSIS_PROMPT_ZH = """你是一个擅长用简单易懂的语言解释实验方法的助手。请仔细阅读下面的论文内容，然后回答：**他们是怎么做的？实验方法是什么？**

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

RELATED_WORK_ANALYSIS_PROMPT_ZH = """你是一个擅长用简单易懂的语言解释相关研究的助手。请仔细阅读下面的论文内容，然后回答：**这个研究与已有研究有什么关系？相关工作有哪些？**

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

LIMITATIONS_ANALYSIS_PROMPT_ZH = """你是一个擅长识别研究局限性的助手。请仔细阅读下面的论文内容，然后回答：**这个研究有什么不足？有什么限制？**

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

REPORT_GENERATION_PROMPT_ZH = """你是一个擅长撰写简洁清晰报告的助手。根据以下关于论文的分析，生成一份Markdown格式的易懂报告。

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

# English Prompts

BACKGROUND_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in explaining academic research in simple, easy-to-understand language. Please carefully read the following paper content and answer: **Why was this research done? What is the background?**

Paper content:
{content}

Requirements:
1. Use very simple, conversational language, like explaining to a high school graduate
2. Avoid overly technical terminology; if necessary, provide simple explanations
3. Highlight the "problem" or "pain point" the researchers are facing
4. Explain why this problem is worth studying
5. **Be specific**: Mention specific problem statements, data, or statistics from the paper (if present)
6. Summarize in 1-3 paragraphs, don't be too long
7. If content information is insufficient, state so honestly

Please output the analysis results directly, do not output any other content.
"""

INNOVATION_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in explaining academic innovations in simple, easy-to-understand language. Please carefully read the following paper content and answer: **What are the new contributions or innovations? What is the core theory?**

Paper content:
{content}
{figures_context}

Requirements:
1. **First, introduce the core idea in simple, conversational language** (1-2 paragraphs), like explaining to a high school graduate
2. **Then detail the specific implementation**:
   - Explain the algorithm or method step-by-step
   - Describe key components of the model architecture
   - Explain training strategy or dataset design
3. Use simple metaphors or analogies to help understand the core idea (if applicable)
4. Explain the main differences between this method and existing methods
5. **Reference specific details**:
   - If formulas exist, explain their meaning in natural language
   - If figures exist, reference them in your analysis (e.g., "As shown in Figure 1", "The data in Table 2 shows...")
   - Mention key parameters, design choices, or technical details
6. Organize content with lists or paragraphs for easy reading
7. If content information is insufficient, state so honestly

Please output the analysis results directly, do not output any other content.
"""

RESULTS_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in summarizing research results in simple, easy-to-understand language. Please carefully read the following paper content and answer: **What is the conclusion? What were the results?**

Paper content:
{content}
{figures_context}

Requirements:
1. Summarize using very simple, conversational language, like explaining to a high school graduate
2. Clearly state the main findings and conclusions
3. **Include specific quantitative data**:
   - Mention key performance metrics (accuracy, F1 score, recall, etc.)
   - Reference comparison data (X% improvement over baseline)
   - Reference specific numbers (e.g., "achieved Y% accuracy on X dataset")
4. **Reference figures and tables**: Reference relevant tables or figures in your results (e.g., "As shown in Table 1", "Figure 2 shows...")
5. Explain the practical significance or value of these results
6. Summarize in 1-3 paragraphs, don't be too long
7. If content information is insufficient, state so honestly

Please output the analysis results directly, do not output any other content.
"""

PAPER_TYPE_DETECTION_PROMPT_EN = """You are a paper classification assistant. Please determine the paper type based on the following paper title and content summary.

Paper title: {title}
Content summary: {content}

Please select the most appropriate one from the following four types, **output ONLY the type name**:

1. **survey** - Survey paper: mainly summarizes and organizes existing research, analyzes development trends in the field
2. **experimental** - Experimental paper: validates new methods through experiments, including detailed experimental settings, result comparisons, and data analysis
3. **theoretical** - Theoretical paper: proposes new theoretical frameworks, mathematical proofs, or algorithmic analysis, focusing on theoretical derivation rather than experimental validation
4. **unknown** - Other or unable to determine type

Please directly output one of the following types: survey, experimental, theoretical, unknown
"""

METHODOLOGY_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in explaining experimental methods in simple, easy-to-understand language. Please carefully read the following paper content and answer: **How did they do it? What is the experimental method?**

Paper content:
{content}

Requirements:
1. Explain experimental design and analysis methods in very simple, conversational language
2. Explain which datasets, evaluation metrics, and comparison methods were used
3. Explain key parameters and conditions of experimental settings
4. Summarize in 1-3 paragraphs, don't be too long
5. If content information is insufficient, state so honestly

Please output the analysis results directly, do not output any other content.
"""

RELATED_WORK_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in explaining related research in simple, easy-to-understand language. Please carefully read the following paper content and answer: **What is the relationship between this research and existing research? What are the related works?**

Paper content:
{content}

Requirements:
1. Use very simple, conversational language to explain the position of this research in the academic context
2. Mention several important related works or methods
3. Explain the shortcomings or limitations of these related works
4. Explain how this research improves or goes beyond these works
5. Summarize in 2-3 paragraphs, don't be too long
6. If content information is insufficient, state so honestly

Please output the analysis results directly, do not output any other content.
"""

LIMITATIONS_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in identifying research limitations. Please carefully read the following paper content and answer: **What are the shortcomings of this research? What are the limitations?**

Paper content:
{content}

Requirements:
1. Use very simple, conversational language to explain possible limitations of the research
2. Point out shortcomings in the method, experiments, or conclusions
3. Mention limitations or future work directions discussed by the authors themselves
4. Summarize in 1-2 paragraphs, keep it concise
5. If content information is insufficient, state so honestly

Please output the analysis results directly, do not output any other content.
"""

REPORT_GENERATION_PROMPT_EN = """You are an assistant who specializes in writing concise, clear reports. Based on the following analysis of a paper, generate a Markdown-formatted easy-to-understand report.

Paper title: {title}
Source: {source}
Paper type: {paper_type}

Background analysis:
{background}

Innovation analysis:
{innovation}

Results analysis:
{results}

{methodology_section}

{related_work_section}

{limitations_section}

Requirements:
1. Use Markdown format
2. Differentiated length requirements:
   - **Background & Motivation**: Keep concise, 100-200 words
   - **Innovation & Core Theory**: Expand in detail, 400-800 words, this is the core of the report
   - **Results**: Keep concise, 100-200 words
   - **Other sections**: Adjust length based on actual content
3. Language should be very easy to understand, avoid academic expressions
4. Use appropriate formatting (bold, lists, subheadings, etc.) to enhance readability
5. The innovation section can use subheadings or lists to organize content
6. Dynamically adjust report structure based on paper type and analysis results:
   - Experimental papers include "Methodology" section
   - Survey papers include "Related Work" section
   - Theoretical papers include "Limitations" section
7. Report structure as follows:

# Paper Analysis Report

## Original Information
- Source: [source]
- Title: [title]
- Type: [type]

## I. Background & Motivation
[Concisely explain research background and motivation]

## II. Innovation & Core Theory
[Expand in detail, can include multiple subsections]

## III. Results
[Concisely summarize main findings]

{additional_sections}

Please output the complete Markdown report directly, do not output any other content.
"""

# Language-specific prompt templates
PROMPTS_ZH = {
    "background": BACKGROUND_ANALYSIS_PROMPT_ZH,
    "innovation": INNOVATION_ANALYSIS_PROMPT_ZH,
    "results": RESULTS_ANALYSIS_PROMPT_ZH,
    "paper_type": PAPER_TYPE_DETECTION_PROMPT_ZH,
    "methodology": METHODOLOGY_ANALYSIS_PROMPT_ZH,
    "related_work": RELATED_WORK_ANALYSIS_PROMPT_ZH,
    "limitations": LIMITATIONS_ANALYSIS_PROMPT_ZH,
    "report": REPORT_GENERATION_PROMPT_ZH,
}

PROMPTS_EN = {
    "background": BACKGROUND_ANALYSIS_PROMPT_EN,
    "innovation": INNOVATION_ANALYSIS_PROMPT_EN,
    "results": RESULTS_ANALYSIS_PROMPT_EN,
    "paper_type": PAPER_TYPE_DETECTION_PROMPT_EN,
    "methodology": METHODOLOGY_ANALYSIS_PROMPT_EN,
    "related_work": RELATED_WORK_ANALYSIS_PROMPT_EN,
    "limitations": LIMITATIONS_ANALYSIS_PROMPT_EN,
    "report": REPORT_GENERATION_PROMPT_EN,
}

# Detail level modifiers for prompts
DETAIL_MODIFIERS = {
    "brief": {
        "background": "Keep it very brief - just 2-3 sentences maximum.",
        "innovation": "Summarize in 2-3 short paragraphs only.",
        "results": "One paragraph maximum.",
    },
    "standard": {
        "background": "1-3 paragraphs.",
        "innovation": "Expand in detail, 400-800 words.",
        "results": "1-3 paragraphs.",
    },
    "detailed": {
        "background": "Provide comprehensive background information in 3-5 paragraphs.",
        "innovation": "Provide extensive detail with multiple subsections, 800-1500 words.",
        "results": "Provide detailed results analysis in 3-5 paragraphs.",
    },
}

# Phase 4: New Extraction Prompts

CITATION_ANALYSIS_PROMPT_ZH = """你是一个擅长分析论文引用的助手。请仔细阅读下面的论文内容，然后分析论文的引用情况。

论文内容：
{content}

要求：
1. 统计引用的文献数量
2. 分类引用类型（基础文献、近期研究、竞争方法等）
3. 列出重要的基础文献
4. 列出重要的近期相关工作
5. 说明引用分布情况

请直接输出分析结果，不要输出任何其他内容。
"""

CITATION_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in analyzing paper citations. Please carefully read the following paper content and analyze the citation situation.

Paper content:
{content}

Requirements:
1. Count the number of cited literature
2. Classify citation types (foundational literature, recent research, competing methods, etc.)
3. List important foundational literature
4. List important recent related work
5. Explain the citation distribution

Please output the analysis results directly, do not output any other content.
"""

FIGURE_ANALYSIS_PROMPT_ZH = """你是一个擅长分析论文图表的助手。请仔细阅读下面的论文内容，然后分析论文中的图表情况。

论文内容：
{content}

要求：
1. 统计图表数量（图和表分别统计）
2. 分类图表类型（趋势图、结构图、数据表等）
3. 列出主要图表及其说明
4. 分析图表在论文中的作用

请直接输出分析结果，不要输出任何其他内容。
"""

FIGURE_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in analyzing paper figures and tables. Please carefully read the following paper content and analyze the figures and tables in the paper.

Paper content:
{content}

Requirements:
1. Count the number of figures and tables (separately)
2. Classify figure types (trend charts, structure diagrams, data tables, etc.)
3. List main figures and their descriptions
4. Analyze the role of figures in the paper

Please output the analysis results directly, do not output any other content.
"""

CODE_ANALYSIS_PROMPT_ZH = """你是一个擅长分析论文代码和算法的助手。请仔细阅读下面的论文内容，然后分析论文中的代码和算法情况。

论文内容：
{content}

要求：
1. 统计算法数量
2. 统计代码片段数量
3. 列出主要算法及其名称
4. 列出关键代码片段

请直接输出分析结果，不要输出任何其他内容。
"""

CODE_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in analyzing code and algorithms in papers. Please carefully read the following paper content and analyze the code and algorithm situation in the paper.

Paper content:
{content}

Requirements:
1. Count the number of algorithms
2. Count the number of code snippets
3. List main algorithms and their names
4. List key code snippets

Please output the analysis results directly, do not output any other content.
"""

REPRODUCIBILITY_ASSESSMENT_PROMPT_ZH = """你是一个擅长评估论文可复现性的助手。请仔细阅读下面的论文内容，然后评估论文的可复现性。

论文内容：
{content}

要求：
1. 检查代码是否可用或公开
2. 检查数据集是否可用或公开
3. 检查实验环境是否详细说明
4. 检查评估指标是否充分
5. 给出可复现性评分（0-100）
6. 提供改进建议

请直接输出分析结果，不要输出任何其他内容。
"""

REPRODUCIBILITY_ASSESSMENT_PROMPT_EN = """You are an assistant who specializes in assessing paper reproducibility. Please carefully read the following paper content and assess the reproducibility of the paper.

Paper content:
{content}

Requirements:
1. Check if code is available or public
2. Check if datasets are available or public
3. Check if experimental environment is detailed
4. Check if evaluation metrics are sufficient
5. Provide reproducibility score (0-100)
6. Provide suggestions for improvement

Please output the analysis results directly, do not output any other content.
"""

COMPARISON_PROMPT_ZH = """你是一个擅长对比多篇论文的助手。请仔细阅读以下几篇论文的内容，然后进行对比分析。

{paper_descriptions}

对比要求：
1. 用简单易懂的语言进行对比
2. 突出每篇论文的独特之处
3. 指出相似之处和差异
4. 给出客观的评价
5. 用列表和分段组织内容，便于阅读

请直接输出对比分析结果，不要输出任何其他内容。
"""

COMPARISON_PROMPT_EN = """You are an assistant who specializes in comparing multiple papers. Please carefully read the content of the following papers and conduct a comparative analysis.

{paper_descriptions}

Comparison requirements:
1. Use simple, easy-to-understand language for comparison
2. Highlight the unique aspects of each paper
3. Point out similarities and differences
4. Provide objective evaluation
5. Organize content with lists and paragraphs for easy reading

Please output the comparative analysis results directly, do not output any other content.
"""

# Phase 5: Adaptive Analysis Prompts

ANALYSIS_PLANNING_PROMPT_ZH = """你是一个论文分析规划专家。请根据以下论文信息，制定分析计划。

论文标题：{title}
论文类型：{paper_type}
内容摘要：{content_preview}
章节信息：{chapters_info}

请分析并输出：
1. 该论文需要分析哪些维度（从以下选择）：
   - background（背景）
   - innovation（创新）
   - results（结果）
   - methodology（方法）
   - related_work（相关工作）
   - limitations（局限性）
   - citations（引用分析）
   - figures（图表分析）
   - code（代码提取）
   - reproducibility（可复现性评估）

2. 各维度的优先级顺序

3. 选择理由（为什么这些维度重要）

4. 需要特别注意的点

5. 建议的详细程度（brief/standard/detailed）

请以 JSON 格式输出，格式如下：
{{
    "dimensions": ["background", "innovation", "results", ...],
    "priority": ["innovation", "background", "results"],
    "reason": "这是一篇实验论文，核心创新在...",
    "notes": ["注意验证实验设计", "重点关注结果对比"],
    "suggested_detail_level": "standard"
}}
"""

ANALYSIS_PLANNING_PROMPT_EN = """You are a paper analysis planning expert. Please create an analysis plan based on the following paper information.

Paper Title: {title}
Paper Type: {paper_type}
Content Summary: {content_preview}
Chapter Information: {chapters_info}

Please analyze and output:
1. Which dimensions need to be analyzed (choose from the following):
   - background (Background)
   - innovation (Innovation)
   - results (Results)
   - methodology (Methodology)
   - related_work (Related Work)
   - limitations (Limitations)
   - citations (Citation Analysis)
   - figures (Figure Analysis)
   - code (Code Extraction)
   - reproducibility (Reproducibility Assessment)

2. Priority order of each dimension

3. Selection reason (why these dimensions are important)

4. Points that need special attention

5. Suggested detail level (brief/standard/detailed)

Please output in JSON format as follows:
{{
    "dimensions": ["background", "innovation", "results", ...],
    "priority": ["innovation", "background", "results"],
    "reason": "This is an experimental paper, the core innovation is in...",
    "notes": ["Pay attention to experimental design", "Focus on result comparison"],
    "suggested_detail_level": "standard"
}}
"""

QUALITY_ASSESSMENT_PROMPT_ZH = """你是一个内容质量评估专家。请评估以下分析结果的质量。

分析维度：{dimension}
分析内容：{content}

请评估：
1. 内容完整性（0-1分）：是否覆盖了该维度应该包含的关键内容
2. 深度（0-1分）：分析深度是否足够，是否触及核心问题
3. 清晰度（0-1分）：语言表达是否清晰易懂
4. 准确性（0-1分）：基于原文内容是否准确

5. 具体问题（如有）
6. 是否需要重新分析
7. 改进建议

请以 JSON 格式输出：
{{
    "completeness": 0.8,
    "depth": 0.7,
    "clarity": 0.9,
    "accuracy": 0.85,
    "overall_score": 0.81,
    "issues": ["缺少具体数据", "部分概念未解释"],
    "needs_refinement": true,
    "suggestion": "需要补充实验数据的具体数值"
}}

如果 overall_score >= 0.75，将 needs_refinement 设为 false。
"""

QUALITY_ASSESSMENT_PROMPT_EN = """You are a content quality assessment expert. Please evaluate the quality of the following analysis result.

Analysis Dimension: {dimension}
Analysis Content: {content}

Please evaluate:
1. Completeness (0-1 score): Does it cover the key content that this dimension should include
2. Depth (0-1 score): Is the analysis depth sufficient, does it touch on core issues
3. Clarity (0-1 score): Is the language expression clear and easy to understand
4. Accuracy (0-1 score): Is it accurate based on the original content

5. Specific issues (if any)
6. Whether re-analysis is needed
7. Improvement suggestions

Please output in JSON format:
{{
    "completeness": 0.8,
    "depth": 0.7,
    "clarity": 0.9,
    "accuracy": 0.85,
    "overall_score": 0.81,
    "issues": ["Missing specific data", "Some concepts not explained"],
    "needs_refinement": true,
    "suggestion": "Need to supplement specific numerical values of experimental data"
}}

If overall_score >= 0.75, set needs_refinement to false.
"""

# Update PROMPTS dictionaries
PROMPTS_ZH.update({
    "citations": CITATION_ANALYSIS_PROMPT_ZH,
    "figures": FIGURE_ANALYSIS_PROMPT_ZH,
    "code": CODE_ANALYSIS_PROMPT_ZH,
    "reproducibility": REPRODUCIBILITY_ASSESSMENT_PROMPT_ZH,
    "comparison": COMPARISON_PROMPT_ZH,
    "analysis_planning": ANALYSIS_PLANNING_PROMPT_ZH,
    "quality_assessment": QUALITY_ASSESSMENT_PROMPT_ZH,
})

PROMPTS_EN.update({
    "citations": CITATION_ANALYSIS_PROMPT_EN,
    "figures": FIGURE_ANALYSIS_PROMPT_EN,
    "code": CODE_ANALYSIS_PROMPT_EN,
    "reproducibility": REPRODUCIBILITY_ASSESSMENT_PROMPT_EN,
    "comparison": COMPARISON_PROMPT_EN,
    "analysis_planning": ANALYSIS_PLANNING_PROMPT_EN,
    "quality_assessment": QUALITY_ASSESSMENT_PROMPT_EN,
})

# New getter functions for extraction prompts
def get_citations_prompt(content: str, language: str = "zh") -> str:
    """Get the citations analysis prompt with content filled in."""
    prompt = get_prompt_template("citations", language)
    return prompt.format(content=content)


def get_figures_prompt(content: str, language: str = "zh") -> str:
    """Get the figures analysis prompt with content filled in."""
    prompt = get_prompt_template("figures", language)
    return prompt.format(content=content)


def get_code_prompt(content: str, language: str = "zh") -> str:
    """Get the code analysis prompt with content filled in."""
    prompt = get_prompt_template("code", language)
    return prompt.format(content=content)


def get_reproducibility_prompt(content: str, language: str = "zh") -> str:
    """Get the reproducibility assessment prompt with content filled in."""
    prompt = get_prompt_template("reproducibility", language)
    return prompt.format(content=content)


def get_comparison_prompt(paper_descriptions: str, language: str = "zh") -> str:
    """Get the comparison prompt with paper descriptions filled in."""
    prompt = get_prompt_template("comparison", language)
    return prompt.format(paper_descriptions=paper_descriptions)


def get_analysis_planning_prompt(
    title: str,
    paper_type: str,
    content_preview: str,
    chapters_info: str = "",
    language: str = "zh"
) -> str:
    """Get the analysis planning prompt with content filled in."""
    prompt = get_prompt_template("analysis_planning", language)
    return prompt.format(
        title=title or "未知" if language == "zh" else "Unknown",
        paper_type=paper_type or "unknown",
        content_preview=content_preview,
        chapters_info=chapters_info
    )


def get_quality_assessment_prompt(
    dimension: str,
    content: str,
    language: str = "zh"
) -> str:
    """Get the quality assessment prompt with content filled in."""
    prompt = get_prompt_template("quality_assessment", language)
    return prompt.format(
        dimension=dimension,
        content=content
    )


# Legacy prompts for backward compatibility
BACKGROUND_ANALYSIS_PROMPT = BACKGROUND_ANALYSIS_PROMPT_ZH
INNOVATION_ANALYSIS_PROMPT = INNOVATION_ANALYSIS_PROMPT_ZH
RESULTS_ANALYSIS_PROMPT = RESULTS_ANALYSIS_PROMPT_ZH
PAPER_TYPE_DETECTION_PROMPT = PAPER_TYPE_DETECTION_PROMPT_ZH
METHODOLOGY_ANALYSIS_PROMPT = METHODOLOGY_ANALYSIS_PROMPT_ZH
RELATED_WORK_ANALYSIS_PROMPT = RELATED_WORK_ANALYSIS_PROMPT_ZH
LIMITATIONS_ANALYSIS_PROMPT = LIMITATIONS_ANALYSIS_PROMPT_ZH
REPORT_GENERATION_PROMPT = REPORT_GENERATION_PROMPT_ZH
CITATION_ANALYSIS_PROMPT = CITATION_ANALYSIS_PROMPT_ZH
FIGURE_ANALYSIS_PROMPT = FIGURE_ANALYSIS_PROMPT_ZH
CODE_ANALYSIS_PROMPT = CODE_ANALYSIS_PROMPT_ZH
REPRODUCIBILITY_ASSESSMENT_PROMPT = REPRODUCIBILITY_ASSESSMENT_PROMPT_ZH
COMPARISON_PROMPT = COMPARISON_PROMPT_ZH

def get_prompt_template(prompt_name: str, language: str = "zh") -> str:
    """
    Get a prompt template for a specific name and language.

    Args:
        prompt_name: Name of the prompt (background, innovation, results, etc.)
        language: Language code (zh, en)

    Returns:
        The prompt template string
    """
    prompts_dict = PROMPTS_ZH if language == "zh" else PROMPTS_EN
    return prompts_dict.get(prompt_name, PROMPTS_ZH.get(prompt_name, ""))


def apply_detail_level(prompt: str, detail_level: str) -> str:
    """
    Apply detail level modifiers to a prompt.

    Args:
        prompt: Original prompt template
        detail_level: Detail level (brief, standard, detailed)

    Returns:
        Modified prompt with detail level specifications
    """
    # For now, return the prompt as-is
    # In a full implementation, this would modify the prompt based on detail level
    return prompt


def get_background_prompt(content: str, language: str = "zh", detail_level: str = "standard", figures_context: str = "") -> str:
    """Get the background analysis prompt with content filled in."""
    prompt = get_prompt_template("background", language)
    prompt = apply_detail_level(prompt, detail_level)
    return prompt.format(content=content, figures_context=figures_context)


def get_innovation_prompt(content: str, language: str = "zh", detail_level: str = "standard", figures_context: str = "") -> str:
    """Get the innovation analysis prompt with content filled in."""
    prompt = get_prompt_template("innovation", language)
    prompt = apply_detail_level(prompt, detail_level)
    return prompt.format(content=content, figures_context=figures_context)


def get_results_prompt(content: str, language: str = "zh", detail_level: str = "standard", figures_context: str = "") -> str:
    """Get the results analysis prompt with content filled in."""
    prompt = get_prompt_template("results", language)
    prompt = apply_detail_level(prompt, detail_level)
    return prompt.format(content=content, figures_context=figures_context)


def get_paper_type_detection_prompt(title: str, content: str, language: str = "zh") -> str:
    """Get the paper type detection prompt with content filled in."""
    prompt = get_prompt_template("paper_type", language)
    # Slice content to first 2000 chars before formatting
    content_preview = content[:2000] if len(content) > 2000 else content
    return prompt.format(title=title or "未知" if language == "zh" else "Unknown", content=content_preview)


def get_methodology_prompt(content: str, language: str = "zh", detail_level: str = "standard") -> str:
    """Get the methodology analysis prompt with content filled in."""
    prompt = get_prompt_template("methodology", language)
    prompt = apply_detail_level(prompt, detail_level)
    return prompt.format(content=content)


def get_related_work_prompt(content: str, language: str = "zh", detail_level: str = "standard") -> str:
    """Get the related work analysis prompt with content filled in."""
    prompt = get_prompt_template("related_work", language)
    prompt = apply_detail_level(prompt, detail_level)
    return prompt.format(content=content)


def get_limitations_prompt(content: str, language: str = "zh", detail_level: str = "standard") -> str:
    """Get the limitations analysis prompt with content filled in."""
    prompt = get_prompt_template("limitations", language)
    prompt = apply_detail_level(prompt, detail_level)
    return prompt.format(content=content)


def get_report_prompt(
    title: str,
    source: str,
    background: str,
    innovation: str,
    results: str,
    paper_type: str = "unknown",
    methodology: str = "",
    related_work: str = "",
    limitations: str = "",
    language: str = "zh"
) -> str:
    """Get the report generation prompt with all information filled in."""
    prompt = get_prompt_template("report", language)

    # Build additional sections dynamically
    additional_sections = []

    if methodology:
        section_title = "## 四、实验方法" if language == "zh" else "## IV. Methodology"
        additional_sections.append(f"\n{section_title}\n" + methodology)

    if related_work:
        section_title = "## 四、相关工作" if language == "zh" else "## IV. Related Work"
        additional_sections.append(f"\n{section_title}\n" + related_work)

    if limitations:
        section_title = "## 四、局限性" if language == "zh" else "## IV. Limitations"
        additional_sections.append(f"\n{section_title}\n" + limitations)

    additional_sections_text = "".join(additional_sections)

    # Build section content
    methodology_section = methodology if methodology else ""
    related_work_section = related_work if related_work else ""
    limitations_section = limitations if limitations else ""

    return prompt.format(
        title=title or ("未知" if language == "zh" else "Unknown"),
        source=source,
        paper_type=paper_type,
        background=background,
        innovation=innovation,
        results=results,
        methodology_section=methodology_section,
        related_work_section=related_work_section,
        limitations_section=limitations_section,
        additional_sections=additional_sections_text
    )