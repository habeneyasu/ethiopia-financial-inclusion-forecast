"""
Unit tests for utility modules
"""

import pytest
import logging
from pathlib import Path
from src.utils.logger import get_logger, ProjectLogger
from src.utils.config import Config


class TestLogger:
    """Test suite for logger utility"""

    def test_get_logger(self):
        """Test getting a logger"""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_logger_caching(self):
        """Test logger caching"""
        logger1 = ProjectLogger.get_logger("test_module")
        logger2 = ProjectLogger.get_logger("test_module")
        assert logger1 is logger2

    def test_logger_levels(self):
        """Test logger with different levels"""
        logger = get_logger("test_module", level=logging.DEBUG)
        assert logger.level == logging.DEBUG


class TestConfig:
    """Test suite for Config class"""

    def test_config_init(self):
        """Test Config initialization"""
        cfg = Config()
        assert cfg.project_root.exists() or cfg.project_root.parent.exists()
        assert cfg.data_dir.name == "data"

    def test_get_data_file_path(self):
        """Test getting data file path"""
        cfg = Config()
        path = cfg.get_data_file_path("test_file", ".csv")
        assert path.suffix == ".csv"
        assert "test_file" in str(path)

    def test_get_processed_file_path(self):
        """Test getting processed file path"""
        cfg = Config()
        path = cfg.get_processed_file_path("test_file", ".csv")
        assert path.suffix == ".csv"
        assert "processed" in str(path)

    def test_unsupported_extension(self):
        """Test unsupported file extension"""
        cfg = Config()
        with pytest.raises(ValueError):
            cfg.get_data_file_path("test_file", ".txt")
