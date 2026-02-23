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
请按照以下四个层次逐步深入地进行分析：

**第一层：通俗理解（面向非专业人士）**
- 用简单的生活比喻或类比来解释核心问题（1-2段）
- 即使是高中生也能听懂
- 例如："就像我们在日常生活中遇到X问题..."

**第二层：关键问题（研究动机）**
- 说明这个研究要解决的具体问题是什么
- 为什么这个问题很重要
- 有什么实际需求或应用场景

**第三层：现有不足（研究缺口）**
- 说明现有方法或技术存在的局限性
- 这些不足带来了什么具体问题
- 用具体的数据或实例说明（如果论文中有）

**第四层：深层洞察（研究意义）**
- 这个研究在整个领域中的位置和重要性
- **举1-2个论文之外的现实世界例子**来说明这个问题的重要性
- 讨论解决这个问题可能带来的长远影响

**特别要求：**
- 引用论文中提到的具体问题陈述、数据或统计信息
- 如果论文中没有具体数据，请**自行构造现实世界的具体例子**来帮助理解
- 用列表和分段组织内容，便于阅读

请直接输出分析结果，不要输出任何其他内容。
"""

INNOVATION_ANALYSIS_PROMPT_ZH = """你是一个擅长用简单易懂的语言解释学术创新的助手。请仔细阅读下面的论文内容，然后回答：**有什么新的贡献或创新点？核心理论是什么？**

论文内容：
{content}
{figures_context}

要求：
请按照以下四个层次逐步深入地进行分析：

**第一层：通俗理解（面向非专业人士）**
- 用简单的生活比喻或类比来解释核心思想（1-2段）
- 即使是高中生也能听懂
- 例如："想象这个方法就像..."

**第二层：关键机制（技术概述）**
- 说明这个方法的核心机制是什么
- 用图表或公式解释基本原理
- 举例说明它是如何解决核心问题的

**第三层：具体实现（技术细节）**
- 详细说明算法步骤或架构组件
- 解释关键参数、设计选择的原因
- 如果有公式，用自然语言解释每个部分
- 引用论文中的具体技术细节（模型名称、层结构、损失函数等）

**第四层：深层洞察（研究意义）**
- 这个方法与已有方法的关键区别是什么
- 为什么要这样设计，有什么权衡
- **举1-2个论文之外的现实世界例子**来说明这个方法的应用或意义
- 讨论这个创新对整个领域的影响

**特别要求：**
- 引用具体的图表、公式、数据（如表1显示X，图2说明Y）
- 如果论文中没有举例，请**自行构造具体的现实世界例子**来帮助理解
- 用列表和分段组织内容，便于阅读

请直接输出分析结果，不要输出任何其他内容。
"""

RESULTS_ANALYSIS_PROMPT_ZH = """你是一个擅长用简单易懂的语言总结研究结果的助手。请仔细阅读下面的论文内容，然后回答：**结论是什么？得到了什么结果？**

论文内容：
{content}
{figures_context}

要求：
请按照以下四个层次逐步深入地进行分析：

**第一层：通俗理解（面向非专业人士）**
- 用简单的话总结主要结论（1-2段）
- 哪怕是非专业人士也能理解这个研究证明了什么
- 例如："简单来说，这个方法做到了X，比之前的方法好Y%"

**第二层：关键发现（核心结果）**
- 说明最重要的几个发现是什么
- 哪些指标得到了改善
- 用对比的方式说明（与基线方法相比）

**第三层：具体数据（详细结果）**
- 包含具体的定量数据：
  - 关键性能指标（准确率、F1分数、召回率等）
  - 对比数据（比基线方法提升X%）
  - 具体数字（例如："在X数据集上达到Y%的准确率"）
- 引用具体的表或图中的数据
- 说明实验条件的细节

**第四层：深层洞察（结果意义）**
- 这些结果有什么实际意义或价值
- **举1-2个论文之外的现实世界例子**说明这些结果的应用价值
- 讨论结果对领域发展的意义
- 分析结果是否验证了研究假设

**特别要求：**
- 引用具体的图表、数据（如表1显示X，图2展示Y的趋势）
- 如果论文中没有应用例子，请**自行构造现实世界的应用场景**来说明结果的价值
- 用列表和分段组织内容，便于阅读

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
请按照以下四个层次逐步深入地进行分析：

**第一层：通俗理解（面向非专业人士）**
- 用简单的话概括实验方法（1-2段）
- 用生活化的比喻说明实验的基本思路
- 例如："他们就像在做一个对比测试，比较X和Y..."

**第二层：关键组件（方法概述）**
- 说明实验设计的主要组成部分
- 介绍使用的数据集、评价指标
- 说明对比的主要方法

**第三层：具体设置（技术细节）**
- 详细说明实验设置的关键参数和条件
- 解释实验流程的步骤
- 说明实验环境的配置（硬件、软件等）
- 引用论文中的具体参数值

**第四层：深层洞察（方法评价）**
- 这个实验设计的优点是什么
- **举1-2个论文之外的现实世界例子**来说明这种实验方法的应用
- 讨论实验方法的局限性和可能改进方向

**特别要求：**
- 引用论文中的具体数据集名称、参数值、实验设置
- 如果论文中缺少某些细节，请根据已有信息合理推断
- 用列表和分段组织内容，便于阅读

请直接输出分析结果，不要输出任何其他内容。
"""

RELATED_WORK_ANALYSIS_PROMPT_ZH = """你是一个擅长用简单易懂的语言解释相关研究的助手。请仔细阅读下面的论文内容，然后回答：**这个研究与已有研究有什么关系？相关工作有哪些？**

论文内容：
{content}

要求：
请按照以下四个层次逐步深入地进行分析：

**第一层：通俗理解（面向非专业人士）**
- 用简单的话说明这个研究在学术领域的位置（1-2段）
- 就像在介绍一个家族族谱一样说明研究脉络
- 例如："这个领域的研究就像一棵大树，本研究属于其中的一根树枝..."

**第二层：核心脉络（研究概览）**
- 说明该研究领域的发展脉络和趋势
- 介绍几个重要的代表性工作或里程碑
- 说明这些工作之间的演进关系

**第三层：具体工作（详细分析）**
- 列出论文中提及的几个重要的相关工作或方法
- 说明这些相关工作的主要贡献和特点
- 指出这些工作的不足或局限性
- 说明当前研究如何改进或超越这些工作

**第四层：深层洞察（领域洞察）**
- **举1-2个论文之外的现实世界例子**来说明这个研究领域的应用和重要性
- 讨论整个研究领域的未来发展方向
- 分析当前研究的创新在整个领域中的意义

**特别要求：**
- 引用论文中提到的具体工作名称、作者、发表信息
- 用列表和分段组织内容，便于阅读

请直接输出分析结果，不要输出任何其他内容。
"""

LIMITATIONS_ANALYSIS_PROMPT_ZH = """你是一个擅长识别研究局限性的助手。请仔细阅读下面的论文内容，然后回答：**这个研究有什么不足？有什么限制？**

论文内容：
{content}

要求：
请按照以下四个层次逐步深入地进行分析：

**第一层：通俗理解（面向非专业人士）**
- 用简单的话概括这个研究的主要限制（1-2段）
- 用生活中的例子类比说明
- 例如："就像这个方法只能在特定条件下工作，就像..."

**第二层：关键限制（主要局限）**
- 列出方法、实验或结论的主要不足之处
- 说明这些限制对结果的影响

**第三层：具体分析（深入剖析）**
- 详细分析每个局限性的原因
- 说明这些局限性可能在什么情况下出现问题
- 引用论文中作者自己讨论的局限性

**第四层：深层洞察（未来方向）**
- 讨论作者提出的未来工作方向
- **举1-2个论文之外的现实世界例子**说明这些局限性在实际应用中的影响
- 提出可能的改进方向或解决思路

**特别要求：**
- 引用论文中作者自己讨论的局限性或未来工作
- 如果论文中没有充分讨论，请基于你的分析提出合理的局限性
- 用列表和分段组织内容，便于阅读

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
Please analyze in the following four progressive tiers:

**Tier 1: Layman Understanding (for non-experts)**
- Use simple metaphors or analogies from everyday life to explain the core problem (1-2 paragraphs)
- Make it understandable even to a high school student
- Example: "It's like when we encounter problem X in everyday life..."

**Tier 2: Key Issues (Research Motivation)**
- Explain what specific problem this research aims to solve
- Why is this problem important
- What practical needs or application scenarios exist

**Tier 3: Existing Gaps (Research Gap)**
- Explain the limitations of existing methods or technologies
- What specific problems do these limitations create
- Use specific data or examples if present in the paper

**Tier 4: Deep Insights (Research Significance)**
- The position and importance of this research in the entire field
- **Provide 1-2 real-world examples outside the paper** to illustrate the importance of this problem
- Discuss the long-term impact of solving this problem

**Special Requirements:**
- Reference specific problem statements, data, or statistics mentioned in the paper
- If the paper lacks specific data, **construct your own real-world examples** to help with understanding
- Organize content with lists and paragraphs for easy reading

Please output the analysis results directly, do not output any other content.
"""

INNOVATION_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in explaining academic innovations in simple, easy-to-understand language. Please carefully read the following paper content and answer: **What are the new contributions or innovations? What is the core theory?**

Paper content:
{content}
{figures_context}

Requirements:
Please analyze in the following four progressive tiers:

**Tier 1: Layman Understanding (for non-experts)**
- Use simple metaphors or analogies from everyday life to explain the core idea (1-2 paragraphs)
- Make it understandable even to a high school student
- Example: "Imagine this method is like..."

**Tier 2: Key Mechanisms (Technical Overview)**
- Explain what the core mechanism of this method is
- Use diagrams or formulas to explain basic principles
- Give examples of how it solves the core problem

**Tier 3: Specific Implementation (Technical Details)**
- Detail the algorithm steps or architecture components
- Explain key parameters and reasons for design choices
- If formulas exist, explain each part in natural language
- Reference specific technical details from the paper (model names, layer structures, loss functions, etc.)

**Tier 4: Deep Insights (Research Significance)**
- What are the key differences between this method and existing methods
- Why was it designed this way, what trade-offs were made
- **Provide 1-2 real-world examples outside the paper** to illustrate the application or significance of this method
- Discuss the impact of this innovation on the entire field

**Special Requirements:**
- Reference specific figures, formulas, and data (e.g., "Table 1 shows X", "Figure 2 demonstrates Y")
- If the paper lacks examples, **construct your own real-world examples** to help with understanding
- Organize content with lists and paragraphs for easy reading

Please output the analysis results directly, do not output any other content.
"""

RESULTS_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in summarizing research results in simple, easy-to-understand language. Please carefully read the following paper content and answer: **What is the conclusion? What were the results?**

Paper content:
{content}
{figures_context}

Requirements:
Please analyze in the following four progressive tiers:

**Tier 1: Layman Understanding (for non-experts)**
- Summarize the main conclusion in simple terms (1-2 paragraphs)
- Make it understandable what this research proved, even to non-experts
- Example: "Simply put, this method achieved X, which is Y% better than previous methods"

**Tier 2: Key Findings (Core Results)**
- Explain what the most important findings are
- Which metrics were improved
- Use comparisons (compared to baseline methods)

**Tier 3: Specific Data (Detailed Results)**
- Include specific quantitative data:
  - Key performance metrics (accuracy, F1 score, recall, etc.)
  - Comparison data (X% improvement over baseline)
  - Specific numbers (e.g., "achieved Y% accuracy on X dataset")
- Reference specific data from tables or figures
- Explain details of experimental conditions

**Tier 4: Deep Insights (Significance of Results)**
- What is the practical significance or value of these results
- **Provide 1-2 real-world examples outside the paper** to illustrate the application value of these results
- Discuss the significance of the results for field development
- Analyze whether results validate the research hypothesis

**Special Requirements:**
- Reference specific figures and data (e.g., "Table 1 shows X", "Figure 2 displays the trend of Y")
- If the paper lacks application examples, **construct real-world application scenarios** to illustrate the value of results
- Organize content with lists and paragraphs for easy reading

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
Please analyze in the following four progressive tiers:

**Tier 1: Layman Understanding (for non-experts)**
- Summarize the experimental method in simple terms (1-2 paragraphs)
- Use everyday metaphors to explain the basic experimental approach
- Example: "They're like doing a comparative test, comparing X and Y..."

**Tier 2: Key Components (Method Overview)**
- Explain the main components of the experimental design
- Introduce the datasets used and evaluation metrics
- Explain the main comparison methods

**Tier 3: Specific Settings (Technical Details)**
- Detail the key parameters and conditions of experimental settings
- Explain the steps of the experimental procedure
- Describe the experimental environment configuration (hardware, software, etc.)
- Reference specific parameter values from the paper

**Tier 4: Deep Insights (Method Evaluation)**
- What are the advantages of this experimental design
- **Provide 1-2 real-world examples outside the paper** to illustrate applications of this experimental method
- Discuss limitations of the experimental method and possible improvements

**Special Requirements:**
- Reference specific dataset names, parameter values, and experimental settings from the paper
- If the paper lacks certain details, make reasonable inferences based on available information
- Organize content with lists and paragraphs for easy reading

Please output the analysis results directly, do not output any other content.
"""

RELATED_WORK_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in explaining related research in simple, easy-to-understand language. Please carefully read the following paper content and answer: **What is the relationship between this research and existing research? What are the related works?**

Paper content:
{content}

Requirements:
Please analyze in the following four progressive tiers:

**Tier 1: Layman Understanding (for non-experts)**
- Explain the position of this research in the academic field in simple terms (1-2 paragraphs)
- Like introducing a family tree, explain the research lineage
- Example: "Research in this field is like a large tree, and this study is one of its branches..."

**Tier 2: Core Lineage (Research Overview)**
- Explain the development lineage and trends of the research field
- Introduce several important representative works or milestones
- Explain the evolutionary relationships between these works

**Tier 3: Specific Works (Detailed Analysis)**
- List several important related works or methods mentioned in the paper
- Explain the main contributions and characteristics of these related works
- Point out the shortcomings or limitations of these works
- Explain how the current research improves or goes beyond these works

**Tier 4: Deep Insights (Field Insights)**
- **Provide 1-2 real-world examples outside the paper** to illustrate the application and importance of this research field
- Discuss future development directions of the entire research field
- Analyze the significance of the current research's innovation within the entire field

**Special Requirements:**
- Reference specific work names, authors, and publication information mentioned in the paper
- Organize content with lists and paragraphs for easy reading

Please output the comparative analysis results directly, do not output any other content.
"""

LIMITATIONS_ANALYSIS_PROMPT_EN = """You are an assistant who specializes in identifying research limitations. Please carefully read the following paper content and answer: **What are the shortcomings of this research? What are the limitations?**

Paper content:
{content}

Requirements:
Please analyze in the following four progressive tiers:

**Tier 1: Layman Understanding (for non-experts)**
- Summarize the main limitations of this research in simple terms (1-2 paragraphs)
- Use everyday examples to analogize the limitations
- Example: "Like this method only works under specific conditions, similar to..."

**Tier 2: Key Limitations (Main Constraints)**
- List the main shortcomings of the method, experiments, or conclusions
- Explain how these limitations affect the results

**Tier 3: Specific Analysis (Deep Dive)**
- Analyze the reasons for each limitation in detail
- Explain under what circumstances these limitations might cause problems
- Reference limitations discussed by the authors themselves in the paper

**Tier 4: Deep Insights (Future Directions)**
- Discuss future work directions proposed by the authors
- **Provide 1-2 real-world examples outside the paper** to illustrate the impact of these limitations in practical applications
- Propose possible improvement directions or solutions

**Special Requirements:**
- Reference limitations or future work directions discussed by the authors in the paper
- If the paper lacks sufficient discussion, propose reasonable limitations based on your analysis
- Organize content with lists and paragraphs for easy reading

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
# These modify the prompts based on the requested detail level
DETAIL_MODIFIERS = {
    "brief": {
        "background": "Keep it very brief - focus on Tier 1 (Layman Understanding) only, 1 paragraph maximum.",
        "innovation": "Focus on Tiers 1-2 (Layman Understanding + Key Mechanisms), keep it concise, 2-3 paragraphs total.",
        "results": "Focus on Tier 1 (Layman Understanding) only, 1 paragraph maximum.",
        "methodology": "Focus on Tier 1 (Layman Understanding) only, 1 paragraph maximum.",
        "related_work": "Focus on Tier 1 (Layman Understanding) only, 1 paragraph maximum.",
        "limitations": "Focus on Tier 1 (Layman Understanding) only, 1 paragraph maximum.",
    },
    "standard": {
        "background": "Include Tiers 1-3 (Layman Understanding + Key Issues + Existing Gaps), 3-4 paragraphs total.",
        "innovation": "Include all four tiers with balanced depth, 5-7 paragraphs total. This is the core of the report.",
        "results": "Include Tiers 1-3 (Layman Understanding + Key Findings + Specific Data), 3-4 paragraphs total.",
        "methodology": "Include Tiers 1-3 (Layman Understanding + Key Components + Specific Settings), 2-3 paragraphs total.",
        "related_work": "Include Tiers 1-3 (Layman Understanding + Core Lineage + Specific Works), 2-3 paragraphs total.",
        "limitations": "Include Tiers 1-3 (Layman Understanding + Key Limitations + Specific Analysis), 2-3 paragraphs total.",
    },
    "detailed": {
        "background": "Include all four tiers with comprehensive detail, 4-6 paragraphs total.",
        "innovation": "Provide extensive detail across all four tiers, 8-12 paragraphs total. Emphasize Tier 3 (Technical Details) and Tier 4 (Deep Insights).",
        "results": "Include all four tiers with comprehensive detail, 5-7 paragraphs total. Emphasize Tier 3 (Specific Data) with detailed quantitative analysis.",
        "methodology": "Include all four tiers with comprehensive detail, 4-5 paragraphs total. Emphasize Tier 3 (Specific Settings).",
        "related_work": "Include all four tiers with comprehensive detail, 4-5 paragraphs total. Emphasize Tier 4 (Field Insights).",
        "limitations": "Include all four tiers with comprehensive detail, 3-4 paragraphs total. Emphasize Tier 4 (Future Directions).",
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