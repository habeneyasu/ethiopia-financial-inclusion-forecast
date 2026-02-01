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
            "observation_date": event_date,  # Also include observation_date for compatibility
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
        # Handle observations
        if not new_observations_df.empty:
            if not main_data.empty:
                # Ensure columns match
                all_cols = set(main_data.columns) | set(new_observations_df.columns)
                for col in all_cols:
                    if col not in main_data.columns:
                        main_data[col] = None
                    if col not in new_observations_df.columns:
                        new_observations_df[col] = None
                main_data = pd.concat([main_data, new_observations_df], ignore_index=True)
            else:
                # If main_data is empty, use new observations as starting point
                main_data = new_observations_df.copy()

        # Handle events
        if not new_events_df.empty:
            if not main_data.empty:
                # Ensure columns match
                all_cols = set(main_data.columns) | set(new_events_df.columns)
                for col in all_cols:
                    if col not in main_data.columns:
                        main_data[col] = None
                    if col not in new_events_df.columns:
                        new_events_df[col] = None
                main_data = pd.concat([main_data, new_events_df], ignore_index=True)
            else:
                # If main_data is empty, use new events as starting point
                main_data = new_events_df.copy()

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

    def update_enrichment_log_markdown(
        self,
        log_path: Optional[Path] = None,
        append: bool = True
    ) -> str:
        """
        Update the data_enrichment_log.md file with all enrichments
        Appends new enrichments to existing log or creates new log if none exists

        Args:
            log_path: Path to enrichment log markdown file
            append: If True, append to existing log; if False, overwrite

        Returns:
            Path to updated log file
        """
        if log_path is None:
            log_path = config.project_root / "data_enrichment_log.md"

        self.logger.info(f"Updating enrichment log at {log_path}")

        # Count enrichments
        observations = [e for e in self._enrichment_log if e["type"] == "observation"]
        events = [e for e in self._enrichment_log if e["type"] == "event"]
        impact_links = [e for e in self._enrichment_log if e["type"] == "impact_link"]

        # Read existing log if it exists and we're appending
        existing_observations = []
        existing_events = []
        existing_impact_links = []
        existing_summary = {}
        
        if log_path.exists() and append:
            with open(log_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            # Try to parse existing enrichments (simple parsing)
            # This is a basic implementation - could be improved with proper markdown parsing
            if "## New Observations" in existing_content:
                # Count existing observations
                obs_count = existing_content.count("### Observation #")
                existing_summary["observations"] = obs_count
            if "## New Events" in existing_content:
                event_count = existing_content.count("### Event #")
                existing_summary["events"] = event_count
            if "## New Impact Links" in existing_content:
                link_count = existing_content.count("### Impact Link #")
                existing_summary["impact_links"] = link_count

        # Calculate total counts (existing + new)
        total_obs = existing_summary.get('observations', 0) + len(observations)
        total_events = existing_summary.get('events', 0) + len(events)
        total_links = existing_summary.get('impact_links', 0) + len(impact_links)
        total_enrichments = total_obs + total_events + total_links

        # Generate new content
        lines = [
            "# Data Enrichment Log",
            "",
            "This document tracks all additions and modifications made to the Ethiopia Financial Inclusion dataset.",
            "",
            "## Enrichment Summary",
            "",
            f"- **Total Enrichments**: {total_enrichments}",
            f"- **Observations Added**: {total_obs}",
            f"- **Events Added**: {total_events}",
            f"- **Impact Links Added**: {total_links}",
            f"- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]

        # Add observations - ensure ALL required fields are present
        if observations:
            lines.extend([
                "## New Observations",
                "",
            ])
            # Start numbering from existing count + 1
            start_idx = existing_summary.get('observations', 0) + 1
            for idx, entry in enumerate(observations, start_idx):
                data = entry["data"]
                # Verify all required fields are present
                required_fields = {
                    'indicator_code': data.get('indicator_code'),
                    'indicator': data.get('indicator'),
                    'pillar': data.get('pillar'),
                    'value_numeric': data.get('value_numeric'),
                    'observation_date': data.get('observation_date'),
                    'source_name': data.get('source_name'),
                    'source_url': data.get('source_url'),
                    'confidence': data.get('confidence'),
                    'collected_by': data.get('collected_by'),
                    'collection_date': data.get('collection_date'),
                    'original_text': data.get('original_text'),
                    'notes': data.get('notes')
                }
                
                # Check for missing required fields
                missing = [k for k, v in required_fields.items() if v is None or v == '']
                if missing:
                    self.logger.warning(f"Observation #{idx} missing fields: {missing}")
                
                lines.extend([
                    f"### Observation #{idx}",
                    "",
                    f"- **Indicator Code**: {required_fields['indicator_code'] or 'N/A'}",
                    f"- **Indicator**: {required_fields['indicator'] or 'N/A'}",
                    f"- **Pillar**: {required_fields['pillar'] or 'N/A'}",
                    f"- **Value**: {required_fields['value_numeric'] or 'N/A'}",
                    f"- **Date**: {required_fields['observation_date'] or 'N/A'}",
                    f"- **Source**: {required_fields['source_name'] or 'N/A'}",
                    f"- **Source URL**: {required_fields['source_url'] or 'N/A'}",
                    f"- **Confidence**: {required_fields['confidence'] or 'N/A'}",
                    f"- **Collected By**: {required_fields['collected_by'] or 'N/A'}",
                    f"- **Collection Date**: {required_fields['collection_date'] or 'N/A'}",
                    f"- **Original Text**: {required_fields['original_text'] or 'N/A'}",
                    f"- **Notes**: {required_fields['notes'] or 'N/A'}",
                    "",
                ])
        else:
            lines.extend([
                "## New Observations",
                "",
                "*No observations added yet.*",
                "",
            ])

        # Add events - ensure ALL required fields are present
        if events:
            lines.extend([
                "---",
                "",
                "## New Events",
                "",
            ])
            # Start numbering from existing count + 1
            start_idx = existing_summary.get('events', 0) + 1
            for idx, entry in enumerate(events, start_idx):
                data = entry["data"]
                # Verify all required fields are present
                required_fields = {
                    'category': data.get('category'),
                    'event_date': data.get('event_date') or data.get('observation_date'),
                    'description': data.get('description'),
                    'source_name': data.get('source_name'),
                    'source_url': data.get('source_url'),
                    'confidence': data.get('confidence'),
                    'collected_by': data.get('collected_by'),
                    'collection_date': data.get('collection_date'),
                    'original_text': data.get('original_text'),
                    'notes': data.get('notes')
                }
                
                # Check for missing required fields
                missing = [k for k, v in required_fields.items() if v is None or v == '']
                if missing:
                    self.logger.warning(f"Event #{idx} missing fields: {missing}")
                
                lines.extend([
                    f"### Event #{idx}",
                    "",
                    f"- **Category**: {required_fields['category'] or 'N/A'}",
                    f"- **Date**: {required_fields['event_date'] or 'N/A'}",
                    f"- **Description**: {required_fields['description'] or 'N/A'}",
                    f"- **Source**: {required_fields['source_name'] or 'N/A'}",
                    f"- **Source URL**: {required_fields['source_url'] or 'N/A'}",
                    f"- **Confidence**: {required_fields['confidence'] or 'N/A'}",
                    f"- **Collected By**: {required_fields['collected_by'] or 'N/A'}",
                    f"- **Collection Date**: {required_fields['collection_date'] or 'N/A'}",
                    f"- **Original Text**: {required_fields['original_text'] or 'N/A'}",
                    f"- **Notes**: {required_fields['notes'] or 'N/A'}",
                    "",
                ])
        else:
            lines.extend([
                "---",
                "",
                "## New Events",
                "",
                "*No events added yet.*",
                "",
            ])

        # Add impact links - ensure ALL required fields are present
        if impact_links:
            lines.extend([
                "---",
                "",
                "## New Impact Links",
                "",
            ])
            # Start numbering from existing count + 1
            start_idx = existing_summary.get('impact_links', 0) + 1
            for idx, entry in enumerate(impact_links, start_idx):
                data = entry["data"]
                # Verify all required fields are present
                required_fields = {
                    'parent_id': data.get('parent_id'),
                    'pillar': data.get('pillar'),
                    'related_indicator': data.get('related_indicator'),
                    'impact_direction': data.get('impact_direction'),
                    'impact_magnitude': data.get('impact_magnitude'),
                    'lag_months': data.get('lag_months'),
                    'evidence_basis': data.get('evidence_basis'),
                    'confidence': data.get('confidence'),
                    'collected_by': data.get('collected_by'),
                    'collection_date': data.get('collection_date'),
                    'notes': data.get('notes')
                }
                
                # Check for missing required fields
                missing = [k for k, v in required_fields.items() if v is None or v == '']
                if missing:
                    self.logger.warning(f"Impact Link #{idx} missing fields: {missing}")
                
                lines.extend([
                    f"### Impact Link #{idx}",
                    "",
                    f"- **Parent Event ID**: {required_fields['parent_id'] or 'N/A'}",
                    f"- **Pillar**: {required_fields['pillar'] or 'N/A'}",
                    f"- **Related Indicator**: {required_fields['related_indicator'] or 'N/A'}",
                    f"- **Impact Direction**: {required_fields['impact_direction'] or 'N/A'}",
                    f"- **Impact Magnitude**: {required_fields['impact_magnitude'] or 'N/A'}",
                    f"- **Lag Months**: {required_fields['lag_months'] or 'N/A'}",
                    f"- **Evidence Basis**: {required_fields['evidence_basis'] or 'N/A'}",
                    f"- **Confidence**: {required_fields['confidence'] or 'N/A'}",
                    f"- **Collected By**: {required_fields['collected_by'] or 'N/A'}",
                    f"- **Collection Date**: {required_fields['collection_date'] or 'N/A'}",
                    f"- **Notes**: {required_fields['notes'] or 'N/A'}",
                    "",
                ])
        else:
            lines.extend([
                "---",
                "",
                "## New Impact Links",
                "",
                "*No impact links added yet.*",
                "",
            ])

        # Add template sections if no enrichments
        if not self._enrichment_log:
            lines.extend([
                "---",
                "",
                "## Observation Template",
                "",
                "```markdown",
                "### Observation #[NUMBER]",
                "",
                "- **Indicator Code**: [CODE]",
                "- **Indicator**: [NAME]",
                "- **Pillar**: [Access/Usage]",
                "- **Value**: [NUMERIC_VALUE]",
                "- **Date**: [YYYY-MM-DD]",
                "- **Source**: [SOURCE_NAME]",
                "- **Source URL**: [URL]",
                "- **Confidence**: [high/medium/low]",
                "- **Collected By**: [NAME]",
                "- **Collection Date**: [YYYY-MM-DD]",
                "- **Original Text**: [QUOTE OR FIGURE FROM SOURCE]",
                "- **Notes**: [WHY THIS DATA IS USEFUL]",
                "```",
                "",
                "---",
                "",
                "## Event Template",
                "",
                "```markdown",
                "### Event #[NUMBER]",
                "",
                "- **Category**: [policy/product_launch/infrastructure/etc]",
                "- **Date**: [YYYY-MM-DD]",
                "- **Description**: [EVENT DESCRIPTION]",
                "- **Source**: [SOURCE_NAME]",
                "- **Source URL**: [URL]",
                "- **Confidence**: [high/medium/low]",
                "- **Collected By**: [NAME]",
                "- **Collection Date**: [YYYY-MM-DD]",
                "- **Original Text**: [QUOTE OR FIGURE FROM SOURCE]",
                "- **Notes**: [WHY THIS EVENT IS RELEVANT]",
                "```",
                "",
                "---",
                "",
                "## Impact Link Template",
                "",
                "```markdown",
                "### Impact Link #[NUMBER]",
                "",
                "- **Parent Event ID**: [EVENT_ID]",
                "- **Pillar**: [Access/Usage]",
                "- **Related Indicator**: [INDICATOR_CODE]",
                "- **Impact Direction**: [positive/negative]",
                "- **Impact Magnitude**: [VALUE IF AVAILABLE]",
                "- **Lag Months**: [NUMBER]",
                "- **Evidence Basis**: [DESCRIPTION]",
                "- **Confidence**: [high/medium/low]",
                "- **Collected By**: [NAME]",
                "- **Collection Date**: [YYYY-MM-DD]",
                "- **Notes**: [RELATIONSHIP RATIONALE]",
                "```",
                "",
            ])

        lines.extend([
            "---",
            "",
            "## Notes",
            "",
            "- All enrichments should follow the schema defined in the project documentation",
            "- Confidence levels: **high** (verified from authoritative source), **medium** (reliable but needs verification), **low** (preliminary or estimated)",
            "- Always include source URLs and original text for traceability",
            "- Document why each addition is useful for forecasting financial inclusion",
        ])

        # Write to file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        # Verify all enrichments were written
        self.logger.info(f"Enrichment log updated at {log_path}")
        self.logger.info(f"  - Wrote {len(observations)} observation(s) with full metadata")
        self.logger.info(f"  - Wrote {len(events)} event(s) with full metadata")
        self.logger.info(f"  - Wrote {len(impact_links)} impact link(s) with full metadata")
        self.logger.info(f"  - All enrichments include: source_url, original_text, confidence, collected_by, collection_date, notes")
        
        return str(log_path)
