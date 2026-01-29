"""
Data visualization module for EDA
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Dict
from pathlib import Path
from src.utils.logger import get_logger
from src.analysis.eda import EDAAnalyzer

# Optional plotly imports
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Plotly not available. Install with: pip install plotly")

logger = get_logger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


class DataVisualizer:
    """Class for creating visualizations"""

    def __init__(self, eda_analyzer: Optional[EDAAnalyzer] = None):
        """
        Initialize DataVisualizer

        Args:
            eda_analyzer: EDAAnalyzer instance
        """
        self.eda_analyzer = eda_analyzer or EDAAnalyzer()
        self.logger = get_logger(__name__)

    def plot_access_trajectory(
        self,
        save_path: Optional[Path] = None,
        show_events: bool = True
    ):
        """
        Plot Ethiopia's account ownership trajectory (2011-2024)

        Args:
            save_path: Optional path to save figure
            show_events: Whether to overlay events

        Returns:
            Plotly figure (if plotly available)
        """
        if not PLOTLY_AVAILABLE:
            self.logger.error("Plotly is required for visualization. Install with: pip install plotly")
            return None
            
        trajectory = self.eda_analyzer.analyze_access_trajectory()

        if trajectory.empty:
            self.logger.warning("No access trajectory data available")
            return None

        fig = go.Figure()

        # Plot trajectory
        fig.add_trace(go.Scatter(
            x=trajectory["year"],
            y=trajectory["value_numeric"],
            mode="lines+markers",
            name="Account Ownership",
            line=dict(width=3, color="#1f77b4"),
            marker=dict(size=10)
        ))

        # Add events if requested
        if show_events:
            events = self.eda_analyzer.get_event_timeline()
            if not events.empty:
                for _, event in events.iterrows():
                    fig.add_vline(
                        x=event["event_date"],
                        line_dash="dash",
                        line_color="gray",
                        annotation_text=event.get("category", "Event")
                    )

        fig.update_layout(
            title="Ethiopia Account Ownership Trajectory (2011-2024)",
            xaxis_title="Year",
            yaxis_title="Account Ownership (%)",
            hovermode="x unified",
            template="plotly_white"
        )

        if save_path:
            fig.write_html(str(save_path))
            self.logger.info(f"Figure saved to {save_path}")

        return fig

    def plot_temporal_coverage(
        self,
        save_path: Optional[Path] = None
    ):
        """
        Create temporal coverage heatmap

        Args:
            save_path: Optional path to save figure

        Returns:
            Plotly figure (if plotly available)
        """
        if not PLOTLY_AVAILABLE:
            self.logger.error("Plotly is required for visualization. Install with: pip install plotly")
            return None
            
        coverage = self.eda_analyzer.get_temporal_coverage()

        if coverage.empty:
            self.logger.warning("No temporal coverage data available")
            return None

        fig = go.Figure(data=go.Heatmap(
            z=coverage.values,
            x=coverage.columns,
            y=coverage.index,
            colorscale="Blues",
            showscale=True
        ))

        fig.update_layout(
            title="Temporal Coverage: Indicators by Year",
            xaxis_title="Year",
            yaxis_title="Indicator Code",
            template="plotly_white"
        )

        if save_path:
            fig.write_html(str(save_path))
            self.logger.info(f"Figure saved to {save_path}")

        return fig

    def plot_event_timeline(
        self,
        save_path: Optional[Path] = None
    ):
        """
        Create timeline visualization of events

        Args:
            save_path: Optional path to save figure

        Returns:
            Plotly figure (if plotly available)
        """
        if not PLOTLY_AVAILABLE:
            self.logger.error("Plotly is required for visualization. Install with: pip install plotly")
            return None
            
        events = self.eda_analyzer.get_event_timeline()

        if events.empty:
            self.logger.warning("No events data available")
            return None

        fig = go.Figure()

        # Color map for event categories
        categories = events["category"].unique()
        colors = px.colors.qualitative.Set3[:len(categories)]
        color_map = dict(zip(categories, colors))

        for _, event in events.iterrows():
            fig.add_trace(go.Scatter(
                x=[event["event_date"], event["event_date"]],
                y=[0, 1],
                mode="markers+text",
                name=event.get("category", "Unknown"),
                marker=dict(size=15, color=color_map.get(event["category"], "gray")),
                text=[event.get("source_name", "")],
                textposition="top center"
            ))

        fig.update_layout(
            title="Event Timeline",
            xaxis_title="Date",
            yaxis_title="",
            yaxis=dict(showticklabels=False),
            template="plotly_white",
            showlegend=True
        )

        if save_path:
            fig.write_html(str(save_path))
            self.logger.info(f"Figure saved to {save_path}")

        return fig

    def plot_correlation_heatmap(
        self,
        indicators: Optional[List[str]] = None,
        save_path: Optional[Path] = None
    ):
        """
        Plot correlation heatmap between indicators

        Args:
            indicators: List of indicator codes (None for all)
            save_path: Optional path to save figure

        Returns:
            Plotly figure (if plotly available)
        """
        if not PLOTLY_AVAILABLE:
            self.logger.error("Plotly is required for visualization. Install with: pip install plotly")
            return None
            
        correlation = self.eda_analyzer.analyze_correlations(indicators)

        if correlation.empty:
            self.logger.warning("No correlation data available")
            return None

        fig = go.Figure(data=go.Heatmap(
            z=correlation.values,
            x=correlation.columns,
            y=correlation.index,
            colorscale="RdBu",
            zmid=0,
            text=correlation.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 10},
            showscale=True
        ))

        fig.update_layout(
            title="Indicator Correlation Matrix",
            xaxis_title="Indicator",
            yaxis_title="Indicator",
            template="plotly_white",
            width=800,
            height=800
        )

        if save_path:
            fig.write_html(str(save_path))
            self.logger.info(f"Figure saved to {save_path}")

        return fig

    def plot_usage_trends(
        self,
        save_path: Optional[Path] = None
    ):
        """
        Plot usage trends over time

        Args:
            save_path: Optional path to save figure

        Returns:
            Plotly figure (if plotly available)
        """
        if not PLOTLY_AVAILABLE:
            self.logger.error("Plotly is required for visualization. Install with: pip install plotly")
            return None
            
        usage_trends = self.eda_analyzer.analyze_usage_trends()

        if usage_trends.empty:
            self.logger.warning("No usage trends data available")
            return None

        fig = go.Figure()

        for indicator in usage_trends["indicator_code"].unique():
            indicator_data = usage_trends[usage_trends["indicator_code"] == indicator]
            fig.add_trace(go.Scatter(
                x=indicator_data["year"],
                y=indicator_data["value_numeric"],
                mode="lines+markers",
                name=indicator
            ))

        fig.update_layout(
            title="Usage Trends Over Time",
            xaxis_title="Year",
            yaxis_title="Value (%)",
            hovermode="x unified",
            template="plotly_white"
        )

        if save_path:
            fig.write_html(str(save_path))
            self.logger.info(f"Figure saved to {save_path}")

        return fig
