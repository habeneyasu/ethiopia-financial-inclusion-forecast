"""
Unit tests for DataEnricher class
"""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch
from src.data.enricher import DataEnricher
from src.data.loader import DataLoader
from src.data.explorer import DataExplorer


class TestDataEnricher:
    """Test suite for DataEnricher"""

    def test_init(self):
        """Test DataEnricher initialization"""
        enricher = DataEnricher()
        assert enricher.data_loader is not None
        assert enricher.data_explorer is not None
        assert len(enricher._enrichment_log) == 0

    def test_add_observation(self):
        """Test adding an observation"""
        enricher = DataEnricher()

        observation = enricher.add_observation(
            pillar="Access",
            indicator="Account Ownership",
            indicator_code="ACC_001",
            value_numeric=45.5,
            observation_date="2023-01-01",
            source_name="World Bank",
            source_url="https://example.com",
            confidence="high"
        )

        assert observation["record_type"] == "observation"
        assert observation["pillar"] == "Access"
        assert observation["value_numeric"] == 45.5
        assert len(enricher._enrichment_log) == 1

    def test_add_event(self):
        """Test adding an event"""
        enricher = DataEnricher()

        event = enricher.add_event(
            category="policy",
            event_date="2023-01-01",
            source_name="Central Bank",
            source_url="https://example.com",
            confidence="high"
        )

        assert event["record_type"] == "event"
        assert event["category"] == "policy"
        assert event["pillar"] == ""  # Events should have empty pillar
        assert len(enricher._enrichment_log) == 1

    def test_add_impact_link(self):
        """Test adding an impact link"""
        enricher = DataEnricher()

        impact_link = enricher.add_impact_link(
            parent_id="EVT_001",
            pillar="Access",
            related_indicator="ACC_001",
            impact_direction="positive",
            impact_magnitude=0.15,
            lag_months=6
        )

        assert impact_link["parent_id"] == "EVT_001"
        assert impact_link["pillar"] == "Access"
        assert impact_link["impact_direction"] == "positive"
        assert len(enricher._enrichment_log) == 1

    @patch.object(DataLoader, "load_unified_data")
    def test_merge_enrichments(self, mock_load):
        """Test merging enrichments"""
        # Setup mock data
        mock_load.return_value = pd.DataFrame({
            "record_type": ["observation"],
            "indicator_code": ["ACC_001"]
        })

        enricher = DataEnricher()

        # Add some enrichments
        enricher.add_observation(
            pillar="Access",
            indicator="Test",
            indicator_code="ACC_002",
            value_numeric=50.0,
            observation_date="2023-01-01",
            source_name="Test",
            source_url="https://test.com"
        )

        result = enricher.merge_enrichments()

        assert "data" in result
        assert isinstance(result["data"], pd.DataFrame)
        assert len(result["data"]) >= 1

    def test_get_enrichment_log(self):
        """Test getting enrichment log"""
        enricher = DataEnricher()
        enricher.add_observation(
            pillar="Access",
            indicator="Test",
            indicator_code="ACC_001",
            value_numeric=50.0,
            observation_date="2023-01-01",
            source_name="Test",
            source_url="https://test.com"
        )

        log = enricher.get_enrichment_log()
        assert len(log) == 1
        assert log[0]["type"] == "observation"

    def test_clear_enrichment_log(self):
        """Test clearing enrichment log"""
        enricher = DataEnricher()
        enricher.add_observation(
            pillar="Access",
            indicator="Test",
            indicator_code="ACC_001",
            value_numeric=50.0,
            observation_date="2023-01-01",
            source_name="Test",
            source_url="https://test.com"
        )

        assert len(enricher._enrichment_log) == 1
        enricher.clear_enrichment_log()
        assert len(enricher._enrichment_log) == 0
