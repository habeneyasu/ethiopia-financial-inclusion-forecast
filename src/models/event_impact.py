"""
Event Impact Modeling Module
Models how events affect financial inclusion indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from src.utils.logger import get_logger
from src.data.loader import DataLoader
from src.data.explorer import DataExplorer

logger = get_logger(__name__)


class EventImpactModeler:
    """Class for modeling event impacts on financial inclusion indicators"""

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        data_explorer: Optional[DataExplorer] = None
    ):
        """
        Initialize EventImpactModeler

        Args:
            data_loader: DataLoader instance
            data_explorer: DataExplorer instance
        """
        self.data_loader = data_loader or DataLoader()
        self.data_explorer = data_explorer or DataExplorer(self.data_loader)
        self.logger = get_logger(__name__)
        self._datasets: Optional[Dict[str, pd.DataFrame]] = None
        self._impact_links: Optional[pd.DataFrame] = None
        self._events: Optional[pd.DataFrame] = None

    def load_impact_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load impact_links sheet and join with events using parent_id

        Returns:
            Dictionary with impact_links, events, and joined data
        """
        self.logger.info("Loading impact data...")

        if self._datasets is None:
            self._datasets = self.data_explorer.load_all_data()

        unified_data = self._datasets["unified_data"]
        impact_links = self._datasets.get("impact_links", pd.DataFrame())

        # Get events from unified data
        events = unified_data[unified_data["record_type"] == "event"].copy()

        # If impact_links is empty, try to get from unified_data
        if impact_links.empty:
            # Check if impact links are in unified_data with parent_id
            impact_links = unified_data[
                unified_data["parent_id"].notna() & 
                (unified_data["parent_id"] != "")
            ].copy()

        self._impact_links = impact_links
        self._events = events

        # Join impact_links with events
        if not impact_links.empty and not events.empty and "parent_id" in impact_links.columns:
            # Join on parent_id = record_id
            joined_data = impact_links.merge(
                events[["record_id", "category", "observation_date", "source_name", "description"]],
                left_on="parent_id",
                right_on="record_id",
                how="left",
                suffixes=("_impact", "_event")
            )
        else:
            joined_data = pd.DataFrame()

        result = {
            "impact_links": impact_links,
            "events": events,
            "joined_data": joined_data
        }

        self.logger.info(f"Loaded {len(impact_links)} impact links and {len(events)} events")
        return result

    def get_impact_summary(self) -> pd.DataFrame:
        """
        Create summary showing: which events affect which indicators, and by how much

        Returns:
            DataFrame with impact summary
        """
        if self._impact_links is None or self._events is None:
            self.load_impact_data()

        if self._impact_links.empty:
            return pd.DataFrame()

        self.logger.info("Creating impact summary...")

        # Get joined data
        impact_data = self.load_impact_data()
        joined = impact_data["joined_data"]

        if joined.empty:
            # Fallback: use impact_links directly
            summary = self._impact_links.groupby(["parent_id", "related_indicator"]).agg({
                "impact_direction": "first",
                "impact_magnitude": "first",
                "lag_months": "first",
                "pillar": "first"
            }).reset_index()
        else:
            summary = joined.groupby([
                "parent_id", "related_indicator", "category"
            ]).agg({
                "impact_direction": "first",
                "impact_magnitude": "first",
                "lag_months": "first",
                "pillar": "first",
                "observation_date_event": "first"
            }).reset_index()

        return summary

    def represent_event_effect_over_time(
        self,
        event_date: pd.Timestamp,
        impact_magnitude: float,
        lag_months: int = 0,
        effect_type: str = "immediate"
    ) -> pd.Series:
        """
        Represent an event's effect over time

        Args:
            event_date: Date of the event
            impact_magnitude: Magnitude of impact
            lag_months: Lag in months before effect starts
            effect_type: Type of effect ("immediate", "gradual", "distributed")

        Returns:
            Series with effect values over time
        """
        # Generate time series from event date
        months_after = pd.date_range(
            start=event_date,
            periods=36,  # 3 years
            freq="M"
        )

        if effect_type == "immediate":
            # Effect happens immediately after lag
            effect = np.where(
                (months_after - event_date).days >= (lag_months * 30),
                impact_magnitude,
                0.0
            )
        elif effect_type == "gradual":
            # Effect builds gradually over 12 months
            months_since_lag = ((months_after - event_date).days / 30) - lag_months
            effect = np.where(
                months_since_lag >= 0,
                impact_magnitude * np.minimum(months_since_lag / 12, 1.0),
                0.0
            )
        elif effect_type == "distributed":
            # Distributed lag effect (decay over time)
            months_since_lag = ((months_after - event_date).days / 30) - lag_months
            decay_rate = 0.95  # 5% decay per month
            effect = np.where(
                months_since_lag >= 0,
                impact_magnitude * (decay_rate ** months_since_lag),
                0.0
            )
        else:
            effect = np.zeros(len(months_after))

        return pd.Series(effect, index=months_after)

    def combine_multiple_event_effects(
        self,
        event_effects: List[pd.Series],
        combination_method: str = "additive"
    ) -> pd.Series:
        """
        Combine effects from multiple events

        Args:
            event_effects: List of effect series from different events
            combination_method: How to combine ("additive", "multiplicative", "max")

        Returns:
            Combined effect series
        """
        if not event_effects:
            return pd.Series(dtype=float)

        # Align all series to same index
        all_indices = set()
        for effect in event_effects:
            all_indices.update(effect.index)

        combined_index = sorted(all_indices)
        combined = pd.Series(0.0, index=combined_index)

        for effect in event_effects:
            # Reindex to combined index, filling missing with 0
            effect_aligned = effect.reindex(combined_index, fill_value=0.0)

            if combination_method == "additive":
                combined += effect_aligned
            elif combination_method == "multiplicative":
                combined = combined * (1 + effect_aligned)
            elif combination_method == "max":
                combined = pd.concat([combined, effect_aligned], axis=1).max(axis=1)
            else:
                combined += effect_aligned  # Default to additive

        return combined

    def validate_against_historical_data(
        self,
        indicator_code: str,
        event_id: str,
        observed_change: float,
        observed_period: Tuple[str, str]
    ) -> Dict:
        """
        Test model against historical data

        Args:
            indicator_code: Indicator to validate
            event_id: Event ID to test
            observed_change: Observed change in indicator
            observed_period: (start_date, end_date) tuple

        Returns:
            Dictionary with validation results
        """
        self.logger.info(f"Validating {event_id} impact on {indicator_code}...")

        if self._impact_links is None:
            self.load_impact_data()

        # Get impact link for this event and indicator
        impact_link = self._impact_links[
            (self._impact_links["parent_id"] == event_id) &
            (self._impact_links["related_indicator"] == indicator_code)
        ]

        if impact_link.empty:
            return {
                "validated": False,
                "reason": "No impact link found"
            }

        # Get event details
        event = self._events[self._events["record_id"] == event_id]
        if event.empty:
            return {
                "validated": False,
                "reason": "Event not found"
            }

        event_date = pd.to_datetime(event["observation_date"].iloc[0])
        impact_magnitude = impact_link["impact_magnitude"].iloc[0] if pd.notna(impact_link["impact_magnitude"].iloc[0]) else None
        lag_months = impact_link["lag_months"].iloc[0] if pd.notna(impact_link["lag_months"].iloc[0]) else 0

        # Calculate predicted effect
        start_date = pd.to_datetime(observed_period[0])
        end_date = pd.to_datetime(observed_period[1])

        if impact_magnitude is None:
            return {
                "validated": False,
                "reason": "Impact magnitude not specified"
            }

        # Model the effect
        effect_series = self.represent_event_effect_over_time(
            event_date=event_date,
            impact_magnitude=impact_magnitude,
            lag_months=int(lag_months) if pd.notna(lag_months) else 0,
            effect_type="gradual"
        )

        # Get effect at end of period
        effect_at_end = effect_series.reindex([end_date], method="ffill").iloc[0] if end_date in effect_series.index else effect_series.iloc[-1]

        # Compare with observed
        difference = abs(observed_change - effect_at_end)
        relative_error = (difference / abs(observed_change) * 100) if observed_change != 0 else None

        validation_result = {
            "validated": True,
            "event_id": event_id,
            "indicator_code": indicator_code,
            "event_date": event_date.strftime("%Y-%m-%d"),
            "predicted_impact": float(effect_at_end),
            "observed_change": observed_change,
            "difference": float(difference),
            "relative_error_pct": float(relative_error) if relative_error else None,
            "lag_months": int(lag_months) if pd.notna(lag_months) else 0,
            "impact_magnitude": float(impact_magnitude) if pd.notna(impact_magnitude) else None
        }

        return validation_result
