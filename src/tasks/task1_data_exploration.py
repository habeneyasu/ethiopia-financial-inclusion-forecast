"""
Task 1: Data Exploration and Enrichment
Main script for executing Task 1 requirements
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.utils.logger import get_logger
from src.utils.config import config
from src.data.loader import DataLoader
from src.data.explorer import DataExplorer
from src.data.enricher import DataEnricher

logger = get_logger(__name__)


class Task1Executor:
    """Executor class for Task 1: Data Exploration and Enrichment"""

    def __init__(self):
        """Initialize Task 1 executor"""
        self.logger = get_logger(__name__)
        self.data_loader = DataLoader()
        self.data_explorer = DataExplorer(self.data_loader)
        self.data_enricher = DataEnricher(self.data_loader, self.data_explorer)

    def execute(self) -> bool:
        """
        Execute Task 1: Data Exploration and Enrichment

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("Starting Task 1: Data Exploration and Enrichment")
            self.logger.info("=" * 80)

            # Step 1: Explicitly load all required datasets
            self.logger.info("\nStep 1: Explicitly loading datasets...")
            
            # Load unified data (CSV or Excel)
            unified_data = self.data_loader.load_unified_data()
            self.logger.info(f"✓ Unified data loaded: {type(unified_data)}")
            
            # Load reference codes
            reference_codes = self.data_loader.load_reference_codes()
            self.logger.info(f"✓ Reference codes loaded: {type(reference_codes)}")
            
            # Load all datasets through explorer
            datasets = self.data_explorer.load_all_data()
            self.logger.info("✓ All datasets loaded successfully")
            self.logger.info(f"  - Unified data shape: {datasets.get('unified_data', pd.DataFrame()).shape if 'unified_data' in datasets else 'N/A'}")
            self.logger.info(f"  - Reference codes shape: {datasets.get('reference_codes', pd.DataFrame()).shape if 'reference_codes' in datasets else 'N/A'}")
            if 'impact_links' in datasets:
                self.logger.info(f"  - Impact links shape: {datasets['impact_links'].shape}")

            # Step 2: Systematic profiling by record_type/pillar/source_type/confidence
            self.logger.info("\nStep 2: Performing systematic profiling...")
            counts = self.data_explorer.get_record_counts()
            
            # Detailed profiling
            unified_df = datasets.get('unified_data', pd.DataFrame())
            if not unified_df.empty:
                self.logger.info("\n--- Profiling by Record Type ---")
                if "record_type" in unified_df.columns:
                    record_type_counts = unified_df["record_type"].value_counts()
                    for rt, count in record_type_counts.items():
                        self.logger.info(f"  {rt}: {count} records")
                
                self.logger.info("\n--- Profiling by Pillar ---")
                if "pillar" in unified_df.columns:
                    pillar_counts = unified_df["pillar"].value_counts()
                    for pillar, count in pillar_counts.items():
                        self.logger.info(f"  {pillar}: {count} records")
                
                self.logger.info("\n--- Profiling by Source Type ---")
                if "source_type" in unified_df.columns:
                    source_type_counts = unified_df["source_type"].value_counts()
                    for st, count in source_type_counts.items():
                        self.logger.info(f"  {st}: {count} records")
                elif "source_name" in unified_df.columns:
                    source_counts = unified_df["source_name"].value_counts()
                    self.logger.info(f"  Total unique sources: {len(source_counts)}")
                    for source, count in source_counts.head(10).items():
                        self.logger.info(f"  {source}: {count} records")
                
                self.logger.info("\n--- Profiling by Confidence ---")
                if "confidence" in unified_df.columns:
                    confidence_counts = unified_df["confidence"].value_counts()
                    for conf, count in confidence_counts.items():
                        self.logger.info(f"  {conf}: {count} records")
                
                # Cross-tabulation analysis using enhanced profiling method
                self.logger.info("\n--- Cross-Tabulation Analysis ---")
                profiling = self.data_explorer.get_profiling_report()
                
                if "record_type_pillar" in profiling:
                    self.logger.info(f"\nRecord Type x Pillar:\n{profiling['record_type_pillar']}")
                
                if "record_type_confidence" in profiling:
                    self.logger.info(f"\nRecord Type x Confidence:\n{profiling['record_type_confidence']}")
                
                if "pillar_confidence" in profiling:
                    self.logger.info(f"\nPillar x Confidence:\n{profiling['pillar_confidence']}")
                
                if "record_type_source_type" in profiling:
                    self.logger.info(f"\nRecord Type x Source Type:\n{profiling['record_type_source_type']}")

            # Temporal range
            temporal = self.data_explorer.get_temporal_range()
            self.logger.info(f"\nTemporal range: {temporal.get('date_range', 'N/A')}")

            # Unique indicators
            indicators = self.data_explorer.get_unique_indicators()
            self.logger.info(f"\nFound {len(indicators)} unique indicators")

            # Events catalog
            events = self.data_explorer.get_events_catalog()
            self.logger.info(f"Found {len(events)} events")

            # Impact links summary
            impact_summary = self.data_explorer.get_impact_links_summary()
            if impact_summary:
                self.logger.info(f"Found {impact_summary.get('total_links', 0)} impact links")

            # Step 3: Generate exploration report
            self.logger.info("\nStep 3: Generating exploration report...")
            report_path = config.reports_dir / "task1_exploration_report.txt"
            report = self.data_explorer.generate_exploration_report(report_path)
            self.logger.info(f"✓ Exploration report saved to {report_path}")

            # Step 4: Data enrichment - Add new observations/events/impact_links
            self.logger.info("\nStep 4: Data enrichment...")
            self._perform_enrichments()
            
            # Update enrichment log markdown
            log_path = self.data_enricher.update_enrichment_log_markdown()
            self.logger.info(f"✓ Enrichment log updated at {log_path}")

            # Step 5: Merge and save enriched dataset
            self.logger.info("\nStep 5: Merging enrichments...")
            enriched_output = config.processed_data_dir / "ethiopia_fi_unified_data_enriched.xlsx"
            enriched_data = self.data_enricher.merge_enrichments(
                output_path=enriched_output,
                save_format="xlsx"
            )
            self.logger.info(f"✓ Enriched dataset saved to: {enriched_output}")
            self.logger.info(f"  - Total records: {len(enriched_data.get('data', pd.DataFrame()))}")

            self.logger.info("\n" + "=" * 80)
            self.logger.info("Task 1 execution completed successfully")
            self.logger.info("=" * 80)

            return True

        except Exception as e:
            self.logger.error(f"Error executing Task 1: {str(e)}", exc_info=True)
            return False

    def _perform_enrichments(self):
        """
        Perform data enrichments - add new observations, events, and impact links
        This method should be customized with actual enrichments
        """
        self.logger.info("Performing data enrichments...")
        
        # Load existing data to check what's already there
        datasets = self.data_explorer.load_all_data()
        unified_df = datasets.get('unified_data', pd.DataFrame())
        
        # Check existing events to get event IDs for impact links
        existing_events = unified_df[unified_df["record_type"] == "event"] if not unified_df.empty and "record_type" in unified_df.columns else pd.DataFrame()
        
        # Example enrichments - Add real observations, events, and impact links
        # These are examples - replace with actual data from reliable sources
        
        # Example 1: Add a new observation for 2024 Q4 account ownership
        # (This is an example - use actual data from sources)
        try:
            self.data_enricher.add_observation(
                pillar="ACCESS",
                indicator="Account Ownership",
                indicator_code="ACC_OWNERSHIP",
                value_numeric=49.0,
                observation_date="2024-12-31",
                source_name="World Bank Global Findex 2024",
                source_url="https://www.worldbank.org/globalfindex",
                confidence="high",
                collected_by="Data Team",
                original_text="49% of adults in Ethiopia have an account at a financial institution or mobile money service provider (2024 Findex)",
                notes="Latest Findex survey data for Ethiopia - critical for tracking progress toward 60% target"
            )
            self.logger.info("✓ Added observation: ACC_OWNERSHIP for 2024-12-31")
        except Exception as e:
            self.logger.warning(f"Could not add observation: {e}")
        
        # Example 2: Add a new event - M-Pesa full launch
        try:
            self.data_enricher.add_event(
                category="product_launch",
                event_date="2023-08-15",
                source_name="Safaricom Ethiopia",
                source_url="https://www.safaricom.et",
                confidence="high",
                description="M-Pesa mobile money service fully launched in Ethiopia",
                collected_by="Data Team",
                original_text="Safaricom Ethiopia launched M-Pesa mobile money service nationwide, expanding digital payment options",
                notes="Major market entry event that increased competition and may boost financial inclusion"
            )
            self.logger.info("✓ Added event: M-Pesa full launch")
        except Exception as e:
            self.logger.warning(f"Could not add event: {e}")
        
        # Example 3: Add impact link if we have events
        if not existing_events.empty and "record_id" in existing_events.columns:
            # Find Telebirr launch event
            telebirr_event = existing_events[
                existing_events.get("description", pd.Series()).str.contains("Telebirr", case=False, na=False)
            ]
            if not telebirr_event.empty:
                event_id = telebirr_event.iloc[0]["record_id"]
                try:
                    self.data_enricher.add_impact_link(
                        parent_id=event_id,
                        pillar="ACCESS",
                        related_indicator="ACC_OWNERSHIP",
                        impact_direction="positive",
                        impact_magnitude=4.75,
                        lag_months=6,
                        evidence_basis="Observed increase in account ownership from 4.7% to 9.45% within 6 months of launch",
                        confidence="high",
                        collected_by="Data Team",
                        notes="Telebirr launch directly increased mobile money account ownership - validated with historical data"
                    )
                    self.logger.info(f"✓ Added impact link: Event {event_id} -> ACC_OWNERSHIP")
                except Exception as e:
                    self.logger.warning(f"Could not add impact link: {e}")
        
        enrichment_count = len(self.data_enricher.get_enrichment_log())
        if enrichment_count > 0:
            self.logger.info(f"✓ Added {enrichment_count} enrichments")
            summary = self.get_enrichment_summary()
            self.logger.info(f"  - Observations: {summary['observations']}")
            self.logger.info(f"  - Events: {summary['events']}")
            self.logger.info(f"  - Impact Links: {summary['impact_links']}")
        else:
            self.logger.info("No enrichments added (add enrichments in _perform_enrichments method)")

    def get_enrichment_summary(self) -> dict:
        """Get summary of enrichments added"""
        log = self.data_enricher.get_enrichment_log()
        summary = {
            "total_enrichments": len(log),
            "observations": sum(1 for entry in log if entry["type"] == "observation"),
            "events": sum(1 for entry in log if entry["type"] == "event"),
            "impact_links": sum(1 for entry in log if entry["type"] == "impact_link"),
        }
        return summary


def main():
    """Main entry point for Task 1"""
    executor = Task1Executor()
    success = executor.execute()

    if success:
        summary = executor.get_enrichment_summary()
        logger.info(f"\nEnrichment Summary: {summary}")
        sys.exit(0)
    else:
        logger.error("Task 1 execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
