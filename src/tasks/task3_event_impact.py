"""
Task 3: Event Impact Modeling
Main script for executing Task 3 requirements
"""

import sys
from pathlib import Path
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config import config
from src.models.event_impact import EventImpactModeler
from src.models.association_matrix import AssociationMatrixBuilder
from src.models.comparable_evidence import ComparableEvidence

logger = get_logger(__name__)


class EventImpactModeling:
    """Comprehensive event impact modeling pipeline"""

    def __init__(self):
        """Initialize event impact modeling"""
        self.logger = get_logger(__name__)
        self.impact_modeler = EventImpactModeler()
        self.matrix_builder = AssociationMatrixBuilder(self.impact_modeler)
        self.comparable_evidence = ComparableEvidence()

    def run_modeling(self) -> bool:
        """
        Execute comprehensive event impact modeling

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("Starting Event Impact Modeling")
            self.logger.info("=" * 80)

            # Step 1: Understand the Impact Data
            self.logger.info("\nStep 1: Loading and understanding impact data...")
            impact_data = self.impact_modeler.load_impact_data()
            self.logger.info(f"✓ Loaded {len(impact_data['impact_links'])} impact links")
            self.logger.info(f"✓ Loaded {len(impact_data['events'])} events")
            self.logger.info(f"✓ Joined {len(impact_data['joined_data'])} impact-event pairs")

            # Step 2: Create Impact Summary
            self.logger.info("\nStep 2: Creating impact summary...")
            impact_summary = self.impact_modeler.get_impact_summary()
            if not impact_summary.empty:
                self.logger.info(f"✓ Impact summary created: {len(impact_summary)} relationships")
                summary_path = config.reports_dir / "impact_summary.csv"
                impact_summary.to_csv(summary_path, index=False)
                self.logger.info(f"✓ Summary saved to {summary_path}")
            else:
                self.logger.warning("No impact summary data available")

            # Step 3: Build Association Matrix
            self.logger.info("\nStep 3: Building event-indicator association matrix...")
            association_matrix = self.matrix_builder.build_association_matrix()
            if not association_matrix.empty:
                self.logger.info(f"✓ Association matrix created: {association_matrix.shape}")
                matrix_path = config.reports_dir / "association_matrix.csv"
                association_matrix.to_csv(matrix_path, index=True)
                self.logger.info(f"✓ Matrix saved to {matrix_path}")

                # Matrix summary
                summary = self.matrix_builder.get_matrix_summary(association_matrix)
                self.logger.info(f"  - Events with impacts: {summary.get('events_with_impacts', 0)}")
                self.logger.info(f"  - Total impacts: {summary.get('total_impacts', 0)}")

                # Visualize matrix
                self.logger.info("\nStep 4: Creating matrix visualization...")
                viz_path = config.reports_dir / "figures" / "association_matrix_heatmap.png"
                self.matrix_builder.visualize_matrix(association_matrix, save_path=viz_path)
            else:
                self.logger.warning("Could not build association matrix")

            # Step 5: Validate Against Historical Data
            self.logger.info("\nStep 5: Validating against historical data...")
            validation_results = self._validate_historical_impacts()
            if validation_results:
                self.logger.info(f"✓ Validated {len(validation_results)} event-indicator pairs")
                for result in validation_results:
                    if result.get("validated"):
                        error = result.get("relative_error_pct", 0)
                        self.logger.info(
                            f"  - {result['event_id']} -> {result['indicator_code']}: "
                            f"Error: {error:.1f}%"
                        )

            # Step 6: Generate Methodology Documentation
            self.logger.info("\nStep 6: Generating methodology documentation...")
            methodology = self._generate_methodology_documentation()
            methodology_path = config.reports_dir / "impact_modeling_methodology.md"
            with open(methodology_path, "w", encoding="utf-8") as f:
                f.write(methodology)
            self.logger.info(f"✓ Methodology saved to {methodology_path}")

            self.logger.info("\n" + "=" * 80)
            self.logger.info("Event Impact Modeling completed successfully")
            self.logger.info("=" * 80)
            self.logger.info("\nNext steps:")
            self.logger.info("1. Review association matrix in reports/association_matrix.csv")
            self.logger.info("2. Check validation results")
            self.logger.info("3. Review methodology documentation")
            self.logger.info("4. Create impact modeling notebook with detailed analysis")

            return True

        except Exception as e:
            self.logger.error(f"Error in event impact modeling: {str(e)}", exc_info=True)
            return False

    def _validate_historical_impacts(self) -> List[Dict]:
        """Validate model against known historical impacts"""
        validation_results = []

        # Known validation case: Telebirr launch
        # Mobile money accounts: 4.7% (2021) to 9.45% (2024) = +4.75pp
        try:
            result = self.impact_modeler.validate_against_historical_data(
                indicator_code="ACC_MM_ACCOUNT",
                event_id="EVT_0001",  # Telebirr launch
                observed_change=4.75,
                observed_period=("2021-05-01", "2024-12-31")
            )
            validation_results.append(result)
        except Exception as e:
            self.logger.warning(f"Could not validate Telebirr impact: {e}")

        return validation_results

    def _generate_methodology_documentation(self) -> str:
        """Generate methodology documentation"""
        return """# Event Impact Modeling Methodology

## Overview

This document describes the methodology for modeling how events (policies, product launches, infrastructure investments) affect financial inclusion indicators in Ethiopia.

## Data Sources

### Impact Links
- Source: Enriched dataset impact_links sheet
- Contains: Event-indicator relationships with direction, magnitude, and lag
- Join: Linked to events via parent_id = record_id

### Events
- Source: Unified dataset (record_type = "event")
- Contains: Event details (date, category, description)
- Categories: policy, product_launch, infrastructure, market_entry, etc.

## Functional Forms

### Effect Representation Over Time

Three functional forms are used to represent event effects:

1. **Immediate Effect**: Effect occurs immediately after lag period
   - Formula: `effect(t) = magnitude if t >= lag, else 0`

2. **Gradual Effect**: Effect builds gradually over 12 months
   - Formula: `effect(t) = magnitude * min((t - lag) / 12, 1)`

3. **Distributed Lag**: Effect decays over time (5% per month)
   - Formula: `effect(t) = magnitude * (0.95 ^ (t - lag))`

### Combining Multiple Events

Three combination methods:

1. **Additive**: Effects are summed
   - `combined = effect1 + effect2 + ...`

2. **Multiplicative**: Effects compound
   - `combined = base * (1 + effect1) * (1 + effect2) * ...`

3. **Maximum**: Take the largest effect
   - `combined = max(effect1, effect2, ...)`

## Association Matrix

The association matrix captures:
- **Rows**: Events (by event ID)
- **Columns**: Indicators (by indicator code)
- **Values**: Impact magnitude (positive for increase, negative for decrease)

### Matrix Construction

1. Load all impact_links
2. Join with events using parent_id
3. For each event-indicator pair:
   - Extract impact_magnitude and impact_direction
   - Convert to signed value (negative for decrease)
   - If multiple links, take maximum absolute value
4. Fill missing with 0 (no impact)

## Validation Approach

### Historical Validation

For events with known outcomes:
1. Extract predicted impact from model
2. Compare with observed change in indicator
3. Calculate relative error: `|predicted - observed| / |observed| * 100`
4. Document discrepancies and potential explanations

### Known Validation Cases

- **Telebirr Launch (May 2021)**: Mobile money accounts 4.7% → 9.45% (+4.75pp)
- **M-Pesa Entry (Aug 2023)**: Impact still unfolding

## Assumptions

1. **Lag Effects**: Events have lagged impacts (6-18 months typical)
2. **Linear Relationships**: Effects are approximately linear in magnitude
3. **Independence**: Events have independent effects (additive combination)
4. **Temporal Stability**: Impact patterns are consistent over time
5. **Comparable Contexts**: Evidence from similar countries is applicable

## Limitations

1. **Sparse Data**: Limited historical data for many event types
2. **Confounding Factors**: Multiple events occur simultaneously
3. **Non-linearity**: Effects may not be linear at extremes
4. **Context Dependency**: Country-specific factors may differ
5. **Measurement Error**: Survey data has inherent uncertainty

## Uncertainty Quantification

- **High Confidence**: Validated against historical data
- **Medium Confidence**: Based on comparable country evidence
- **Low Confidence**: Estimated from limited or indirect evidence

## Sources for Impact Estimates

- Impact links from enriched dataset
- Comparable country evidence (Kenya, Tanzania, Rwanda)
- Academic research on mobile money impacts
- Operator reports and industry analysis
- Policy evaluation studies

## Refinement Process

1. Compare predicted vs. observed for known cases
2. Identify systematic biases
3. Adjust magnitude estimates based on validation
4. Update lag assumptions if needed
5. Document reasoning for all adjustments

---

*Methodology version: 1.0*  
*Last updated: """ + datetime.now().strftime("%Y-%m-%d") + """*
"""


def main():
    """Main entry point for event impact modeling"""
    modeler = EventImpactModeling()
    success = modeler.run_modeling()

    if success:
        sys.exit(0)
    else:
        logger.error("Event impact modeling failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
