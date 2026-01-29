"""
Exploratory Data Analysis module
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from src.utils.logger import get_logger
from src.data.loader import DataLoader
from src.data.explorer import DataExplorer

logger = get_logger(__name__)


class EDAAnalyzer:
    """Class for comprehensive exploratory data analysis"""

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        data_explorer: Optional[DataExplorer] = None
    ):
        """
        Initialize EDAAnalyzer

        Args:
            data_loader: DataLoader instance
            data_explorer: DataExplorer instance
        """
        self.data_loader = data_loader or DataLoader()
        self.data_explorer = data_explorer or DataExplorer(self.data_loader)
        self.logger = get_logger(__name__)
        self._datasets: Optional[Dict[str, pd.DataFrame]] = None

    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all datasets"""
        if self._datasets is None:
            self._datasets = self.data_explorer.load_all_data()
        return self._datasets

    def get_dataset_overview(self) -> Dict:
        """
        Summarize dataset by record_type, pillar, and source_type

        Returns:
            Dictionary with summary statistics
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        
        self.logger.info("Generating dataset overview...")

        overview = {
            "total_records": len(unified_data),
            "by_record_type": unified_data["record_type"].value_counts().to_dict() if "record_type" in unified_data.columns else {},
            "by_pillar": unified_data["pillar"].value_counts().to_dict() if "pillar" in unified_data.columns else {},
            "by_source_type": unified_data["source_type"].value_counts().to_dict() if "source_type" in unified_data.columns else {},
            "by_confidence": unified_data["confidence"].value_counts().to_dict() if "confidence" in unified_data.columns else {},
        }

        return overview

    def get_temporal_coverage(self) -> pd.DataFrame:
        """
        Create temporal coverage matrix: which years have data for which indicators

        Returns:
            DataFrame with indicators as rows and years as columns
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info("Analyzing temporal coverage...")

        # Filter observations only
        observations = unified_data[unified_data["record_type"] == "observation"].copy()

        if observations.empty or "indicator_code" not in observations.columns:
            return pd.DataFrame()

        # Extract year from observation_date
        date_col = "observation_date"
        if date_col in observations.columns:
            observations["year"] = pd.to_datetime(observations[date_col], errors="coerce").dt.year
        else:
            return pd.DataFrame()

        # Create coverage matrix
        coverage = observations.groupby(["indicator_code", "year"]).size().unstack(fill_value=0)
        coverage = (coverage > 0).astype(int)  # Binary: 1 if data exists, 0 if not

        return coverage

    def analyze_access_trajectory(self) -> pd.DataFrame:
        """
        Analyze Ethiopia's account ownership trajectory (2011-2024)

        Returns:
            DataFrame with account ownership data by year
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info("Analyzing Access trajectory...")

        # Filter for Access pillar observations
        access_data = unified_data[
            (unified_data["record_type"] == "observation") &
            (unified_data["pillar"] == "ACCESS") &
            (unified_data["indicator_code"] == "ACC_OWNERSHIP")
        ].copy()

        if access_data.empty:
            return pd.DataFrame()

        # Extract year and value
        date_col = "observation_date"
        if date_col in access_data.columns:
            access_data["year"] = pd.to_datetime(access_data[date_col], errors="coerce").dt.year
        else:
            return pd.DataFrame()

        # Get latest value per year
        trajectory = access_data.groupby("year")["value_numeric"].last().reset_index()
        trajectory = trajectory.sort_values("year")

        # Calculate growth rates
        trajectory["change_pp"] = trajectory["value_numeric"].diff()
        trajectory["change_pct"] = trajectory["value_numeric"].pct_change() * 100

        return trajectory

    def analyze_usage_trends(self) -> pd.DataFrame:
        """
        Analyze mobile money account penetration and digital payment trends

        Returns:
            DataFrame with usage indicators over time
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info("Analyzing Usage trends...")

        # Filter for Usage pillar observations
        usage_data = unified_data[
            (unified_data["record_type"] == "observation") &
            (unified_data["pillar"] == "USAGE")
        ].copy()

        if usage_data.empty:
            return pd.DataFrame()

        # Extract year
        date_col = "observation_date"
        if date_col in usage_data.columns:
            usage_data["year"] = pd.to_datetime(usage_data[date_col], errors="coerce").dt.year
        else:
            return pd.DataFrame()

        # Group by indicator and year
        usage_trends = usage_data.groupby(["indicator_code", "year"])["value_numeric"].last().reset_index()
        usage_trends = usage_trends.sort_values(["indicator_code", "year"])

        return usage_trends

    def analyze_gender_gap(self) -> pd.DataFrame:
        """
        Analyze gender gap in account ownership if data available

        Returns:
            DataFrame with gender-disaggregated data
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info("Analyzing gender gap...")

        # Filter for observations with gender data
        gender_data = unified_data[
            (unified_data["record_type"] == "observation") &
            (unified_data["gender"].notna()) &
            (unified_data["gender"] != "all")
        ].copy()

        if gender_data.empty:
            return pd.DataFrame()

        # Extract year
        date_col = "observation_date"
        if date_col in gender_data.columns:
            gender_data["year"] = pd.to_datetime(gender_data[date_col], errors="coerce").dt.year
        else:
            return pd.DataFrame()

        # Analyze by gender
        gender_analysis = gender_data.groupby(["indicator_code", "gender", "year"])["value_numeric"].last().reset_index()
        
        # Calculate gap if both male and female data available
        if "male" in gender_data["gender"].values and "female" in gender_data["gender"].values:
            pivot = gender_analysis.pivot_table(
                index=["indicator_code", "year"],
                columns="gender",
                values="value_numeric"
            ).reset_index()
            
            if "male" in pivot.columns and "female" in pivot.columns:
                pivot["gender_gap_pp"] = pivot["male"] - pivot["female"]
                return pivot

        return gender_analysis

    def analyze_infrastructure(self) -> pd.DataFrame:
        """
        Analyze infrastructure data (4G coverage, mobile penetration, ATM density)

        Returns:
            DataFrame with infrastructure indicators
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info("Analyzing infrastructure data...")

        # Filter for infrastructure-related indicators
        infra_keywords = ["4G", "mobile", "ATM", "coverage", "penetration", "density", "agent"]
        
        infra_data = unified_data[
            (unified_data["record_type"] == "observation") &
            (unified_data["indicator"].str.contains("|".join(infra_keywords), case=False, na=False) |
             unified_data["indicator_code"].str.contains("|".join(infra_keywords), case=False, na=False))
        ].copy()

        if infra_data.empty:
            return pd.DataFrame()

        # Extract year
        date_col = "observation_date"
        if date_col in infra_data.columns:
            infra_data["year"] = pd.to_datetime(infra_data[date_col], errors="coerce").dt.year
        else:
            return pd.DataFrame()

        infrastructure = infra_data.groupby(["indicator_code", "year"])["value_numeric"].last().reset_index()
        infrastructure = infrastructure.sort_values(["indicator_code", "year"])

        return infrastructure

    def get_event_timeline(self) -> pd.DataFrame:
        """
        Get timeline of all cataloged events

        Returns:
            DataFrame with events sorted by date
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info("Extracting event timeline...")

        events = unified_data[unified_data["record_type"] == "event"].copy()

        if events.empty:
            return pd.DataFrame()

        # Extract date
        date_col = "observation_date" if "observation_date" in events.columns else "event_date"
        if date_col in events.columns:
            events["event_date"] = pd.to_datetime(events[date_col], errors="coerce")
            events = events.sort_values("event_date")
        else:
            return pd.DataFrame()

        return events[["event_date", "category", "source_name", "record_id", "description"]].copy()

    def analyze_correlations(self, indicators: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Examine correlations between different indicators

        Args:
            indicators: List of indicator codes to analyze (None for all)

        Returns:
            Correlation matrix
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info("Analyzing correlations...")

        # Filter observations
        observations = unified_data[unified_data["record_type"] == "observation"].copy()

        if observations.empty:
            return pd.DataFrame()

        # Extract year
        date_col = "observation_date"
        if date_col in observations.columns:
            observations["year"] = pd.to_datetime(observations[date_col], errors="coerce").dt.year
        else:
            return pd.DataFrame()

        # Pivot to get indicators as columns, years as rows
        if indicators:
            observations = observations[observations["indicator_code"].isin(indicators)]

        pivot = observations.pivot_table(
            index="year",
            columns="indicator_code",
            values="value_numeric",
            aggfunc="last"
        )

        # Calculate correlation
        correlation = pivot.corr()

        return correlation

    def identify_data_gaps(self) -> Dict:
        """
        Identify gaps: which indicators have sparse coverage

        Returns:
            Dictionary with gap analysis
        """
        if self._datasets is None:
            self.load_data()

        unified_data = self._datasets["unified_data"]
        self.logger.info("Identifying data gaps...")

        observations = unified_data[unified_data["record_type"] == "observation"].copy()

        if observations.empty:
            return {}

        # Count observations per indicator
        indicator_counts = observations["indicator_code"].value_counts()

        # Identify sparse indicators (fewer than 3 observations)
        sparse_indicators = indicator_counts[indicator_counts < 3].to_dict()

        # Temporal gaps
        temporal_coverage = self.get_temporal_coverage()
        temporal_gaps = {}
        if not temporal_coverage.empty:
            for indicator in temporal_coverage.index:
                years_with_data = temporal_coverage.loc[indicator].sum()
                if years_with_data < 3:
                    temporal_gaps[indicator] = years_with_data

        gaps = {
            "sparse_indicators": sparse_indicators,
            "temporal_gaps": temporal_gaps,
            "total_indicators": len(indicator_counts),
            "indicators_with_adequate_data": len(indicator_counts[indicator_counts >= 3])
        }

        return gaps

    def generate_insights_summary(self, output_path: Optional[Path] = None) -> str:
        """
        Generate comprehensive insights summary

        Args:
            output_path: Optional path to save summary

        Returns:
            Summary as string
        """
        self.logger.info("Generating insights summary...")

        overview = self.get_dataset_overview()
        access_traj = self.analyze_access_trajectory()
        gaps = self.identify_data_gaps()

        summary_lines = [
            "=" * 80,
            "EXPLORATORY DATA ANALYSIS - KEY INSIGHTS",
            "=" * 80,
            "",
            "DATASET OVERVIEW",
            "-" * 80,
            f"Total records: {overview.get('total_records', 0)}",
            f"By record type: {overview.get('by_record_type', {})}",
            f"By pillar: {overview.get('by_pillar', {})}",
            f"By source type: {overview.get('by_source_type', {})}",
            "",
            "ACCESS TRAJECTORY",
            "-" * 80,
        ]

        if not access_traj.empty:
            summary_lines.append(access_traj.to_string())
            summary_lines.append("")
            summary_lines.append(f"Growth 2011-2024: {access_traj['value_numeric'].iloc[-1] - access_traj['value_numeric'].iloc[0]:.1f}pp")
            summary_lines.append(f"Growth 2021-2024: {access_traj[access_traj['year'] >= 2021]['change_pp'].sum():.1f}pp")
        else:
            summary_lines.append("No access trajectory data available")

        summary_lines.extend([
            "",
            "DATA GAPS",
            "-" * 80,
            f"Sparse indicators (<3 observations): {len(gaps.get('sparse_indicators', {}))}",
            f"Indicators with adequate data: {gaps.get('indicators_with_adequate_data', 0)}",
            "",
            "=" * 80
        ])

        summary = "\n".join(summary_lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)
            self.logger.info(f"Insights summary saved to {output_path}")

        return summary
