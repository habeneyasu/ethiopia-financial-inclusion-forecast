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

# Optional plotly imports
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

logger = get_logger(__name__)

if not PLOTLY_AVAILABLE:
    logger.warning("Plotly not available. Install with: pip install plotly")

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
                # Extract years from event dates before iterating
                events_with_years = events.copy()
                events_with_years["event_year"] = events_with_years["event_date"].apply(
                    lambda x: int(pd.to_datetime(x).year) if pd.notna(x) else None
                )
                events_with_years = events_with_years[events_with_years["event_year"].notna()]
                
                for _, event in events_with_years.iterrows():
                    try:
                        event_year = int(event["event_year"])
                        fig.add_vline(
                            x=event_year,
                            line_dash="dash",
                            line_color="gray",
                            annotation_text=str(event.get("category", "Event"))
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not add event line: {e}")
                        continue

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
        Plot usage trends over time with clear labels and annotations

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

        # Create a mapping for better indicator names
        indicator_names = {
            "ACC_MM_ACCOUNT": "Mobile Money Accounts",
            "USAGE_DIGITAL": "Digital Payment Usage",
            "USAGE_P2P": "P2P Transfers",
            "USAGE_TRANSACTIONS": "Transaction Volume"
        }

        # Color palette for different indicators
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for idx, indicator in enumerate(usage_trends["indicator_code"].unique()):
            indicator_data = usage_trends[usage_trends["indicator_code"] == indicator]
            display_name = indicator_names.get(indicator, indicator.replace("_", " ").title())
            
            fig.add_trace(go.Scatter(
                x=indicator_data["year"],
                y=indicator_data["value_numeric"],
                mode="lines+markers",
                name=display_name,
                line=dict(width=2.5),
                marker=dict(size=8),
                hovertemplate=f"<b>{display_name}</b><br>" +
                             "Year: %{x}<br>" +
                             "Value: %{y:.2f}%<br>" +
                             "<extra></extra>"
            ))

        # Add vertical lines for major events if available
        try:
            datasets = self.eda_analyzer.load_data()
            events = datasets.get("unified_data", pd.DataFrame())
            if not events.empty and "record_type" in events.columns:
                event_data = events[events["record_type"] == "event"].copy()
                if "event_date" in event_data.columns or "observation_date" in event_data.columns:
                    date_col = "event_date" if "event_date" in event_data.columns else "observation_date"
                    for _, event in event_data.iterrows():
                        event_date = pd.to_datetime(event[date_col], errors="coerce")
                        if pd.notna(event_date) and event_date.year >= usage_trends["year"].min():
                            event_year = event_date.year
                            event_name = event.get("description", event.get("category", "Event"))[:30]
                            fig.add_vline(
                                x=event_year,
                                line_dash="dash",
                                line_color="gray",
                                opacity=0.5,
                                annotation_text=event_name,
                                annotation_position="top"
                            )
        except Exception as e:
            self.logger.debug(f"Could not add event markers: {e}")

        fig.update_layout(
            title={
                "text": "Digital Payment Usage Trends (2014-2024)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16, "family": "Arial, sans-serif"}
            },
            xaxis_title={
                "text": "Year",
                "font": {"size": 14, "family": "Arial, sans-serif"}
            },
            yaxis_title={
                "text": "Percentage (%)",
                "font": {"size": 14, "family": "Arial, sans-serif"}
            },
            hovermode="x unified",
            template="plotly_white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font={"size": 12}
            ),
            height=500,
            margin=dict(l=80, r=20, t=80, b=60),
            xaxis=dict(
                title="Year",
                showgrid=True,
                gridcolor="lightgray",
                dtick=1 if usage_trends["year"].max() - usage_trends["year"].min() < 10 else 2,
                titlefont={"size": 14, "family": "Arial, sans-serif"},
                tickfont={"size": 12}
            ),
            yaxis=dict(
                title="Percentage (%)",
                showgrid=True,
                gridcolor="lightgray",
                ticksuffix="%",
                titlefont={"size": 14, "family": "Arial, sans-serif"},
                tickfont={"size": 12}
            )
        )

        if save_path:
            fig.write_html(str(save_path))
            self.logger.info(f"Figure saved to {save_path}")

        return fig
