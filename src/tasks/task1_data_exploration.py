"""
Task 1: Data Exploration and Enrichment
Main script for executing Task 1 requirements
"""

import sys
from pathlib import Path
from datetime import datetime
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

            # Step 1: Load all datasets
            self.logger.info("\nStep 1: Loading datasets...")
            datasets = self.data_explorer.load_all_data()
            self.logger.info("✓ All datasets loaded successfully")

            # Step 2: Explore the data
            self.logger.info("\nStep 2: Exploring data...")

            # Count records
            counts = self.data_explorer.get_record_counts()
            self.logger.info("Record counts calculated")

            # Temporal range
            temporal = self.data_explorer.get_temporal_range()
            self.logger.info(f"Temporal range: {temporal.get('date_range', 'N/A')}")

            # Unique indicators
            indicators = self.data_explorer.get_unique_indicators()
            self.logger.info(f"Found {len(indicators)} unique indicators")

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

            # Step 4: Data enrichment (placeholder - user will add their enrichments)
            self.logger.info("\nStep 4: Data enrichment ready...")
            self.logger.info("Use DataEnricher methods to add new observations, events, and impact links")
            self.logger.info("Example methods:")
            self.logger.info("  - data_enricher.add_observation(...)")
            self.logger.info("  - data_enricher.add_event(...)")
            self.logger.info("  - data_enricher.add_impact_link(...)")

            # Step 5: Save enriched dataset (when enrichments are added)
            self.logger.info("\nStep 5: Ready to merge enrichments...")
            enriched_output = config.processed_data_dir / "ethiopia_fi_unified_data_enriched.xlsx"
            self.logger.info(f"Enriched dataset will be saved to: {enriched_output}")

            self.logger.info("\n" + "=" * 80)
            self.logger.info("Task 1 execution completed successfully")
            self.logger.info("=" * 80)

            return True

        except Exception as e:
            self.logger.error(f"Error executing Task 1: {str(e)}", exc_info=True)
            return False

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
