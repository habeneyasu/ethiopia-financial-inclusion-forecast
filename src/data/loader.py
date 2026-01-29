"""
Data loading module with OOP design
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List, Union
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class DataLoader:
    """Class for loading data files with error handling and validation"""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize DataLoader

        Args:
            base_path: Base path for data files (defaults to config.raw_data_dir)
        """
        self.base_path = base_path or config.raw_data_dir
        self.logger = get_logger(__name__)
        self._cache: Dict[str, pd.DataFrame] = {}

    def _find_file(self, filename: str, extensions: tuple = (".csv", ".xlsx")) -> Optional[Path]:
        """
        Find file with any supported extension

        Args:
            filename: Base filename without extension
            extensions: Supported file extensions

        Returns:
            Path to file if found, None otherwise
        """
        for ext in extensions:
            file_path = self.base_path / f"{filename}{ext}"
            if file_path.exists():
                self.logger.info(f"Found file: {file_path}")
                return file_path

        self.logger.warning(f"File not found: {filename} with extensions {extensions}")
        return None

    def load_file(
        self,
        filename: str,
        sheet_name: Optional[Union[str, int, List]] = None,
        use_cache: bool = True,
        **kwargs
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Load a data file (CSV or Excel)

        Args:
            filename: Base filename without extension
            sheet_name: Sheet name(s) for Excel files (None for CSV or all sheets)
            use_cache: Whether to use cached data
            **kwargs: Additional arguments for pd.read_csv or pd.read_excel

        Returns:
            DataFrame or dict of DataFrames (for multiple sheets)

        Raises:
            FileNotFoundError: If file is not found
            ValueError: If file format is not supported
        """
        cache_key = f"{filename}_{sheet_name}"

        if use_cache and cache_key in self._cache:
            self.logger.debug(f"Loading {filename} from cache")
            return self._cache[cache_key]

        file_path = self._find_file(filename)
        if file_path is None:
            raise FileNotFoundError(f"File not found: {filename} in {self.base_path}")

        try:
            if file_path.suffix == ".csv":
                df = pd.read_csv(file_path, **kwargs)
                self.logger.info(f"Loaded CSV: {filename} - Shape: {df.shape}")
            elif file_path.suffix == ".xlsx":
                if sheet_name is None:
                    # Load all sheets
                    excel_file = pd.ExcelFile(file_path)
                    dfs = {sheet: pd.read_excel(file_path, sheet_name=sheet, **kwargs) 
                           for sheet in excel_file.sheet_names}
                    self.logger.info(f"Loaded Excel: {filename} - Sheets: {list(dfs.keys())}")
                    if use_cache:
                        for sheet, df in dfs.items():
                            self._cache[f"{filename}_{sheet}"] = df
                    return dfs
                else:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
                    self.logger.info(f"Loaded Excel sheet '{sheet_name}': {filename} - Shape: {df.shape}")
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

            if use_cache:
                self._cache[cache_key] = df

            return df

        except Exception as e:
            self.logger.error(f"Error loading {filename}: {str(e)}")
            raise

    def load_unified_data(
        self,
        sheet_name: Optional[Union[str, int, List]] = None,
        use_cache: bool = True
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Load the unified Ethiopia financial inclusion dataset

        Args:
            sheet_name: Sheet name(s) for Excel files
            use_cache: Whether to use cached data

        Returns:
            DataFrame or dict of DataFrames
        """
        return self.load_file(
            config.unified_data_file,
            sheet_name=sheet_name,
            use_cache=use_cache
        )

    def load_reference_codes(
        self,
        sheet_name: Optional[Union[str, int, List]] = None,
        use_cache: bool = True
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Load reference codes dataset

        Args:
            sheet_name: Sheet name(s) for Excel files
            use_cache: Whether to use cached data

        Returns:
            DataFrame or dict of DataFrames
        """
        return self.load_file(
            config.reference_codes_file,
            sheet_name=sheet_name,
            use_cache=use_cache
        )

    def load_additional_guide(
        self,
        sheet_name: Optional[Union[str, int, List]] = None,
        use_cache: bool = True
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Load additional data points guide

        Args:
            sheet_name: Sheet name(s) for Excel files
            use_cache: Whether to use cached data

        Returns:
            DataFrame or dict of DataFrames
        """
        return self.load_file(
            config.additional_data_guide_file,
            sheet_name=sheet_name,
            use_cache=use_cache
        )

    def clear_cache(self):
        """Clear the data cache"""
        self._cache.clear()
        self.logger.info("Cache cleared")
