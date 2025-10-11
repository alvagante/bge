"""
Logging configuration and utilities for the Social Quote Generator.

This module provides centralized logging with both console and file handlers,
supporting multiple log levels and formatted output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class LoggerConfig:
    """Configure and manage application logging."""
    
    def __init__(
        self,
        log_dir: str = "output/logs",
        log_level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True
    ):
        """
        Initialize logger configuration.
        
        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            console_output: Enable console logging
            file_output: Enable file logging
        """
        self.log_dir = Path(log_dir)
        self.log_level = self._parse_log_level(log_level)
        self.console_output = console_output
        self.file_output = file_output
        self.logger = None
        
    def _parse_log_level(self, level: str) -> int:
        """Parse string log level to logging constant."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(level.upper(), logging.INFO)
    
    def setup_logger(self, name: str = "social_quote_generator") -> logging.Logger:
        """
        Set up and configure the logger with handlers.
        
        Args:
            name: Logger name
            
        Returns:
            Configured logger instance
        """
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            fmt='%(levelname)s: %(message)s'
        )
        
        # Add console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler
        if self.file_output:
            self._ensure_log_directory()
            log_file = self._get_log_filename()
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
            
        return self.logger
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_log_filename(self) -> Path:
        """Generate log filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.log_dir / f"social_quote_generator_{timestamp}.log"
    
    def get_logger(self) -> Optional[logging.Logger]:
        """Get the configured logger instance."""
        return self.logger


def get_logger(
    name: str = "social_quote_generator",
    log_dir: str = "output/logs",
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True
) -> logging.Logger:
    """
    Convenience function to get a configured logger.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        console_output: Enable console logging
        file_output: Enable file logging
        
    Returns:
        Configured logger instance
    """
    config = LoggerConfig(
        log_dir=log_dir,
        log_level=log_level,
        console_output=console_output,
        file_output=file_output
    )
    return config.setup_logger(name)
