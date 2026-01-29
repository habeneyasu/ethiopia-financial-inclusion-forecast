"""
Data enrichment module for adding new observations, events, and impact links
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from src.utils.logger import get_logger
from src.data.loader import DataLoader
from src.data.explorer import DataExplorer
from src.utils.config import config

logger = get_logger(__name__)


class DataEnricher:
    """Class for enriching the dataset with new observations, events, and impact links"""

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        data_explorer: Optional[DataExplorer] = None
    ):
        """
        Initialize DataEnricher

        Args:
            data_loader: DataLoader instance
            data_explorer: DataExplorer instance
        """
        self.data_loader = data_loader or DataLoader()
        self.data_explorer = data_explorer or DataExplorer(self.data_loader)
        self.logger = get_logger(__name__)
        self._enrichment_log: List[Dict[str, Any]] = []

    def add_observation(
        self,
        pillar: str,
        indicator: str,
        indicator_code: str,
        value_numeric: float,
        observation_date: str,
        source_name: str,
        source_url: str,
        confidence: str = "medium",
        record_type: str = "observation",
        collected_by: Optional[str] = None,
        original_text: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add a new observation record

        Args:
            pillar: Pillar name (e.g., "Access", "Usage")
            indicator: Indicator name
            indicator_code: Indicator code
            value_numeric: Numeric value
            observation_date: Date of observation (YYYY-MM-DD)
            source_name: Name of the source
            source_url: URL of the source
            confidence: Confidence level (high/medium/low)
            record_type: Record type (default: "observation")
            collected_by: Name of person who collected the data
            original_text: Original text from source
            notes: Additional notes
            **kwargs: Additional fields

        Returns:
            Dictionary representing the new observation
        """
        observation = {
            "record_type": record_type,
            "pillar": pillar,
            "indicator": indicator,
            "indicator_code": indicator_code,
            "value_numeric": value_numeric,
            "observation_date": observation_date,
            "source_name": source_name,
            "source_url": source_url,
            "confidence": confidence,
            "collected_by": collected_by or "system",
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "original_text": original_text,
            "notes": notes,
            **kwargs
        }

        self._enrichment_log.append({
            "type": "observation",
            "data": observation,
            "timestamp": datetime.now().isoformat()
        })

        self.logger.info(f"Added observation: {indicator_code} = {value_numeric} on {observation_date}")
        return observation

    def add_event(
        self,
        category: str,
        event_date: str,
        source_name: str,
        source_url: str,
        confidence: str = "medium",
        record_type: str = "event",
        description: Optional[str] = None,
        collected_by: Optional[str] = None,
        original_text: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add a new event record (pillar should be left empty)

        Args:
            category: Event category (e.g., "policy", "product_launch", "infrastructure")
            event_date: Date of event (YYYY-MM-DD)
            source_name: Name of the source
            source_url: URL of the source
            confidence: Confidence level (high/medium/low)
            record_type: Record type (default: "event")
            description: Event description
            collected_by: Name of person who collected the data
            original_text: Original text from source
            notes: Additional notes
            **kwargs: Additional fields

        Returns:
            Dictionary representing the new event
        """
        event = {
            "record_type": record_type,
            "category": category,
            "pillar": "",  # Events should have empty pillar
            "event_date": event_date,
            "source_name": source_name,
            "source_url": source_url,
            "confidence": confidence,
            "description": description,
            "collected_by": collected_by or "system",
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "original_text": original_text,
            "notes": notes,
            **kwargs
        }

        self._enrichment_log.append({
            "type": "event",
            "data": event,
            "timestamp": datetime.now().isoformat()
        })

        self.logger.info(f"Added event: {category} on {event_date}")
        return event

    def add_impact_link(
        self,
        parent_id: str,
        pillar: str,
        related_indicator: str,
        impact_direction: str,
        impact_magnitude: Optional[float] = None,
        lag_months: Optional[int] = None,
        evidence_basis: Optional[str] = None,
        confidence: str = "medium",
        collected_by: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add a new impact link connecting an event to an indicator

        Args:
            parent_id: ID of the parent event
            pillar: Pillar name
            related_indicator: Related indicator code
            impact_direction: Impact direction (e.g., "positive", "negative")
            impact_magnitude: Impact magnitude (optional)
            lag_months: Lag in months (optional)
            evidence_basis: Evidence basis (optional)
            confidence: Confidence level (high/medium/low)
            collected_by: Name of person who collected the data
            notes: Additional notes
            **kwargs: Additional fields

        Returns:
            Dictionary representing the new impact link
        """
        impact_link = {
            "parent_id": parent_id,
            "pillar": pillar,
            "related_indicator": related_indicator,
            "impact_direction": impact_direction,
            "impact_magnitude": impact_magnitude,
            "lag_months": lag_months,
            "evidence_basis": evidence_basis,
            "confidence": confidence,
            "collected_by": collected_by or "system",
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "notes": notes,
            **kwargs
        }

        self._enrichment_log.append({
            "type": "impact_link",
            "data": impact_link,
            "timestamp": datetime.now().isoformat()
        })

        self.logger.info(
            f"Added impact link: Event {parent_id} -> {related_indicator} ({impact_direction})"
        )
        return impact_link

    def merge_enrichments(
        self,
        output_path: Optional[Path] = None,
        save_format: str = "xlsx"
    ) -> Dict[str, pd.DataFrame]:
        """
        Merge new enrichments with existing data

        Args:
            output_path: Path to save enriched dataset
            save_format: Format to save ("xlsx" or "csv")

        Returns:
            Dictionary with enriched datasets
        """
        self.logger.info("Merging enrichments with existing data...")

        # Load existing data
        existing_data = self.data_loader.load_unified_data()
        if isinstance(existing_data, dict):
            main_data = existing_data.get("data", pd.DataFrame())
            impact_links = existing_data.get("impact_links", pd.DataFrame())
        else:
            main_data = existing_data
            impact_links = pd.DataFrame()

        # Separate enrichments by type
        observations = []
        events = []
        impact_links_new = []

        for entry in self._enrichment_log:
            if entry["type"] == "observation":
                observations.append(entry["data"])
            elif entry["type"] == "event":
                events.append(entry["data"])
            elif entry["type"] == "impact_link":
                impact_links_new.append(entry["data"])

        # Convert to DataFrames
        new_observations_df = pd.DataFrame(observations) if observations else pd.DataFrame()
        new_events_df = pd.DataFrame(events) if events else pd.DataFrame()
        new_impact_links_df = pd.DataFrame(impact_links_new) if impact_links_new else pd.DataFrame()

        # Merge with existing data
        if not main_data.empty and not new_observations_df.empty:
            # Ensure columns match
            all_cols = set(main_data.columns) | set(new_observations_df.columns)
            for col in all_cols:
                if col not in main_data.columns:
                    main_data[col] = None
                if col not in new_observations_df.columns:
                    new_observations_df[col] = None

            main_data = pd.concat([main_data, new_observations_df], ignore_index=True)

        if not main_data.empty and not new_events_df.empty:
            all_cols = set(main_data.columns) | set(new_events_df.columns)
            for col in all_cols:
                if col not in main_data.columns:
                    main_data[col] = None
                if col not in new_events_df.columns:
                    new_events_df[col] = None

            main_data = pd.concat([main_data, new_events_df], ignore_index=True)

        if not impact_links.empty and not new_impact_links_df.empty:
            all_cols = set(impact_links.columns) | set(new_impact_links_df.columns)
            for col in all_cols:
                if col not in impact_links.columns:
                    impact_links[col] = None
                if col not in new_impact_links_df.columns:
                    new_impact_links_df[col] = None

            impact_links = pd.concat([impact_links, new_impact_links_df], ignore_index=True)
        elif not new_impact_links_df.empty:
            impact_links = new_impact_links_df

        result = {"data": main_data}
        if not impact_links.empty:
            result["impact_links"] = impact_links

        # Save if path provided
        if output_path:
            if save_format == "xlsx":
                with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                    main_data.to_excel(writer, sheet_name="data", index=False)
                    if not impact_links.empty:
                        impact_links.to_excel(writer, sheet_name="impact_links", index=False)
            else:
                main_data.to_csv(output_path.with_suffix(".csv"), index=False)
                if not impact_links.empty:
                    impact_links.to_csv(
                        output_path.parent / f"{output_path.stem}_impact_links.csv",
                        index=False
                    )

            self.logger.info(f"Enriched dataset saved to {output_path}")

        return result

    def get_enrichment_log(self) -> List[Dict[str, Any]]:
        """Get the enrichment log"""
        return self._enrichment_log

    def clear_enrichment_log(self):
        """Clear the enrichment log"""
        self._enrichment_log.clear()
        self.logger.info("Enrichment log cleared")
