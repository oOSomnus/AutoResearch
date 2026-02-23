# AutoResearch

> 基于 LangGraph 的智能论文阅读 Agent，自动分析学术论文并生成易懂报告

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-green)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 简介

AutoResearch 是一个功能强大的智能论文阅读助手，能够自动分析学术论文并生成易于理解的报告。它支持多种输出格式、双语分析、可恢复工作流和高级内容提取。

### 核心特性

**基础分析维度**：
- **背景与动机** - 为什么要做这个研究？
- **创新与核心理论** - 有什么新的贡献和方法？
- **结果与结论** - 得到了什么结果？

**扩展分析维度**（根据论文类型动态选择）：
- **实验方法** - 实验类论文：实验设计和分析方法
- **相关工作** - 综述类论文：领域研究脉络和趋势
- **局限性** - 理论类论文：方法限制和未来方向

**高级功能**：
- 多格式输出：Markdown、HTML、PDF、JSON
- 双语支持：中文/英文
- 详细程度控制：简洁/标准/详细
- 可恢复分析：检查点保存与恢复
- 批量处理：多论文批量分析
- 交互问答：基于 RAG 的论文问答
- 内容提取：引用分析、图表分析、代码提取、可复现性评估
- 缓存优化：结果缓存加速重复分析
- **智能自适应分析**：基于论文内容动态规划分析路径，自动质量评估与精炼
- **交互式对话模式**：支持与论文助手进行多轮对话问答

## 架构概览

### 工作流程图

**标准模式工作流**：

```mermaid
flowchart TD
    A[开始] --> B[fetch_pdf<br/>获取PDF]
    B --> C[extract_content<br/>提取内容和章节]
    C --> D[detect_paper_type<br/>检测论文类型]

    D --> E{论文类型?}

    E -->|survey| F[analyze_background<br/>背景分析]
    E -->|experimental| G[analyze_background<br/>背景分析]
    E -->|theoretical/unknown| H[analyze_background<br/>背景分析]

    F --> I[analyze_related_work<br/>相关工作]
    G --> J[analyze_innovation<br/>创新分析]
    H --> J

    I --> J
    J --> K{论文类型?}

    K -->|survey| L[analyze_results<br/>结果分析]
    K -->|experimental| M[analyze_methodology<br/>实验方法]
    K -->|theoretical/unknown| N[analyze_limitations<br/>局限性]

    M --> L
    N --> L

    L --> O[generate_report<br/>生成报告]
    O --> P[save_report<br/>保存报告]
    P --> Q[结束]

    style A fill:#667eea
    style B fill:#764ba2
    style C fill:#f093fb
    style D fill:#4facfe
    style E fill:#43e97b
    style P fill:#ff6b6b
    style Q fill:#667eea
```

**自适应模式工作流**：

```mermaid
flowchart TD
    A[开始] --> B[fetch_pdf<br/>获取PDF]
    B --> C[extract_content<br/>提取内容和章节]
    C --> D[detect_paper_type<br/>检测论文类型]
    D --> E[plan_analysis<br/>智能分析规划]

    E --> F{是否有待分析维度?}
    F -->|是| G[路由到下一维度]
    F -->|否| X[generate_report]

    G --> H[执行分析节点]
    H --> I[assess_quality<br/>质量评估]

    I --> J{质量是否达标?}
    J -->|否, 且未达最大迭代次数| K[返回精炼]
    J -->|是| F
    K --> H

    X --> Y[save_report]
    Y --> Z[结束]

    style A fill:#667eea
    style E fill:#ff6b6b
    style I fill:#feca57
    style K fill:#ff6b6b
    style Z fill:#667eea
```

**交互式对话模式工作流**：

```mermaid
flowchart TD
    A[开始] --> B[run_initial_analysis<br/>完成初始分析]
    B --> C[进入对话循环]
    C --> D[用户提问]
    D --> E[answer_question<br/>回答问题]
    E --> F{用户是否退出?}
    F -->|否| D
    F -->|是| G[结束]

    style A fill:#667eea
    style B fill:#4facfe
    style E fill:#43e97b
    style G fill:#ff6b6b
```

### 模块架构

```mermaid
graph TB
    subgraph CLI Layer[CLI Layer]
        A[main.py<br/>命令行入口]
    end

    subgraph Core Layer[Core Layer]
        B[graph.py<br/>LangGraph 工作流]
        C[nodes.py<br/>节点函数]
        D[prompts.py<br/>提示词模板]
    end

    subgraph Processing Layer[Processing Layer]
        E[pdf_reader.py<br/>PDF读取]
        F[chunking.py<br/>章节提取]
    end

    subgraph Output Layer[Output Layer]
        G[formatters/<br/>格式化器]
    end

    subgraph Enhancement Layer[Enhancement Layer]
        H[cache.py<br/>缓存管理]
        I[checkpoint.py<br/>检查点]
        J[progress.py<br/>进度追踪]
        K[history.py<br/>历史记录]
        L[batch.py<br/>批量处理]
        M[qa_mode.py<br/>问答模式]
        N[ui.py<br/>终端UI]
    end

    subgraph Analysis Layer[Analysis Layer]
        O[extractors/<br/>提取器]
        P[comparison.py<br/>论文对比]
    end

    subgraph Support Layer[Support Layer]
        Q[config.py<br/>配置管理]
        R[types.py<br/>数据类型]
        S[cache/<br/>缓存包]
        T[retry.py<br/>重试逻辑]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    D --> G

    B --> H
    B --> I
    B --> J
    B --> K
    B --> L
    A --> M
    A --> N

    B --> O
    A --> P

    B --> Q
    C --> R
    H --> S
    C --> T

    style A fill:#667eea
    style G fill:#764ba2
    style H fill:#f093fb
    style I fill:#4facfe
    style J fill:#43e97b
    style K fill:#ff6b6b
    style L fill:#feca57
    style M fill:#48dbfb
    style N fill:#1dd1a1
    style O fill:#5f27cd
    style P fill:#5f27cd
```

## 快速开始

### 环境要求

- Python 3.8+
- OpenAI 兼容的 API（如 OpenAI、Azure、Claude 等）

### 安装

```bash
# 克隆仓库
git clone https://github.com/oOSomnus/AutoResearch.git
cd AutoResearch

# 安装依赖
uv pip install -r requirements.txt
# 或者使用 pip
pip install -r requirements.txt
```

### 配置

复制环境变量模板并配置 API 信息：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 信息：

```env
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4
```

## 使用方法

### 交互式模式

运行程序后按提示输入 PDF 路径或 URL：

```bash
python main.py
```

### 直接模式

```bash
# 基础用法
python main.py ./paper.pdf
python main.py https://arxiv.org/pdf/xxxxx.pdf

# 指定输出格式
python main.py --format html ./paper.pdf
python main.py --format pdf ./paper.pdf

# 指定语言
python main.py --language en ./paper.pdf

# 指定详细程度
python main.py --detail brief ./paper.pdf
python main.py --detail detailed ./paper.pdf

# 组合选项
python main.py --format html --language en --detail detailed ./paper.pdf
```

### 批量处理

创建一个文本文件，每行一个 PDF 路径或 URL：

```bash
python main.py --batch papers_list.txt
```

### 历史记录

查看之前的分析历史：

```bash
python main.py --history
```

### 高级功能

```bash
# 启用引用提取
python main.py --extract-citations ./paper.pdf

# 启用图表分析
python main.py --analyze-figures ./paper.pdf

# 启用代码提取
python main.py --extract-code ./paper.pdf

# 启用可复现性评估
python main.py --assess-reproducibility ./paper.pdf

# 多论文对比
python main.py --compare paper1.pdf paper2.pdf paper3.pdf

# 从检查点恢复
python main.py --resume checkpoint.json

# 清除缓存
python main.py --clear-cache
```

### 智能自适应分析

启用自适应分析模式，系统会根据论文内容智能规划分析路径，并自动评估质量：

```bash
# 启用自适应分析（默认参数）
python main.py --adaptive ./paper.pdf

# 自定义迭代次数和质量阈值
python main.py --adaptive --max-iterations 5 --quality-threshold 0.8 ./paper.pdf

# 自适应分析 + 自定义输出格式
python main.py --adaptive --format html --language en ./paper.pdf
```

**自适应分析特性**：
- 智能分析规划：基于论文类型和内容自动决定分析维度和优先级
- 自动质量评估：每个分析维度完成后进行质量评估
- 迭代精炼：质量不足时自动重新分析（最多可配置迭代次数）
- 动态提取：根据论文内容自动决定是否执行引用、图表、代码等提取

### 交互式对话模式

启用交互式对话模式，在分析完成后可以向论文助手提问：

```bash
# 启用交互式对话模式
python main.py --interactive ./paper.pdf

# 交互式模式 + 自适应分析
python main.py --adaptive --interactive ./paper.pdf
```

**交互模式特性**：
- 初始完成论文分析后进入对话循环
- 可以向助手提问关于论文的任何问题
- 支持多轮对话，助手会记住上下文
- 输入 `exit` 或 `quit` 退出对话

## 模块结构

```
AutoResearch/
├── main.py                    # 命令行入口
├── paper_agent/
│   ├── graph.py              # LangGraph 工作流定义（标准 + 自适应 + 交互式）
│   ├── nodes.py              # 节点函数实现（含自适应决策节点）
│   ├── prompts.py            # 提示词模板（含分析和质量评估提示）
│   ├── pdf_reader.py         # PDF 读取工具
│   ├── chunking.py           # 章节提取模块
│   ├── formatters/           # 报告格式化器
│   │   ├── base_formatter.py
│   │   ├── markdown_formatter.py
│   │   ├── html_formatter.py
│   │   ├── pdf_formatter.py
│   │   ├── json_formatter.py
│   │   ├── bilingual_formatter.py
│   │   └── chart_generator.py
│   ├── cache/                # 缓存包
│   │   ├── lru_cache.py
│   │   ├── disk_cache.py
│   │   └── cache_key.py
│   ├── extractors/           # 内容提取器
│   │   ├── citation_extractor.py
│   │   ├── figure_extractor.py
│   │   ├── code_extractor.py
│   │   └── reproducibility_analyzer.py
│   ├── config.py             # 配置管理
│   ├── cache.py              # 缓存管理
│   ├── checkpoint.py         # 检查点管理
│   ├── progress.py           # 进度追踪
│   ├── history.py            # 历史记录
│   ├── batch.py              # 批量处理
│   ├── qa_mode.py            # 问答模式
│   ├── ui.py                 # 终端 UI
│   ├── comparison.py         # 论文对比
│   ├── research_assistant.py # 研究助手
│   ├── types.py              # 数据类型（含自适应分析类型）
│   ├── retry.py              # 重试逻辑
│   └── __init__.py
├── test/
│   ├── __init__.py
│   ├── test_adaptive_graph.py    # 自适应图测试
│   ├── test_quality_assessment.py # 质量评估测试
│   └── test_interactive_mode.py   # 交互模式测试
├── docs/
│   └── architecture.md       # 架构文档
├── requirements.txt           # 项目依赖
├── .env.example             # 环境变量模板
├── CLAUDE.md                # Claude Code 指导文档
└── README.md                 # 本文件
```

## CLI 参数参考

```
usage: main.py [-h] [--format {markdown,html,pdf,json}] [--language {zh,en}]
               [--detail {brief,standard,detailed}] [--resume PATH]
               [--clear-cache] [--batch FILE] [--history] [--qa-mode]
               [--extract-citations] [--analyze-figures] [--extract-code]
               [--assess-reproducibility] [--compare PDF [PDF ...]]
               [--adaptive, -a] [--interactive, -i] [--max-iterations N]
               [--quality-threshold T] [--user-feedback]
               [source]

positional arguments:
  source                PDF文件路径或URL

optional arguments:
  -h, --help            显示帮助信息
  --format, -f           输出格式: markdown, html, pdf, json
  --language, -l         语言: zh (中文) / en (英文)
  --detail, -d           详细程度: brief / standard / detailed
  --resume PATH          从检查点恢复分析
  --clear-cache          清除缓存
  --batch FILE           批量处理文件
  --history              查看分析历史
  --qa-mode              启用交互式问答模式
  --extract-citations    启用引用提取和分析
  --analyze-figures      启用图表分析
  --extract-code         启用代码提取
  --assess-reproducibility 启用可复现性评估
  --compare PDF [PDF ...] 对比多个论文

自适应分析选项：
  --adaptive, -a         启用智能自适应分析模式
  --interactive, -i      启用交互式对话模式
  --max-iterations N     最大迭代次数（默认: 3）
  --quality-threshold T  质量阈值 0-1（默认: 0.75）
  --user-feedback        启用用户反馈模式
```

## 开发说明

### 工作流设计

**标准模式**：
- 使用 LangGraph 条件分支根据论文类型动态选择分析路径
- 综述论文：background → related_work → innovation → results
- 实验论文：background → innovation → methodology → results
- 理论/未知论文：background → innovation → limitations → results

**自适应模式**（`--adaptive`）：
1. **智能分析规划** (`plan_analysis`): 根据论文类型和内容自动决定分析维度
2. **动态路由** (`route_after_planning`): 按优先级顺序执行分析维度
3. **质量评估** (`assess_quality`): 每个维度完成后评估分析质量
4. **迭代精炼** (`route_after_assessment`): 质量不足时自动重新分析
5. **动态提取**: 根据内容决定是否执行引用、图表、代码等提取

**交互式对话模式**（`--interactive`）：
1. 完成初始论文分析
2. 进入对话循环，用户可以提问
3. 基于分析结果回答问题
4. 支持多轮对话，保持上下文

### 扩展性

- 新增分析节点：在 `paper_agent/nodes.py` 中添加节点函数
- 新增输出格式：在 `paper_agent/formatters/` 中添加格式化器
- 新增提取功能：在 `paper_agent/extractors/` 中添加提取器
- 自定义提示词：在 `paper_agent/prompts.py` 中添加或修改提示词模板
- 新增决策节点：在 `paper_agent/graph.py` 中扩展路由逻辑

### 技术栈

- **LangGraph** - 条件分支工作流编排，支持 MessagesState 用于对话模式
- **LangChain** - LLM 抽象层
- **PyPDF2** - PDF 文本提取
- **requests** - HTTP 请求下载
- **可选依赖**：matplotlib、weasyprint、rich、tqdm

### 测试

```bash
# 运行所有测试
pytest test/

# 运行特定测试文件
pytest test/test_adaptive_graph.py
pytest test/test_quality_assessment.py
pytest test/test_interactive_mode.py

# 查看测试覆盖率
pytest --cov=paper_agent test/
```

**测试覆盖**：
- `test_adaptive_graph.py`: 自适应图结构、路由函数、工作流执行
- `test_quality_assessment.py`: 质量评估逻辑、阈值处理
- `test_interactive_mode.py`: 交互式对话功能

## 许可证

MIT License