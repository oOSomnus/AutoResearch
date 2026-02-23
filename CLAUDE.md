# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoResearch is a LangGraph-based intelligent paper reading agent that analyzes academic papers and produces easy-to-understand reports. The agent supports multiple output formats, bilingual analysis, resumable workflows, and advanced content extraction.

### Core Features

**Basic Analysis Dimensions**:
- Background & motivation - Why was this research done?
- Innovation & core theory - What are the new contributions?
- Results & conclusions - What were the findings?

**Extended Analysis Dimensions** (dynamically selected based on paper type):
- Methodology - Experimental papers: experimental design and analysis
- Related work - Survey papers: research trends and domain overview
- Limitations - Theoretical papers: method limitations and future directions

**Advanced Features**:
- Multi-format output: Markdown, HTML, PDF, JSON
- Bilingual support: Chinese/English
- Detail level control: brief/standard/detailed
- Resumable analysis: checkpoint save and restore
- Batch processing: multi-paper batch analysis
- Interactive Q&A: RAG-based paper questioning
- Content extraction: citation analysis, figure analysis, code extraction, reproducibility assessment
- Cache optimization: result caching for faster repeat analysis
- **Intelligent adaptive analysis**: Dynamic analysis planning, automatic quality assessment and refinement
- **Interactive conversation mode**: Multi-turn dialogue with paper assistant
- **Smart content extraction**: LLM-driven title extraction, intelligent chapter detection, automatic figure/table annotation

## Setup

```bash
# Clone repository
git clone https://github.com/oOSomnus/AutoResearch.git
cd AutoResearch

# Install using uv tool (recommended for global installation)
uv tool install -e .
# Commands available: autoresearch and paper-agent

# Install using uv pip (editable mode for development)
uv pip install -e .

# Or using pip
pip install -e .

# Or from requirements.txt (legacy)
uv pip install -r requirements.txt

# Or install with all optional features
uv tool install -e ".[all]"
# or
uv pip install -e ".[all]"
```

**uv tool install vs uv pip install -e:**

| Installation Method | Location | Scope | Recommended For |
|-------------------|---------|-------|----------------|
| `uv tool install -e .` | Global tool directory | Any terminal session | Daily use, no venv activation needed |
| `uv pip install -e .` | Current virtual environment | Current venv only | Development/debugging with frequent code changes |

**Optional dependency groups:**
- `output` - PDF output and chart generation (weasyprint, matplotlib)
- `interactive` - Progress bars, enhanced terminal UI (tqdm, rich, click)
- `performance` - Token counting, persistent caching (tiktoken, diskcache)

Install specific optional features:
```bash
uv tool install -e ".[output]"
uv pip install -e ".[interactive]"
pip install -e ".[performance]"
```

Configure environment:
```bash
cp .env.example .env
# Edit .env with your OPENAI_API_BASE and OPENAI_API_KEY
```

Required environment variables (in `.env`):
- `OPENAI_API_BASE` - OpenAI-compatible API endpoint
- `OPENAI_API_KEY` - API authentication key
- `MODEL_NAME` - Model to use (default: gpt-4)

## Running the Agent

After installation, you can run the agent in three ways:

### Method 1: Using CLI Commands (Recommended)

Installation creates two CLI entry points:
- `uv tool install -e .` makes them available globally (any terminal)
- `uv pip install -e .` makes them available in the current virtual environment

```bash
# Interactive mode (prompts for PDF path/URL)
autoresearch
# or
paper-agent

# Direct mode with file path or URL
autoresearch ./paper.pdf
autoresearch https://arxiv.org/pdf/xxxx.pdf

# Specify output format
autoresearch --format html ./paper.pdf
autoresearch --format pdf ./paper.pdf

# Specify language
autoresearch --language en ./paper.pdf

# Specify detail level
autoresearch --detail brief ./paper.pdf

# Adaptive analysis mode
autoresearch --adaptive ./paper.pdf

# Interactive Q&A mode
autoresearch --interactive ./paper.pdf

# Batch processing
autoresearch --batch papers_list.txt

# View history
autoresearch --history

# Enable advanced features
autoresearch --extract-citations ./paper.pdf
autoresearch --analyze-figures ./paper.pdf
autoresearch --extract-code ./paper.pdf
autoresearch --assess-reproducibility ./paper.pdf

# Multi-paper comparison
autoresearch --compare paper1.pdf paper2.pdf

# Resume from checkpoint
autoresearch --resume checkpoint.json

# Clear cache
autoresearch --clear-cache
```

### Method 2: Using Python Directly (Compatible)

```bash
# Interactive mode (prompts for PDF path/URL)
python main.py

# Direct mode with file path or URL
python main.py ./paper.pdf
python main.py https://arxiv.org/pdf/xxxx.pdf

# All options work the same as CLI commands
python main.py --adaptive ./paper.pdf
python main.py --interactive ./paper.pdf
```

### Method 3: Run Graph Directly (for testing)

```bash
python -m paper_agent.graph <pdf_path_or_url>
```

## Architecture

The project uses **LangGraph** to orchestrate conditional branching workflows through multiple nodes.

### Core Workflow Nodes

1. **fetch_pdf** - Downloads PDF from URL or validates local file, extracts title
2. **extract_content** - Extracts text from PDF and chapters
3. **detect_paper_type** - Detects paper type (survey/experimental/theoretical)
4. **analyze_background** - Uses LLM to analyze research background and motivation
5. **analyze_innovation** - Uses LLM to analyze innovation and core theory
6. **analyze_methodology** - Uses LLM to analyze experimental methodology (for experimental papers)
7. **analyze_related_work** - Uses LLM to analyze related work (for survey papers)
8. **analyze_limitations** - Uses LLM to analyze limitations (for theoretical papers)
9. **analyze_results** - Uses LLM to analyze results and conclusions
10. **generate_report** - Combines all analyses into a report using formatters
11. **save_report** - Saves report to current directory

**Advanced Extraction Nodes** (optional):
- **extract_citations** - Extract and analyze citations
- **analyze_figures** - Analyze figures and tables
- **extract_code** - Extract code snippets and algorithms
- **assess_reproducibility** - Assess paper reproducibility

**Adaptive Analysis Nodes** (Phase 5):
- **plan_analysis** - Intelligently plans which dimensions to analyze based on paper content
- **assess_quality** - Evaluates analysis quality (completeness, depth, clarity, accuracy)
- **gather_user_feedback** - Collects user feedback on key decisions (interactive mode)

### Workflow Paths

**Standard Mode**:
- **Survey papers**: background → related_work → innovation → results
- **Experimental papers**: background → innovation → methodology → results
- **Theoretical/Unknown papers**: background → innovation → limitations → results

**Adaptive Mode** (`--adaptive` flag):
1. fetch_pdf → extract_content → detect_paper_type → **plan_analysis**
2. Dynamic routing based on analysis plan (dimensions executed in priority order)
3. After each analysis: **assess_quality**
4. If quality below threshold: return to analysis node for refinement (max N iterations)
5. Once all dimensions complete: generate_report → save_report

**Interactive Q&A Mode** (`--interactive` flag):
1. Run adaptive analysis (run_initial_analysis)
2. Enter conversation loop with user
3. answer_question responds to user queries
4. User can exit with "exit", "quit", etc.

### Module Structure

**Core Layer**:
- **`paper_agent/graph.py`** - Defines three workflow modes:
  - `create_paper_agent_graph()` - Standard linear workflow (backward compatible)
  - `create_adaptive_paper_agent_graph()` - Adaptive workflow with quality assessment
  - `create_interactive_paper_agent_graph()` - Interactive Q&A workflow
- **`paper_agent/nodes/`** - Node functions organized by category:
  - `base.py` - AgentState TypedDict and get_llm() utility
  - `input.py` - PDF fetching and content extraction nodes
  - `analysis.py` - Core analysis dimension nodes
  - `output.py` - Report generation and saving nodes
  - `adaptive.py` - Adaptive analysis planning and quality assessment
  - `extraction.py` - Content extraction nodes
- **`paper_agent/prompts.py`** - Bilingual prompt templates including planning and quality assessment

**Processing Layer**:
- **`paper_agent/pdf_reader.py`** - PDF extraction utilities using PyPDF2, plus URL download
- **`paper_agent/chunking.py`** - Chapter extraction and intelligent content selection

**Output Layer**:
- **`paper_agent/formatters/`** - Report output formatters
  - `base_formatter.py` - Abstract base class with markdown list normalization
  - `markdown_formatter.py` - Markdown output (default)
  - `html_formatter.py` - HTML output with MathJax support
  - `pdf_formatter.py` - PDF output via weasyprint
  - `json_formatter.py` - Structured JSON output
  - `bilingual_formatter.py` - Language switching wrapper
  - `chart_generator.py` - matplotlib-based chart generation

**Enhancement Layer**:
- **`paper_agent/cache.py`** - Cache manager for analysis results
- **`paper_agent/checkpoint.py`** - Checkpoint management for resumable analysis
- **`paper_agent/progress.py`** - Progress tracking with tqdm
- **`paper_agent/history.py`** - SQLite-based analysis history management
- **`paper_agent/batch.py`** - Batch processing coordinator
- **`paper_agent/qa_mode.py`** - Interactive RAG-based Q&A mode
- **`paper_agent/ui.py`** - Rich terminal UI with fallback support

**Analysis Layer**:
- **`paper_agent/extractors/`** - Content extractors
  - `citation_extractor.py` - Citation extraction and analysis
  - `figure_extractor.py` - Figure/table extraction
  - `code_extractor.py` - Code/algorithm extraction
  - `reproducibility_analyzer.py` - Reproducibility assessment
- **`paper_agent/comparison.py`** - Multi-paper comparison
- **`paper_agent/research_assistant.py`** - Research assistant mode

**Testing Layer**:
- **`test/`** - Test suite
  - `test_adaptive_graph.py` - Tests for adaptive graph functionality
  - `test_quality_assessment.py` - Tests for quality assessment
  - `test_interactive_mode.py` - Tests for interactive Q&A mode

**Support Layer**:
- **`pyproject.toml`** - Python project configuration with modern packaging standard
  - CLI entry points: `autoresearch` and `paper-agent`
  - Optional dependency groups: output, interactive, performance, all, dev
  - Build system: hatchling with support for `uv tool install` global installation
  - Tool configurations: black, isort, ruff, mypy, pytest, coverage
- **`paper_agent/config.py`** - Configuration management
- **`paper_agent/types.py`** - Data structure definitions including:
  - `AnalysisDecision` - Analysis planning result from LLM (Phase 5)
  - `QualityAssessment` - Quality evaluation result (Phase 5)
  - `FigureInfo`, `TableInfo`, `CodeSnippet`, `CitationInfo` - Extraction types
  - `ReproducibilityAssessment`, `ComparisonResult` - Additional analysis types
- **`paper_agent/cache/`** - Caching utilities (LRU cache, disk cache)
- **`paper_agent/retry.py`** - Exponential backoff retry logic

### AgentState

The TypedDict passed between nodes contains:

**Core Fields**:
- `source` - Original file path or URL
- `pdf_path` - Local path to PDF file
- `title` - Extracted paper title
- `content` - Extracted PDF text
- `chapters` - List of extracted chapters with type info
- `paper_type` - Paper type: survey/experimental/theoretical/unknown
- `background` - Analysis result for background
- `innovation` - Analysis result for innovation
- `results` - Analysis result for results
- `methodology` - Analysis result for methodology
- `related_work` - Analysis result for related work
- `limitations` - Analysis result for limitations
- `report` - Final formatted report

**Output Configuration**:
- `output_format` - Output format: markdown/html/pdf/json
- `language` - Target language: zh/en
- `detail_level` - Detail level: brief/standard/detailed

**Extraction Fields** (Phase 4):
- `citations` - Citation analysis text
- `figures` - Figure analysis text
- `code` - Code extraction text
- `reproducibility` - Reproducibility assessment text
- `citations_list` - List of CitationInfo objects
- `figures_list` - List of FigureInfo objects
- `code_snippets` - List of CodeSnippet objects
- `reproducibility_score` - Reproducibility score (0-1)

**Progress & Checkpoint Fields** (Phase 2):
- `completed_nodes` - List of completed node names
- `checkpoint_path` - Path to checkpoint file
- `cache_key` - Cache key for the analysis

**Adaptive Analysis Fields** (Phase 5):
- `analysis_plan` - Dict containing analysis plan (dimensions, priority, reasoning)
- `quality_scores` - Dict mapping dimensions to their quality metrics
- `iteration_count` - Dict tracking how many iterations each dimension has had
- `needs_refinement` - List of dimensions that need re-analysis
- `should_exit` - Boolean flag for early termination
- `research_mode` - Current mode: 'auto', 'interactive', 'manual'
- `current_dimension` - Currently analyzed dimension
- `dimension_to_assess` - Dimension to assess for quality
- `max_iterations` - Maximum refinement iterations per dimension (default: 3)
- `quality_threshold` - Minimum quality score to accept (default: 0.75)

## Development Notes

### Workflow Design

- The project uses LangGraph conditional branching based on paper type
- Workflows adapt dynamically: survey, experimental, and theoretical papers take different analysis paths
- All nodes support checkpoint saving and cache checking for resumability
- Adaptive mode adds intelligent planning and quality assessment loops

### Content Processing

- Uses chapter-based extraction to handle long papers (no 30k character limit)
- Content selection is optimized per analysis type for better accuracy
- PDF hash is calculated for cache key generation
- **Smart content extraction (Phase 6)**:
  - LLM-driven title extraction with multi-stage fallback (LLM → metadata → heuristics)
  - Improved chapter detection with reduced false positives (225+ → ~11 valid chapters)
  - Intelligent content selection: exact match → partial match → semantic proximity
  - Smart truncation: preserves beginning (70%) and end (30%) when exceeding token limits
  - Automatic figure/table detection and annotation for context passing
  - Expanded keyword lists per analysis type for better matching

### Prompts

- All prompts are designed for simple, conversational output accessible to high school graduates
- Bilingual prompts are available for both Chinese and English
- Detail level modifiers control output verbosity
- Phase 5 added prompts for analysis planning and quality assessment
- **Phase 6: Balanced response style improvements**:
  - Prompts now require both simple language AND specific technical details
  - Background analysis: requires specific problem statements and data/statistics
  - Innovation analysis: simple introduction + detailed implementation steps, requires figure/formula references
  - Results analysis: requires specific quantitative data and table/figure references
  - Figure/table context is injected separately for better utilization
  - Report formatter now includes dedicated "Figures & Tables" section
- **Four-tier progressive analysis structure** (all analysis dimensions):
  - **Tier 1: 通俗理解/ Layman Understanding** - Simple explanation with everyday metaphors, accessible to non-experts
  - **Tier 2: 关键机制/Key Mechanisms** - Technical overview explaining core principles
  - **Tier 3: 具体实现/Specific Implementation** - Detailed technical steps, parameters, formulas, and code
  - **Tier 4: 深层洞察/Deep Insights** - Research significance with external real-world examples and future directions
- Each prompt requires 1-2 external real-world examples (not just from the paper) to illustrate concepts and applications

### Output Formats

- Default: Markdown
- HTML: Supports MathJax for LaTeX rendering, responsive design
- PDF: Generated via HTML conversion using weasyprint (optional dependency)
- JSON: Structured output with all analysis data

### Error Handling

- Nodes include fallback mechanisms when LLM fails
- Optional dependencies gracefully degrade to simple functionality
- Cache and checkpoint systems help with recovery and debugging
- Quality assessment failures gracefully default to accepting the result

### Extensibility

**Adding a new node**:
1. Add node function in `paper_agent/nodes/` (choose appropriate file: base.py, input.py, analysis.py, output.py, adaptive.py, or extraction.py)
2. Update `AgentState` in `paper_agent/nodes/base.py` if needed
3. Add routing function in `paper_agent/graph.py`
4. Add node to workflow in `create_paper_agent_graph()` or `create_adaptive_paper_agent_graph()`
5. Export the node in `paper_agent/nodes/__init__.py`
6. Add prompt template in `paper_agent/prompts.py`

**Adding a new output format**:
1. Create new formatter class in `paper_agent/formatters/` inheriting from `BaseFormatter`
2. Implement `format_report()` method
3. Add to formatters `__init__.py`
4. Update main.py CLI options

**Adding a new extraction feature**:
1. Create extractor class in `paper_agent/extractors/`
2. Add corresponding node function in `paper_agent/nodes/extraction.py`
3. Export the node in `paper_agent/nodes/__init__.py`
4. Add prompt template in `paper_agent/prompts.py`
5. Add CLI flag in main.py

**Adding a new adaptive analysis dimension**:
1. Ensure the dimension is in `plan_analysis` prompts
2. Add mapping in `route_after_planning` if needed
3. Add corresponding analysis node
4. Add quality assessment support if applicable

### Documentation Updates

**IMPORTANT**: After any code changes, you MUST also update the relevant documentation files:

1. **README.md** - Update usage examples, feature descriptions, and installation instructions if affected
2. **docs/** - Update any related documentation files in the docs directory (API docs, architecture docs, user guides, etc.)
3. **CLAUDE.md** - Update this file with new architecture decisions, workflow changes, and development guidelines

This ensures that documentation stays synchronized with the codebase and users have accurate, up-to-date information.

## Key Design Decisions

1. **State Management**: Extended AgentState with optional fields for backward compatibility
2. **Caching Strategy**: Dual-layer caching (memory LRU + persistent disk) with content-based keys
3. **Parallel Execution**: Independent analysis nodes can be parallelized in future
4. **Bilingual Support**: Language switching mode (--language parameter) for single-language output
5. **Default Cache**: Results are cached by default for improved performance
6. **Adaptive Analysis**: Quality assessment adds extra LLM calls but improves result quality
7. **Backward Compatibility**: Standard mode remains as default for existing users
8. **Multi-Stage Title Extraction**: LLM-first approach with heuristics as fallback for maximum accuracy
9. **Balanced Response Style**: Prompts require both accessibility and technical depth for better utility
10. **Figure Context Injection**: Automatic figure/table detection and annotation improves analysis quality
11. **Four-Tier Progressive Analysis**: Analysis prompts use a four-tier structure (Layman → Key Mechanisms → Specific Implementation → Deep Insights) with external examples for comprehensive understanding
12. **Markdown List Normalization**: Formatters automatically normalize list indentation to proper markdown standard (2+ spaces per nesting level) for correct rendering

## Dependencies

**Core Dependencies**:
- langgraph>=0.2.0
- langchain>=0.3.0
- langchain-openai>=0.2.0
- PyPDF2>=3.0.0
- requests>=2.31.0
- python-dotenv>=1.0.0
- chromadb>=0.4.0

**Optional Dependencies**:
- weasyprint>=60.0 - PDF output
- matplotlib>=3.8.0 - Chart generation
- tqdm>=4.66.0 - Progress bars
- rich>=13.7.0 - Enhanced terminal UI
- click>=8.1.0 - CLI framework
- tiktoken>=0.5.0 - Token counting
- diskcache>=5.6.0 - Persistent caching

**Testing Dependencies**:
- pytest>=7.0.0 - Test framework
- pytest-cov>=4.0.0 - Test coverage reporting