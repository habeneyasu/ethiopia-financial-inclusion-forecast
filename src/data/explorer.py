"""
Data exploration module with comprehensive analysis capabilities
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from src.utils.logger import get_logger
from src.data.loader import DataLoader

logger = get_logger(__name__)


class DataExplorer:
    """Class for exploring and analyzing the financial inclusion dataset"""

    def __init__(self, data_loader: Optional[DataLoader] = None):
        """
        Initialize DataExplorer

        Args:
            data_loader: DataLoader instance (creates new one if None)
        """
        self.data_loader = data_loader or DataLoader()
        self.logger = get_logger(__name__)
        self._unified_data: Optional[pd.DataFrame] = None
        self._impact_links: Optional[pd.DataFrame] = None
        self._reference_codes: Optional[pd.DataFrame] = None

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all datasets

        Returns:
            Dictionary containing all loaded datasets
        """
        self.logger.info("Loading all datasets...")

        # Load unified data (may have multiple sheets)
        unified_data = self.data_loader.load_unified_data()
        if isinstance(unified_data, dict):
            # Try common sheet names
            if "data" in unified_data:
                self._unified_data = unified_data["data"]
            elif "ethiopia_fi_unified_data" in unified_data:
                self._unified_data = unified_data["ethiopia_fi_unified_data"]
            elif len(unified_data) > 0:
                self._unified_data = unified_data[list(unified_data.keys())[0]]
            else:
                self._unified_data = pd.DataFrame()
            
            # Try common impact link sheet names
            if "impact_links" in unified_data:
                self._impact_links = unified_data["impact_links"]
            elif "Impact_sheet" in unified_data:
                self._impact_links = unified_data["Impact_sheet"]
            elif "impact_sheet" in unified_data:
                self._impact_links = unified_data["impact_sheet"]
            else:
                self._impact_links = pd.DataFrame()
        else:
            self._unified_data = unified_data
            self._impact_links = pd.DataFrame()

        # Load reference codes
        ref_codes = self.data_loader.load_reference_codes()
        if isinstance(ref_codes, dict):
            if "reference_codes" in ref_codes:
                self._reference_codes = ref_codes["reference_codes"]
            elif len(ref_codes) > 0:
                self._reference_codes = ref_codes[list(ref_codes.keys())[0]]
            else:
                self._reference_codes = pd.DataFrame()
        else:
            self._reference_codes = ref_codes

        result = {
            "unified_data": self._unified_data,
            "reference_codes": self._reference_codes
        }

        if self._impact_links is not None and not self._impact_links.empty:
            result["impact_links"] = self._impact_links

        self.logger.info("All datasets loaded successfully")
        return result

    def get_record_counts(self) -> Dict[str, pd.Series]:
        """
        Count records by record_type, pillar, source_type, and confidence

        Returns:
            Dictionary with counts for each category
        """
        if self._unified_data is None:
            self.load_all_data()

        self.logger.info("Calculating record counts...")

        counts = {}
        if "record_type" in self._unified_data.columns:
            counts["record_type"] = self._unified_data["record_type"].value_counts()

        if "pillar" in self._unified_data.columns:
            counts["pillar"] = self._unified_data["pillar"].value_counts()

        if "source_type" in self._unified_data.columns:
            counts["source_type"] = self._unified_data["source_type"].value_counts()
        elif "source_name" in self._unified_data.columns:
            # Fallback to source_name if source_type not available
            counts["source_name"] = self._unified_data["source_name"].value_counts()

        if "confidence" in self._unified_data.columns:
            counts["confidence"] = self._unified_data["confidence"].value_counts()

        return counts

    def get_profiling_report(self) -> Dict[str, pd.DataFrame]:
        """
        Generate comprehensive profiling report with cross-tabulations

        Returns:
            Dictionary with profiling DataFrames
        """
        if self._unified_data is None or self._unified_data.empty:
            self.load_all_data()

        if self._unified_data.empty:
            return {}

        self.logger.info("Generating profiling report...")

        profiling = {}

        # Cross-tabulation: record_type x pillar
        if "record_type" in self._unified_data.columns and "pillar" in self._unified_data.columns:
            profiling["record_type_pillar"] = pd.crosstab(
                self._unified_data["record_type"],
                self._unified_data["pillar"],
                margins=True
            )

        # Cross-tabulation: record_type x confidence
        if "record_type" in self._unified_data.columns and "confidence" in self._unified_data.columns:
            profiling["record_type_confidence"] = pd.crosstab(
                self._unified_data["record_type"],
                self._unified_data["confidence"],
                margins=True
            )

        # Cross-tabulation: pillar x confidence
        if "pillar" in self._unified_data.columns and "confidence" in self._unified_data.columns:
            profiling["pillar_confidence"] = pd.crosstab(
                self._unified_data["pillar"],
                self._unified_data["confidence"],
                margins=True
            )

        # Cross-tabulation: record_type x source_type (if available)
        if "record_type" in self._unified_data.columns:
            if "source_type" in self._unified_data.columns:
                profiling["record_type_source_type"] = pd.crosstab(
                    self._unified_data["record_type"],
                    self._unified_data["source_type"],
                    margins=True
                )
            elif "source_name" in self._unified_data.columns:
                # Top 10 sources by record type
                source_counts = self._unified_data.groupby(["record_type", "source_name"]).size().reset_index(name="count")
                top_sources = source_counts.nlargest(10, "count")
                profiling["record_type_top_sources"] = top_sources

        return profiling

    def get_temporal_range(self) -> Dict[str, Optional[str]]:
        """
        Identify the temporal range of observations

        Returns:
            Dictionary with min_date, max_date, and date_range
        """
        if self._unified_data is None or self._unified_data.empty:
            self.load_all_data()

        if self._unified_data.empty:
            return {"min_date": None, "max_date": None, "date_range": None}

        self.logger.info("Analyzing temporal range...")

        date_columns = [
            col for col in self._unified_data.columns
            if "date" in col.lower() or "year" in col.lower()
        ]

        if not date_columns:
            return {"min_date": None, "max_date": None, "date_range": None}

        # Try to find observation_date or similar
        date_col = None
        for col in ["observation_date", "event_date", "date", "period_start", "period_end"]:
            if col in self._unified_data.columns:
                date_col = col
                break

        if date_col is None and date_columns:
            date_col = date_columns[0]

        if date_col:
            dates = pd.to_datetime(
                self._unified_data[date_col], errors="coerce"
            ).dropna()

            if len(dates) > 0:
                min_date = dates.min().strftime("%Y-%m-%d")
                max_date = dates.max().strftime("%Y-%m-%d")
                date_range = f"{min_date} to {max_date}"

                return {
                    "min_date": min_date,
                    "max_date": max_date,
                    "date_range": date_range,
                    "date_column": date_col
                }

        return {"min_date": None, "max_date": None, "date_range": None}

    def get_unique_indicators(self) -> pd.DataFrame:
        """
        List all unique indicators and their coverage

        Returns:
            DataFrame with indicator information
        """
        if self._unified_data is None:
            self.load_all_data()

        self.logger.info("Extracting unique indicators...")

        if "indicator_code" not in self._unified_data.columns:
            self.logger.warning("indicator_code column not found")
            return pd.DataFrame()

        indicator_cols = [
            col for col in ["indicator_code", "indicator", "pillar"]
            if col in self._unified_data.columns
        ]

        indicators = self._unified_data[indicator_cols].drop_duplicates()

        # Add coverage count
        if "indicator_code" in indicators.columns:
            coverage = self._unified_data.groupby("indicator_code").size().reset_index(
                name="record_count"
            )
            indicators = indicators.merge(coverage, on="indicator_code", how="left")

        return indicators.sort_values("indicator_code" if "indicator_code" in indicators.columns else indicators.columns[0])

    def get_events_catalog(self) -> pd.DataFrame:
        """
        Understand which events are cataloged and their dates

        Returns:
            DataFrame with event information
        """
        if self._unified_data is None or self._unified_data.empty:
            self.load_all_data()

        if self._unified_data.empty:
            return pd.DataFrame()

        self.logger.info("Extracting events catalog...")

        if "record_type" not in self._unified_data.columns:
            self.logger.warning("record_type column not found")
            return pd.DataFrame()

        event_data = self._unified_data[
            self._unified_data["record_type"] == "event"
        ].copy()

        if event_data.empty:
            self.logger.warning("No events found in dataset")
            return pd.DataFrame()

        event_cols = [
            col for col in [
                "event_date", "observation_date", "category", "pillar", "source_name",
                "confidence", "description", "record_id"
            ]
            if col in event_data.columns
        ]

        sort_col = "event_date" if "event_date" in event_data.columns else (
            "observation_date" if "observation_date" in event_data.columns else event_cols[0]
        )

        return event_data[event_cols].sort_values(sort_col)

    def get_impact_links_summary(self) -> Dict:
        """
        Review existing impact_links and relationships

        Returns:
            Dictionary with impact links summary
        """
        if self._impact_links is None:
            # Try to load if not already loaded
            unified_data = self.data_loader.load_unified_data()
            if isinstance(unified_data, dict):
                self._impact_links = unified_data.get("impact_links", pd.DataFrame())
            else:
                self.logger.warning("Impact links not found in dataset")
                return {}

        if self._impact_links.empty:
            return {}

        self.logger.info("Analyzing impact links...")

        summary = {
            "total_links": len(self._impact_links),
            "columns": list(self._impact_links.columns),
            "unique_events": self._impact_links.get("parent_id", pd.Series()).nunique() if "parent_id" in self._impact_links.columns else 0,
            "unique_indicators": self._impact_links.get("related_indicator", pd.Series()).nunique() if "related_indicator" in self._impact_links.columns else 0,
        }

        if "pillar" in self._impact_links.columns:
            summary["by_pillar"] = self._impact_links["pillar"].value_counts().to_dict()

        if "impact_direction" in self._impact_links.columns:
            summary["by_direction"] = self._impact_links["impact_direction"].value_counts().to_dict()

        return summary

    def generate_exploration_report(self, output_path: Optional[Path] = None) -> str:
        """
        Generate a comprehensive exploration report

        Args:
            output_path: Optional path to save report

        Returns:
            Report as string
        """
        if self._unified_data is None:
            self.load_all_data()

        self.logger.info("Generating exploration report...")

        report_lines = [
            "=" * 80,
            "DATA EXPLORATION REPORT",
            "=" * 80,
            "",
        ]

        # Basic info
        report_lines.extend([
            "DATASET OVERVIEW",
            "-" * 80,
            f"Total records: {len(self._unified_data)}",
            f"Total columns: {len(self._unified_data.columns)}",
            f"Columns: {', '.join(self._unified_data.columns)}",
            "",
        ])

        # Record counts
        counts = self.get_record_counts()
        report_lines.append("RECORD COUNTS")
        report_lines.append("-" * 80)
        for category, count_series in counts.items():
            report_lines.append(f"\n{category.upper()}:")
            report_lines.append(str(count_series))
        report_lines.append("")

        # Temporal range
        temporal = self.get_temporal_range()
        report_lines.append("TEMPORAL RANGE")
        report_lines.append("-" * 80)
        report_lines.append(f"Date range: {temporal.get('date_range', 'N/A')}")
        report_lines.append(f"Min date: {temporal.get('min_date', 'N/A')}")
        report_lines.append(f"Max date: {temporal.get('max_date', 'N/A')}")
        report_lines.append("")

        # Indicators
        indicators = self.get_unique_indicators()
        report_lines.append("UNIQUE INDICATORS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total unique indicators: {len(indicators)}")
        if not indicators.empty:
            report_lines.append("\nFirst 10 indicators:")
            report_lines.append(str(indicators.head(10)))
        report_lines.append("")

        # Events
        events = self.get_events_catalog()
        report_lines.append("EVENTS CATALOG")
        report_lines.append("-" * 80)
        report_lines.append(f"Total events: {len(events)}")
        if not events.empty:
            report_lines.append("\nFirst 10 events:")
            report_lines.append(str(events.head(10)))
        report_lines.append("")

        # Impact links
        impact_summary = self.get_impact_links_summary()
        if impact_summary:
            report_lines.append("IMPACT LINKS SUMMARY")
            report_lines.append("-" * 80)
            for key, value in impact_summary.items():
                report_lines.append(f"{key}: {value}")
        report_lines.append("")

        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            self.logger.info(f"Report saved to {output_path}")

        return report
