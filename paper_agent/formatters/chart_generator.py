"""
Chart Generator - Generate charts and visualizations from analysis results.
"""
import io
import base64
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Optional matplotlib import - will be loaded when needed
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    matplotlib.rcParams['axes.unicode_minus'] = False
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


@dataclass
class ChartData:
    """Data structure for chart generation."""
    labels: List[str]
    values: List[float]
    title: str = ""
    chart_type: str = "bar"  # bar, pie, line, radar
    colors: Optional[List[str]] = None
    x_label: str = ""
    y_label: str = ""


class ChartGenerator:
    """Generate charts from analysis data."""

    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize the chart generator.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.charts: List[ChartData] = []

        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib is not installed. Chart generation is disabled.")
            print("Install it with: pip install matplotlib>=3.8.0")

    def add_chart(self, chart_data: ChartData) -> None:
        """Add a chart to the generator."""
        self.charts.append(chart_data)

    def generate_all_charts(self) -> Dict[str, str]:
        """
        Generate all charts and return as base64-encoded images.

        Returns:
            Dictionary mapping chart names to base64 image data
        """
        if not MATPLOTLIB_AVAILABLE:
            return {}

        results = {}

        for i, chart_data in enumerate(self.charts):
            chart_name = f"chart_{i+1}"
            img_data = self._generate_chart(chart_data)
            results[chart_name] = img_data

        return results

    def _generate_chart(self, chart_data: ChartData) -> str:
        """
        Generate a single chart.

        Args:
            chart_data: Chart data

        Returns:
            Base64-encoded image data
        """
        if not MATPLOTLIB_AVAILABLE:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_data.chart_type == "bar":
            self._generate_bar_chart(ax, chart_data)
        elif chart_data.chart_type == "pie":
            self._generate_pie_chart(ax, chart_data)
        elif chart_data.chart_type == "line":
            self._generate_line_chart(ax, chart_data)
        elif chart_data.chart_type == "radar":
            self._generate_radar_chart(fig, ax, chart_data)
        else:
            self._generate_bar_chart(ax, chart_data)

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        # Encode as base64
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_data}"

    def _generate_bar_chart(self, ax, chart_data: ChartData) -> None:
        """Generate a bar chart."""
        colors = chart_data.colors or ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']

        bars = ax.bar(chart_data.labels, chart_data.values, color=colors[:len(chart_data.labels)])
        ax.set_title(chart_data.title)
        ax.set_xlabel(chart_data.x_label)
        ax.set_ylabel(chart_data.y_label)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

    def _generate_pie_chart(self, ax, chart_data: ChartData) -> None:
        """Generate a pie chart."""
        colors = chart_data.colors or ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']

        ax.pie(chart_data.values, labels=chart_data.labels, colors=colors[:len(chart_data.labels)],
               autopct='%1.1f%%', startangle=90)
        ax.set_title(chart_data.title)
        ax.axis('equal')
        plt.tight_layout()

    def _generate_line_chart(self, ax, chart_data: ChartData) -> None:
        """Generate a line chart."""
        colors = chart_data.colors or ['#667eea']

        ax.plot(chart_data.labels, chart_data.values, marker='o', color=colors[0], linewidth=2)
        ax.set_title(chart_data.title)
        ax.set_xlabel(chart_data.x_label)
        ax.set_ylabel(chart_data.y_label)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

    def _generate_radar_chart(self, fig, ax, chart_data: ChartData) -> None:
        """Generate a radar chart."""
        try:
            import numpy as np
        except ImportError:
            print("Warning: numpy is not installed. Radar chart generation is disabled.")
            return

        n = len(chart_data.labels)
        angles = [n / float(n) * 2 * np.pi for _ in range(n)]
        angles += angles[:1]

        values = chart_data.values + chart_data.values[:1]

        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles, values, 'o-', linewidth=2, color='#667eea')
        ax.fill(angles, values, alpha=0.25, color='#667eea')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(chart_data.labels)
        ax.set_title(chart_data.title, pad=20)
        plt.tight_layout()

    @staticmethod
    def extract_charts_from_state(state: Dict[str, Any]) -> List[ChartData]:
        """
        Extract chart data from analysis state.

        This attempts to identify quantitative data in the analysis
        that can be visualized.

        Args:
            state: Analysis state

        Returns:
            List of chart data
        """
        charts = []

        # Try to extract data from reproducibility score
        if "reproducibility_score" in state:
            score = state["reproducibility_score"]
            charts.append(ChartData(
                labels=["可复现性评分"],
                values=[score * 100],  # Convert to percentage
                title="可复现性评估",
                chart_type="bar",
                colors=['#667eea' if score > 0.7 else '#f093fb' if score > 0.4 else '#ff6b6b'],
                x_label="",
                y_label="分数 (0-100)"
            ))

        # Try to extract citation counts (if available)
        if "citations_list" in state and state["citations_list"]:
            # Count by citation type
            type_counts = {}
            for citation in state["citations_list"]:
                c_type = citation.get("citation_type", "other")
                type_counts[c_type] = type_counts.get(c_type, 0) + 1

            if type_counts:
                type_names = {
                    "foundational": "基础文献",
                    "recent": "近期研究",
                    "competing": "竞争方法",
                    "other": "其他"
                }
                charts.append(ChartData(
                    labels=[type_names.get(k, k) for k in type_counts.keys()],
                    values=list(type_counts.values()),
                    title="引用类型分布",
                    chart_type="pie"
                ))

        return charts

    def generate_html_chart_tags(self, chart_data: str) -> str:
        """
        Generate HTML img tags for a base64-encoded chart.

        Args:
            chart_data: Base64-encoded image data

        Returns:
            HTML img tag
        """
        return f'<img src="{chart_data}" alt="Chart" style="max-width: 100%; height: auto; border-radius: 5px;">'