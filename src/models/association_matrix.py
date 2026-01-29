"""
Association Matrix Builder
Creates event-indicator association matrix
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from src.utils.logger import get_logger
from src.models.event_impact import EventImpactModeler

logger = get_logger(__name__)


class AssociationMatrixBuilder:
    """Build event-indicator association matrix"""

    def __init__(self, impact_modeler: Optional[EventImpactModeler] = None):
        """
        Initialize AssociationMatrixBuilder

        Args:
            impact_modeler: EventImpactModeler instance
        """
        self.impact_modeler = impact_modeler or EventImpactModeler()
        self.logger = get_logger(__name__)

    def build_association_matrix(
        self,
        indicators: Optional[List[str]] = None,
        events: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Build event-indicator association matrix

        Args:
            indicators: List of indicator codes (None for all)
            events: List of event IDs (None for all)

        Returns:
            DataFrame with events as rows, indicators as columns
        """
        self.logger.info("Building event-indicator association matrix...")

        # Load impact data
        impact_data = self.impact_modeler.load_impact_data()
        impact_links = impact_data["impact_links"]
        events_df = impact_data["events"]

        if impact_links.empty:
            self.logger.warning("No impact links found")
            return pd.DataFrame()

        # Get all unique events and indicators
        if events is None:
            events = impact_links["parent_id"].unique().tolist()
        if indicators is None:
            indicators = impact_links["related_indicator"].dropna().unique().tolist()

        # Initialize matrix
        matrix = pd.DataFrame(
            index=events,
            columns=indicators,
            dtype=float
        )

        # Fill matrix with impact values
        for _, link in impact_links.iterrows():
            event_id = link.get("parent_id")
            indicator = link.get("related_indicator")
            impact_magnitude = link.get("impact_magnitude")
            impact_direction = link.get("impact_direction", "increase")

            if event_id in matrix.index and indicator in matrix.columns:
                # Convert magnitude based on direction
                if pd.notna(impact_magnitude):
                    value = float(impact_magnitude)
                    if impact_direction == "decrease":
                        value = -value
                else:
                    # Use default magnitude if not specified
                    value = 0.1 if impact_direction == "increase" else -0.1

                # If multiple links for same event-indicator pair, take maximum
                if pd.isna(matrix.loc[event_id, indicator]):
                    matrix.loc[event_id, indicator] = value
                else:
                    # Combine effects (take larger absolute value)
                    if abs(value) > abs(matrix.loc[event_id, indicator]):
                        matrix.loc[event_id, indicator] = value

        # Fill NaN with 0 (no impact)
        matrix = matrix.fillna(0.0)

        return matrix

    def get_matrix_summary(self, matrix: pd.DataFrame) -> Dict:
        """
        Get summary statistics from association matrix

        Args:
            matrix: Association matrix DataFrame

        Returns:
            Dictionary with summary statistics
        """
        if matrix.empty:
            return {}

        summary = {
            "total_events": len(matrix.index),
            "total_indicators": len(matrix.columns),
            "total_impacts": (matrix != 0).sum().sum(),
            "positive_impacts": (matrix > 0).sum().sum(),
            "negative_impacts": (matrix < 0).sum().sum(),
            "events_with_impacts": (matrix != 0).any(axis=1).sum(),
            "indicators_with_impacts": (matrix != 0).any(axis=0).sum(),
            "max_positive_impact": matrix.max().max(),
            "max_negative_impact": matrix.min().min(),
            "average_impact_magnitude": matrix[matrix != 0].abs().mean().mean() if (matrix != 0).any().any() else 0.0
        }

        return summary

    def visualize_matrix(
        self,
        matrix: pd.DataFrame,
        save_path: Optional[Path] = None
    ):
        """
        Create heatmap visualization of association matrix

        Args:
            matrix: Association matrix DataFrame
            save_path: Optional path to save figure
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            plt.figure(figsize=(max(12, len(matrix.columns) * 0.8), max(8, len(matrix.index) * 0.5)))
            
            # Create heatmap
            sns.heatmap(
                matrix,
                annot=True,
                fmt=".2f",
                cmap="RdBu_r",
                center=0,
                square=False,
                linewidths=0.5,
                cbar_kws={"label": "Impact Magnitude"},
                xticklabels=True,
                yticklabels=True
            )

            plt.title("Event-Indicator Association Matrix", fontsize=14, fontweight="bold")
            plt.xlabel("Indicators", fontsize=12)
            plt.ylabel("Events", fontsize=12)
            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches="tight")
                self.logger.info(f"Matrix visualization saved to {save_path}")
            else:
                plt.show()

            plt.close()

        except ImportError:
            self.logger.warning("Matplotlib/Seaborn not available for visualization")
        except Exception as e:
            self.logger.error(f"Error creating visualization: {e}")
