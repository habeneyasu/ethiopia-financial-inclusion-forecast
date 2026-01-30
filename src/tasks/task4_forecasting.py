"""
Task 4: Forecasting Access and Usage
Main script for executing Task 4 requirements
"""

import sys
from pathlib import Path
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config import config
from src.models.forecaster import ForecastModeler
from src.analysis.visualizer import DataVisualizer
from src.analysis.eda import EDAAnalyzer

logger = get_logger(__name__)


class ForecastingPipeline:
    """Comprehensive forecasting pipeline for Access and Usage"""

    def __init__(self):
        """Initialize forecasting pipeline"""
        self.logger = get_logger(__name__)
        self.forecast_modeler = ForecastModeler()
        self.eda_analyzer = EDAAnalyzer()
        self.visualizer = DataVisualizer(self.eda_analyzer)

    def run_forecasting(self) -> bool:
        """
        Execute comprehensive forecasting pipeline

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("Starting Forecasting Pipeline: Access and Usage")
            self.logger.info("=" * 80)

            # Step 1: Define Targets
            self.logger.info("\nStep 1: Defining forecast targets...")
            targets = {
                "access": {
                    "indicator_code": "ACC_OWNERSHIP",
                    "pillar": "ACCESS",
                    "description": "Account Ownership Rate (% of adults with account)"
                },
                "usage": {
                    "indicator_code": "USG_DIGITAL_PAY",
                    "pillar": "USAGE",
                    "description": "Digital Payment Usage (% of adults using digital payments)"
                }
            }
            self.logger.info(f"✓ Target 1: {targets['access']['description']}")
            self.logger.info(f"✓ Target 2: {targets['usage']['description']}")

            # Step 2: Load Historical Data
            self.logger.info("\nStep 2: Loading historical data...")
            self.forecast_modeler.load_data()
            self.logger.info("✓ Historical data loaded")

            # Step 3: Generate Forecasts
            forecast_years = [2025, 2026, 2027]
            results = {}

            for target_name, target_info in targets.items():
                self.logger.info(f"\nStep 3: Forecasting {target_name.upper()}...")
                try:
                    result = self.forecast_modeler.forecast_indicator(
                        indicator_code=target_info["indicator_code"],
                        pillar=target_info["pillar"],
                        forecast_years=forecast_years,
                        include_events=True,
                        model_type="linear",
                        confidence_level=0.95
                    )
                    results[target_name] = result
                    self.logger.info(f"✓ {target_name} forecast completed")
                    self.logger.info(f"  Model RMSE: {result['model_metrics']['rmse']:.2f}")
                    self.logger.info(f"  Model MAE: {result['model_metrics']['mae']:.2f}")
                except Exception as e:
                    self.logger.warning(f"⚠ Could not forecast {target_name}: {e}")
                    # Try with alternative indicator codes
                    if target_name == "usage":
                        # Try mobile money account rate as proxy
                        try:
                            result = self.forecast_modeler.forecast_indicator(
                                indicator_code="ACC_MM_ACCOUNT",
                                pillar="ACCESS",
                                forecast_years=forecast_years,
                                include_events=True,
                                model_type="linear",
                                confidence_level=0.95
                            )
                            results[target_name] = result
                            self.logger.info(f"✓ Used ACC_MM_ACCOUNT as proxy for usage")
                        except Exception as e2:
                            self.logger.error(f"✗ Failed to forecast {target_name} with proxy: {e2}")

            # Step 4: Generate Forecast Tables
            self.logger.info("\nStep 4: Generating forecast tables...")
            for target_name, result in results.items():
                table = self.forecast_modeler.generate_forecast_table(result, scenario="base")
                self.logger.info(f"\n{targets[target_name]['description']} Forecast (Base Scenario):")
                self.logger.info(f"\n{table.to_string(index=False)}")

            # Step 5: Scenario Analysis
            self.logger.info("\nStep 5: Generating scenario analysis...")
            for target_name, result in results.items():
                scenarios = result["scenarios"]
                self.logger.info(f"\n{targets[target_name]['description']} - Scenario Ranges:")
                for scenario_name, scenario_df in scenarios.items():
                    avg_forecast = scenario_df["forecast"].mean()
                    self.logger.info(f"  {scenario_name.capitalize()}: {avg_forecast:.1f}% average")

            # Step 6: Save Results
            self.logger.info("\nStep 6: Saving forecast results...")
            output_dir = Path(config.get("paths", {}).get("reports", "reports"))
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save forecast summary
            summary_path = output_dir / "forecast_summary.txt"
            with open(summary_path, "w") as f:
                f.write("=" * 80 + "\n")
                f.write("FORECAST SUMMARY: ACCESS AND USAGE (2025-2027)\n")
                f.write("=" * 80 + "\n\n")

                for target_name, result in results.items():
                    f.write(f"\n{targets[target_name]['description']}\n")
                    f.write("-" * 80 + "\n")
                    table = self.forecast_modeler.generate_forecast_table(result, scenario="base")
                    f.write(table.to_string(index=False))
                    f.write("\n\n")

                    # Add scenario comparison
                    f.write("Scenario Comparison:\n")
                    for scenario_name, scenario_df in result["scenarios"].items():
                        avg = scenario_df["forecast"].mean()
                        f.write(f"  {scenario_name.capitalize()}: {avg:.1f}% average\n")
                    f.write("\n")

            self.logger.info(f"✓ Forecast summary saved to {summary_path}")

            # Step 7: Interpretation
            self.logger.info("\nStep 7: Generating interpretation...")
            self._interpret_results(results, targets)

            self.logger.info("\n" + "=" * 80)
            self.logger.info("Forecasting pipeline completed successfully")
            self.logger.info("=" * 80)

            return True

        except Exception as e:
            self.logger.error(f"Error executing forecasting pipeline: {e}", exc_info=True)
            return False

    def _interpret_results(self, results: dict, targets: dict):
        """Generate interpretation of forecast results"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("FORECAST INTERPRETATION")
        self.logger.info("=" * 80)

        for target_name, result in results.items():
            self.logger.info(f"\n{targets[target_name]['description']}:")
            forecast_df = result["forecast"]

            # Key predictions
            avg_forecast = forecast_df["forecast"].mean()
            growth = forecast_df["forecast"].iloc[-1] - forecast_df["forecast"].iloc[0]

            self.logger.info(f"  Average forecast (2025-2027): {avg_forecast:.1f}%")
            self.logger.info(f"  Projected growth: {growth:+.1f} percentage points")

            # Uncertainty
            avg_range = (forecast_df["upper_bound"] - forecast_df["lower_bound"]).mean()
            self.logger.info(f"  Average uncertainty range: ±{avg_range/2:.1f} percentage points")

            # Scenario ranges
            scenarios = result["scenarios"]
            optimistic_avg = scenarios["optimistic"]["forecast"].mean()
            pessimistic_avg = scenarios["pessimistic"]["forecast"].mean()
            scenario_range = optimistic_avg - pessimistic_avg

            self.logger.info(f"  Scenario range: {pessimistic_avg:.1f}% - {optimistic_avg:.1f}%")
            self.logger.info(f"  Total scenario spread: {scenario_range:.1f} percentage points")

        # Limitations
        self.logger.info("\nKey Limitations:")
        self.logger.info("  - Sparse historical data (5 Findex points over 13 years)")
        self.logger.info("  - Limited event impact data for some indicators")
        self.logger.info("  - Assumes trend continuation and known event effects")
        self.logger.info("  - Does not account for unknown future events")
        self.logger.info("  - Confidence intervals based on historical residuals only")


def main():
    """Main entry point for Task 4"""
    pipeline = ForecastingPipeline()
    success = pipeline.run_forecasting()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
