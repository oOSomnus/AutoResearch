# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoResearch is a LangGraph-based paper reading agent that analyzes academic papers and produces easy-to-understand Markdown reports. The agent extracts the "three elements" of a paper: background & motivation, innovation & core theory, and results & conclusions.

## Setup

```bash
# Install dependencies
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_BASE and OPENAI_API_KEY
```

Required environment variables (in `.env`):
- `OPENAI_API_BASE` - OpenAI-compatible API endpoint
- `OPENAI_API_KEY` - API authentication key
- `MODEL_NAME` - Model to use (default: gpt-4)

## Running the Agent

```bash
# Interactive mode (prompts for PDF path/URL)
python main.py

# Direct mode with file path or URL
python main.py ./paper.pdf
python main.py https://arxiv.org/pdf/xxxx.pdf

# Run graph directly (for testing)
python -m paper_agent.graph <pdf_path_or_url>
```

## Architecture

The project uses **LangGraph** to orchestrate a sequential workflow through 7 nodes:

1. **fetch_pdf** (`paper_agent/nodes.py`) - Downloads PDF from URL or validates local file, extracts title
2. **extract_content** - Extracts text from PDF (limited to 30k chars to avoid token limits)
3. **analyze_background** - Uses LLM to analyze research background and motivation
4. **analyze_innovation** - Uses LLM to analyze innovation and core theory
5. **analyze_results** - Uses LLM to analyze results and conclusions
6. **generate_report** - Combines all analyses into a Markdown report
7. **save_report** - Saves report to current directory as `<filename>_report.md`

### Module Structure

- **`paper_agent/graph.py`** - Defines the StateGraph workflow with `AgentState` and connects all nodes sequentially. Entry point is `fetch_pdf`, exit point is `save_report`.
- **`paper_agent/nodes.py`** - Contains all 7 node functions. Each node accepts `AgentState` and returns updated `AgentState`. Uses `get_llm()` to create LangChain `ChatOpenAI` instances.
- **`paper_agent/prompts.py`** - Chinese prompt templates for each analysis phase. All prompts emphasize simple, non-academic language accessible to high school graduates.
- **`paper_agent/pdf_reader.py`** - PDF extraction utilities using PyPDF2, plus URL download via requests. Handles title extraction from PDF metadata or first page.

### AgentState

The TypedDict passed between nodes contains:
- `source` - Original file path or URL
- `pdf_path` - Local path to PDF file
- `title` - Extracted paper title
- `content` - Extracted PDF text (max 30k chars)
- `background` - Analysis result for background
- `innovation` - Analysis result for innovation
- `results` - Analysis result for results
- `report` - Final Markdown report

## Development Notes

- The project uses LangChain's `ChatOpenAI` for LLM calls, supporting any OpenAI-compatible API
- PDF content is truncated to 30k characters (~10k tokens) to stay within model limits
- Prompts are designed to produce simple, conversational Chinese output - this is intentional, not a bug
- Error handling in nodes includes fallback to raw text formatting if LLM fails
- The workflow is strictly sequential (no branching or cycles) - nodes execute in order and pass state linearly