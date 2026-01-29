"""
Comparable Country Evidence Module
Uses documented impacts from similar contexts when Ethiopian data is insufficient
"""

import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ComparableEvidence:
    """Manage comparable country evidence for impact estimation"""

    def __init__(self):
        """Initialize ComparableEvidence"""
        self.logger = get_logger(__name__)
        self._evidence_db: Dict = {}

    def add_evidence(
        self,
        event_type: str,
        country: str,
        indicator: str,
        impact_magnitude: float,
        lag_months: int,
        source: str,
        notes: Optional[str] = None
    ):
        """
        Add comparable country evidence

        Args:
            event_type: Type of event (e.g., "product_launch", "policy")
            country: Country name
            indicator: Indicator code
            impact_magnitude: Impact magnitude
            lag_months: Lag in months
            source: Source of evidence
            notes: Additional notes
        """
        key = f"{event_type}_{indicator}"
        if key not in self._evidence_db:
            self._evidence_db[key] = []

        self._evidence_db[key].append({
            "country": country,
            "indicator": indicator,
            "impact_magnitude": impact_magnitude,
            "lag_months": lag_months,
            "source": source,
            "notes": notes
        })

        self.logger.info(f"Added evidence: {country} - {event_type} on {indicator}")

    def get_evidence(
        self,
        event_type: str,
        indicator: str
    ) -> List[Dict]:
        """
        Get comparable evidence for event type and indicator

        Args:
            event_type: Type of event
            indicator: Indicator code

        Returns:
            List of evidence records
        """
        key = f"{event_type}_{indicator}"
        return self._evidence_db.get(key, [])

    def estimate_impact_from_evidence(
        self,
        event_type: str,
        indicator: str,
        method: str = "median"
    ) -> Dict:
        """
        Estimate impact based on comparable evidence

        Args:
            event_type: Type of event
            indicator: Indicator code
            method: Aggregation method ("median", "mean", "min", "max")

        Returns:
            Dictionary with estimated impact
        """
        evidence = self.get_evidence(event_type, indicator)

        if not evidence:
            return {
                "estimated": False,
                "reason": "No comparable evidence available"
            }

        magnitudes = [e["impact_magnitude"] for e in evidence]
        lags = [e["lag_months"] for e in evidence]

        if method == "median":
            impact = float(np.median(magnitudes))
            lag = int(np.median(lags))
        elif method == "mean":
            impact = float(np.mean(magnitudes))
            lag = int(np.mean(lags))
        elif method == "min":
            impact = float(np.min(magnitudes))
            lag = int(np.min(lags))
        elif method == "max":
            impact = float(np.max(magnitudes))
            lag = int(np.max(lags))
        else:
            impact = float(np.median(magnitudes))
            lag = int(np.median(lags))

        return {
            "estimated": True,
            "impact_magnitude": impact,
            "lag_months": lag,
            "evidence_count": len(evidence),
            "countries": [e["country"] for e in evidence],
            "method": method
        }
