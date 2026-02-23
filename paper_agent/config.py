"""
Configuration Module - Centralized configuration for the paper agent.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FormatterConfig:
    """Report output configuration."""
    output_format: str = "markdown"  # markdown, html, pdf, json
    language: str = "zh"             # zh, en
    detail_level: str = "standard"   # brief, standard, detailed
    include_charts: bool = False     # Whether to include charts
    include_latex: bool = True       # Whether to render LaTeX


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    cache_dir: str = ".cache"
    max_memory_size: int = 100       # Max items in memory cache
    disk_cache_ttl: int = 86400      # Disk cache TTL in seconds (24 hours)


@dataclass
class AnalysisConfig:
    """Analysis configuration."""
    # Content extraction
    max_content_chars: int = 50000   # Max characters to extract from PDF

    # Analysis dimensions
    analyze_background: bool = True
    analyze_innovation: bool = True
    analyze_results: bool = True
    analyze_methodology: bool = False
    analyze_related_work: bool = False
    analyze_limitations: bool = False

    # New extraction dimensions
    extract_citations: bool = False
    analyze_figures: bool = False
    extract_code: bool = False
    assess_reproducibility: bool = False

    # Parallel execution
    enable_parallel: bool = False
    max_parallel_workers: int = 2


@dataclass
class AppConfig:
    """Main application configuration combining all sub-configurations."""
    formatter: FormatterConfig = field(default_factory=FormatterConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)

    # Model configuration
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model_name: str = "gpt-4"
    temperature: float = 0.3

    # Paths
    work_dir: str = "."
    checkpoints_dir: str = ".checkpoints"
    history_db: str = ".history.db"

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0

    # Batch processing
    batch_size: int = 1
    batch_delay: float = 1.0


def get_config_from_env() -> AppConfig:
    """Create configuration from environment variables."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    return AppConfig(
        formatter=FormatterConfig(),
        cache=CacheConfig(),
        analysis=AnalysisConfig(),
        api_base=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("MODEL_NAME", "gpt-4"),
        temperature=float(os.getenv("TEMPERATURE", "0.3")),
    )