"""
Unit tests for DataLoader class
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.data.loader import DataLoader
from src.utils.config import config


class TestDataLoader:
    """Test suite for DataLoader"""

    def test_init(self):
        """Test DataLoader initialization"""
        loader = DataLoader()
        assert loader.base_path == config.raw_data_dir
        assert loader._cache == {}

    def test_init_custom_path(self):
        """Test DataLoader with custom path"""
        custom_path = Path("/custom/path")
        loader = DataLoader(base_path=custom_path)
        assert loader.base_path == custom_path

    @patch("src.data.loader.Path.exists")
    @patch("pandas.read_csv")
    def test_load_csv_file(self, mock_read_csv, mock_exists):
        """Test loading CSV file"""
        mock_exists.return_value = True
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = mock_df

        loader = DataLoader()
        result = loader.load_file("test_file", use_cache=False)

        assert isinstance(result, pd.DataFrame)
        mock_read_csv.assert_called_once()

    @patch("src.data.loader.Path.exists")
    @patch("pandas.read_excel")
    def test_load_excel_file(self, mock_read_excel, mock_exists):
        """Test loading Excel file"""
        mock_exists.return_value = True
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_excel.return_value = mock_df

        loader = DataLoader()
        # Mock the file suffix
        with patch.object(Path, "suffix", ".xlsx"):
            result = loader.load_file("test_file.xlsx", use_cache=False)

        assert isinstance(result, pd.DataFrame)

    def test_load_file_not_found(self):
        """Test loading non-existent file"""
        loader = DataLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_file("nonexistent_file", use_cache=False)

    def test_cache_functionality(self):
        """Test caching functionality"""
        loader = DataLoader()
        assert len(loader._cache) == 0

        loader._cache["test"] = pd.DataFrame()
        assert len(loader._cache) == 1

        loader.clear_cache()
        assert len(loader._cache) == 0

    @patch.object(DataLoader, "load_file")
    def test_load_unified_data(self, mock_load_file):
        """Test loading unified data"""
        mock_df = pd.DataFrame()
        mock_load_file.return_value = mock_df

        loader = DataLoader()
        result = loader.load_unified_data()

        assert isinstance(result, pd.DataFrame)
        mock_load_file.assert_called_once()

    @patch.object(DataLoader, "load_file")
    def test_load_reference_codes(self, mock_load_file):
        """Test loading reference codes"""
        mock_df = pd.DataFrame()
        mock_load_file.return_value = mock_df

        loader = DataLoader()
        result = loader.load_reference_codes()

        assert isinstance(result, pd.DataFrame)
        mock_load_file.assert_called_once()
