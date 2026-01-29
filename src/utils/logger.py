"""
Reusable logging utility module
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ProjectLogger:
    """Centralized logging class for the project"""

    _loggers: dict[str, logging.Logger] = {}
    _log_dir: Path = Path("logs")
    _log_dir.mkdir(exist_ok=True)

    @classmethod
    def get_logger(
        cls,
        name: str,
        level: int = logging.INFO,
        log_to_file: bool = True,
        log_to_console: bool = True,
    ) -> logging.Logger:
        """
        Get or create a logger instance

        Args:
            name: Logger name (typically __name__)
            level: Logging level (default: INFO)
            log_to_file: Whether to log to file
            log_to_console: Whether to log to console

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()  # Avoid duplicate handlers

        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File handler
        if log_to_file:
            log_file = cls._log_dir / f"{name.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger


def get_logger(
    name: Optional[str] = None,
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    Convenience function to get a logger

    Args:
        name: Logger name (defaults to calling module's __name__)
        level: Logging level
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console

    Returns:
        Configured logger instance
    """
    if name is None:
        import inspect
        name = inspect.stack()[1].frame.f_globals.get("__name__", "root")

    return ProjectLogger.get_logger(name, level, log_to_file, log_to_console)
