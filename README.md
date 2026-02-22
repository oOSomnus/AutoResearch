# AutoResearch

> 基于 LangGraph 的论文阅读 Agent，快速理解学术论文的核心内容

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-green)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 简介

AutoResearch 是一个智能论文阅读助手，能够自动分析学术论文并生成易于理解的 Markdown 报告。它提取论文的"三大核心要素"：

- **背景与动机** - 为什么要做这个研究？
- **创新与核心理论** - 有什么新的贡献和方法？
- **结果与结论** - 得到了什么结果？

**特点**：
- 支持本地 PDF 文件和在线 URL
- 使用 LangGraph 构建顺序工作流
- 输出简单易懂的非学术化语言，适合高中毕业生阅读
- 自动生成结构化的 Markdown 报告

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

输入 `q` 退出，输入 `h` 查看帮助。

### 直接模式

直接指定文件路径或 URL 进行分析：

```bash
# 分析本地 PDF 文件
python main.py ./paper.pdf

# 分析在线 PDF
python main.py https://arxiv.org/pdf/xxxxx.pdf

# 查看帮助
python main.py -h
```

### 作为模块调用

```python
from paper_agent.graph import run_paper_analysis

final_state = run_paper_analysis("./paper.pdf")
print(final_state['report'])
```

## 输出示例

分析完成后，会在当前目录生成 `<filename>_report.md` 报告文件，格式如下：

```markdown
# 论文分析报告

## 原始信息
- 来源: https://arxiv.org/pdf/2301.xxxxx.pdf
- 标题: Your Paper Title

## 一、背景&原因
[简洁说明研究背景和动机，100-200字]

## 二、创新&核心理论
[详细展开核心方法，400-800字]
- 核心算法原理
- 模型架构组件
- 训练策略
- 与现有方法的对比

## 三、结果
[简洁总结主要发现，100-200字]
```

## 架构设计

AutoResearch 使用 **LangGraph** 构建一个严格顺序的 StateGraph 工作流，包含 7 个节点：

```
fetch_pdf
    ↓
extract_content
    ↓
analyze_background
    ↓
analyze_innovation
    ↓
analyze_results
    ↓
generate_report
    ↓
save_report
```

### 模块结构

```
AutoResearch/
├── main.py                 # 命令行入口
├── paper_agent/
│   ├── graph.py            # LangGraph 工作流定义
│   ├── nodes.py            # 各节点实现
│   ├── prompts.py          # 中文提示词模板
│   ├── pdf_reader.py       # PDF 读取与下载工具
│   └── __init__.py
├── requirements.txt        # 项目依赖
├── .env.example           # 环境变量模板
└── README.md              # 本文件
```

### AgentState 状态流转

节点间通过 `AgentState` 传递信息：

| 字段 | 说明 |
|------|------|
| `source` | 原始文件路径或 URL |
| `pdf_path` | 本地 PDF 文件路径 |
| `title` | 论文标题 |
| `content` | 提取的文本（最多 30k 字符） |
| `background` | 背景分析结果 |
| `innovation` | 创新分析结果 |
| `results` | 结果分析结果 |
| `report` | 最终 Markdown 报告 |

### 技术栈

- **LangGraph** - 工作流编排
- **LangChain** - LLM 抽象层
- **PyPDF2** - PDF 文本提取
- **requests** - HTTP 请求下载

## 开发说明

- PDF 内容限制为 30k 字符（约 10k tokens）以避免超出模型限制
- 提示词设计为输出简单、口语化的中文，这是有意设计，非 bug
- 节点错误处理包含 LLM 失败时的原始文本格式化回退
- 工作流严格顺序执行，无分支或循环

## 许可证

MIT License
