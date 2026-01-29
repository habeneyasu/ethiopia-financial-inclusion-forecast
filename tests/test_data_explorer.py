"""
Unit tests for DataExplorer class
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.data.explorer import DataExplorer
from src.data.loader import DataLoader


class TestDataExplorer:
    """Test suite for DataExplorer"""

    def test_init(self):
        """Test DataExplorer initialization"""
        explorer = DataExplorer()
        assert explorer.data_loader is not None
        assert explorer._unified_data is None

    def test_init_with_loader(self):
        """Test DataExplorer with custom loader"""
        loader = DataLoader()
        explorer = DataExplorer(data_loader=loader)
        assert explorer.data_loader == loader

    @patch.object(DataLoader, "load_unified_data")
    @patch.object(DataLoader, "load_reference_codes")
    def test_load_all_data(self, mock_ref_codes, mock_unified):
        """Test loading all data"""
        mock_unified.return_value = pd.DataFrame({"col1": [1, 2]})
        mock_ref_codes.return_value = pd.DataFrame({"col2": [3, 4]})

        explorer = DataExplorer()
        result = explorer.load_all_data()

        assert "unified_data" in result
        assert "reference_codes" in result
        assert isinstance(result["unified_data"], pd.DataFrame)

    def test_get_record_counts(self):
        """Test getting record counts"""
        explorer = DataExplorer()
        explorer._unified_data = pd.DataFrame({
            "record_type": ["observation", "event", "observation"],
            "pillar": ["Access", "Usage", "Access"],
            "confidence": ["high", "medium", "high"]
        })

        counts = explorer.get_record_counts()

        assert "record_type" in counts
        assert "pillar" in counts
        assert "confidence" in counts

    def test_get_temporal_range(self):
        """Test getting temporal range"""
        explorer = DataExplorer()
        explorer._unified_data = pd.DataFrame({
            "observation_date": ["2020-01-01", "2021-06-15", "2022-12-31"]
        })

        temporal = explorer.get_temporal_range()

        assert "min_date" in temporal
        assert "max_date" in temporal
        assert temporal["min_date"] is not None

    def test_get_unique_indicators(self):
        """Test getting unique indicators"""
        explorer = DataExplorer()
        explorer._unified_data = pd.DataFrame({
            "indicator_code": ["ACC_001", "ACC_001", "USG_002"],
            "indicator": ["Indicator 1", "Indicator 1", "Indicator 2"],
            "pillar": ["Access", "Access", "Usage"]
        })

        indicators = explorer.get_unique_indicators()

        assert len(indicators) == 2
        assert "indicator_code" in indicators.columns

    def test_get_events_catalog(self):
        """Test getting events catalog"""
        explorer = DataExplorer()
        explorer._unified_data = pd.DataFrame({
            "record_type": ["event", "observation", "event"],
            "event_date": ["2020-01-01", None, "2021-06-15"],
            "category": ["policy", None, "product_launch"]
        })

        events = explorer.get_events_catalog()

        assert len(events) == 2
        assert all(events["record_type"] == "event")

    def test_get_impact_links_summary(self):
        """Test getting impact links summary"""
        explorer = DataExplorer()
        explorer._impact_links = pd.DataFrame({
            "parent_id": ["EVT_001", "EVT_001", "EVT_002"],
            "pillar": ["Access", "Usage", "Access"],
            "impact_direction": ["positive", "positive", "negative"]
        })

        summary = explorer.get_impact_links_summary()

        assert summary["total_links"] == 3
        assert summary["unique_events"] == 2

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", create=True)
    def test_generate_exploration_report(self, mock_open, mock_mkdir):
        """Test generating exploration report"""
        explorer = DataExplorer()
        explorer._unified_data = pd.DataFrame({
            "record_type": ["observation", "event"],
            "indicator_code": ["ACC_001", None]
        })

        report = explorer.generate_exploration_report()

        assert isinstance(report, str)
        assert "DATA EXPLORATION REPORT" in report
