"""
Exploratory Data Analysis
Main script for comprehensive EDA pipeline
"""

import sys
from pathlib import Path
from src.utils.logger import get_logger
from src.utils.config import config
from src.analysis.eda import EDAAnalyzer
from src.analysis.visualizer import DataVisualizer

logger = get_logger(__name__)


class ExploratoryDataAnalysis:
    """Comprehensive exploratory data analysis for financial inclusion forecasting"""

    def __init__(self):
        """Initialize EDA analysis pipeline"""
        self.logger = get_logger(__name__)
        self.eda_analyzer = EDAAnalyzer()
        self.visualizer = DataVisualizer(self.eda_analyzer)

    def run_analysis(self) -> bool:
        """
        Execute comprehensive exploratory data analysis

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("Starting Exploratory Data Analysis")
            self.logger.info("=" * 80)

            # Step 1: Dataset Overview
            self.logger.info("\nStep 1: Dataset Overview...")
            overview = self.eda_analyzer.get_dataset_overview()
            self.logger.info(f"✓ Total records: {overview.get('total_records', 0)}")
            self.logger.info(f"✓ Record types: {overview.get('by_record_type', {})}")

            # Step 2: Temporal Coverage
            self.logger.info("\nStep 2: Temporal Coverage Analysis...")
            temporal_coverage = self.eda_analyzer.get_temporal_coverage()
            self.logger.info(f"✓ Temporal coverage matrix created: {temporal_coverage.shape}")

            # Step 3: Access Analysis
            self.logger.info("\nStep 3: Access Trajectory Analysis...")
            access_traj = self.eda_analyzer.analyze_access_trajectory()
            if not access_traj.empty:
                self.logger.info(f"✓ Access trajectory analyzed: {len(access_traj)} data points")
            else:
                self.logger.warning("No access trajectory data found")

            # Step 4: Usage Analysis
            self.logger.info("\nStep 4: Usage Trends Analysis...")
            usage_trends = self.eda_analyzer.analyze_usage_trends()
            if not usage_trends.empty:
                self.logger.info(f"✓ Usage trends analyzed: {len(usage_trends)} data points")
            else:
                self.logger.warning("No usage trends data found")

            # Step 5: Infrastructure Analysis
            self.logger.info("\nStep 5: Infrastructure Analysis...")
            infrastructure = self.eda_analyzer.analyze_infrastructure()
            if not infrastructure.empty:
                self.logger.info(f"✓ Infrastructure data analyzed: {len(infrastructure)} data points")
            else:
                self.logger.warning("No infrastructure data found")

            # Step 6: Event Timeline
            self.logger.info("\nStep 6: Event Timeline Analysis...")
            events = self.eda_analyzer.get_event_timeline()
            if not events.empty:
                self.logger.info(f"✓ Events cataloged: {len(events)}")
            else:
                self.logger.warning("No events found")

            # Step 7: Correlation Analysis
            self.logger.info("\nStep 7: Correlation Analysis...")
            correlation = self.eda_analyzer.analyze_correlations()
            if not correlation.empty:
                self.logger.info(f"✓ Correlation matrix created: {correlation.shape}")
            else:
                self.logger.warning("No correlation data available")

            # Step 8: Data Gaps
            self.logger.info("\nStep 8: Data Gap Identification...")
            gaps = self.eda_analyzer.identify_data_gaps()
            self.logger.info(f"✓ Sparse indicators: {len(gaps.get('sparse_indicators', {}))}")

            # Step 9: Generate Visualizations
            self.logger.info("\nStep 9: Generating Visualizations...")
            figures_dir = config.reports_dir / "figures"
            figures_dir.mkdir(parents=True, exist_ok=True)

            # Access trajectory
            self.visualizer.plot_access_trajectory(
                save_path=figures_dir / "access_trajectory.html"
            )

            # Temporal coverage
            self.visualizer.plot_temporal_coverage(
                save_path=figures_dir / "temporal_coverage.html"
            )

            # Event timeline
            self.visualizer.plot_event_timeline(
                save_path=figures_dir / "event_timeline.html"
            )

            # Correlation heatmap
            self.visualizer.plot_correlation_heatmap(
                save_path=figures_dir / "correlation_heatmap.html"
            )

            # Usage trends
            self.visualizer.plot_usage_trends(
                save_path=figures_dir / "usage_trends.html"
            )

            self.logger.info(f"✓ Visualizations saved to {figures_dir}")

            # Step 10: Generate Insights Summary
            self.logger.info("\nStep 10: Generating Insights Summary...")
            insights_path = config.reports_dir / "eda_insights_summary.txt"
            summary = self.eda_analyzer.generate_insights_summary(insights_path)
            self.logger.info(f"✓ Insights summary saved to {insights_path}")

            self.logger.info("\n" + "=" * 80)
            self.logger.info("Exploratory Data Analysis completed successfully")
            self.logger.info("=" * 80)
            self.logger.info("\nNext steps:")
            self.logger.info("1. Review visualizations in reports/figures/")
            self.logger.info("2. Check insights summary in reports/eda_insights_summary.txt")
            self.logger.info("3. Create EDA notebook with detailed analysis")
            self.logger.info("4. Document at least 5 key insights")

            return True

        except Exception as e:
            self.logger.error(f"Error in exploratory data analysis: {str(e)}", exc_info=True)
            return False


def main():
    """Main entry point for exploratory data analysis"""
    analyzer = ExploratoryDataAnalysis()
    success = analyzer.run_analysis()

    if success:
        sys.exit(0)
    else:
        logger.error("Exploratory data analysis failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
