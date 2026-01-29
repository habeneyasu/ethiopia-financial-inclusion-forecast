"""
Configuration management module
"""

import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field

# Load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


@dataclass
class Config:
    """Project configuration class"""

    # Project paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = field(init=False)
    raw_data_dir: Path = field(init=False)
    processed_data_dir: Path = field(init=False)
    models_dir: Path = field(init=False)
    reports_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)

    # Data files
    unified_data_file: str = "ethiopia_fi_unified_data"
    reference_codes_file: str = "reference_codes"
    additional_data_guide_file: str = "Additional Data Points Guide"

    # Supported file extensions
    supported_extensions: tuple = (".csv", ".xlsx")

    def __post_init__(self):
        """Initialize derived paths"""
        self.data_dir = self.project_root / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        self.models_dir = self.project_root / "models"
        self.reports_dir = self.project_root / "reports"
        self.logs_dir = self.project_root / "logs"

    def get_data_file_path(self, filename: str, extension: str = ".csv") -> Path:
        """
        Get full path to a data file

        Args:
            filename: Base filename without extension
            extension: File extension (default: .csv)

        Returns:
            Full path to the file
        """
        if extension not in self.supported_extensions:
            raise ValueError(f"Unsupported extension: {extension}")

        return self.raw_data_dir / f"{filename}{extension}"

    def get_processed_file_path(self, filename: str, extension: str = ".csv") -> Path:
        """
        Get full path to a processed data file

        Args:
            filename: Base filename without extension
            extension: File extension (default: .csv)

        Returns:
            Full path to the processed file
        """
        return self.processed_data_dir / f"{filename}{extension}"

    @property
    def unified_data_paths(self) -> Dict[str, Path]:
        """Get all possible paths for unified data file"""
        return {
            ext: self.get_data_file_path(self.unified_data_file, ext)
            for ext in self.supported_extensions
        }

    @property
    def reference_codes_paths(self) -> Dict[str, Path]:
        """Get all possible paths for reference codes file"""
        return {
            ext: self.get_data_file_path(self.reference_codes_file, ext)
            for ext in self.supported_extensions
        }

    @property
    def additional_guide_paths(self) -> Dict[str, Path]:
        """Get all possible paths for additional data guide file"""
        return {
            ext: self.get_data_file_path(self.additional_data_guide_file, ext)
            for ext in self.supported_extensions
        }


# Global config instance
config = Config()
