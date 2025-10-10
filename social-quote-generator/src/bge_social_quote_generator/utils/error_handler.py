"""
Error handling utilities for the Social Quote Generator.

This module provides error collection, categorization, and reporting
to enable graceful error recovery and comprehensive error summaries.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ErrorCategory(Enum):
    """Categories of errors that can occur during pipeline execution."""
    CONFIGURATION = "configuration"
    EXTRACTION = "extraction"
    GENERATION = "generation"
    PUBLISHING = "publishing"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    FATAL = "fatal"      # Stops execution
    ERROR = "error"      # Logged but execution continues
    WARNING = "warning"  # Minor issue, execution continues
    INFO = "info"        # Informational message


@dataclass
class ErrorRecord:
    """Record of a single error occurrence."""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    episode_number: Optional[str] = None
    platform: Optional[str] = None
    exception: Optional[Exception] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error record to dictionary."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "episode_number": self.episode_number,
            "platform": self.platform,
            "exception": str(self.exception) if self.exception else None,
            "context": self.context
        }


class ErrorHandler:
    """
    Collect, categorize, and report errors during pipeline execution.
    
    This class enables graceful error recovery by collecting errors
    without stopping execution, then providing comprehensive summaries.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler.
        
        Args:
            logger: Logger instance for error logging
        """
        self.logger = logger or logging.getLogger(__name__)
        self.errors: List[ErrorRecord] = []
        self._fatal_error_occurred = False
    
    def handle_configuration_error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle configuration-related errors.
        
        Args:
            message: Error message
            exception: Optional exception object
            severity: Error severity level
            context: Additional context information
        """
        self._record_error(
            category=ErrorCategory.CONFIGURATION,
            severity=severity,
            message=message,
            exception=exception,
            context=context or {}
        )
    
    def handle_extraction_error(
        self,
        episode_number: str,
        message: str,
        exception: Optional[Exception] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle quote extraction errors.
        
        Args:
            episode_number: Episode number being processed
            message: Error message
            exception: Optional exception object
            severity: Error severity level
            context: Additional context information
        """
        self._record_error(
            category=ErrorCategory.EXTRACTION,
            severity=severity,
            message=message,
            episode_number=episode_number,
            exception=exception,
            context=context or {}
        )
    
    def handle_generation_error(
        self,
        episode_number: str,
        platform: str,
        message: str,
        exception: Optional[Exception] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle image generation errors.
        
        Args:
            episode_number: Episode number being processed
            platform: Target platform (instagram, twitter, etc.)
            message: Error message
            exception: Optional exception object
            severity: Error severity level
            context: Additional context information
        """
        self._record_error(
            category=ErrorCategory.GENERATION,
            severity=severity,
            message=message,
            episode_number=episode_number,
            platform=platform,
            exception=exception,
            context=context or {}
        )
    
    def handle_publishing_error(
        self,
        episode_number: str,
        platform: str,
        message: str,
        exception: Optional[Exception] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle social media publishing errors.
        
        Args:
            episode_number: Episode number being processed
            platform: Target platform (instagram, twitter, etc.)
            message: Error message
            exception: Optional exception object
            severity: Error severity level
            context: Additional context information
        """
        self._record_error(
            category=ErrorCategory.PUBLISHING,
            severity=severity,
            message=message,
            episode_number=episode_number,
            platform=platform,
            exception=exception,
            context=context or {}
        )
    
    def handle_validation_error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle validation errors.
        
        Args:
            message: Error message
            exception: Optional exception object
            severity: Error severity level
            context: Additional context information
        """
        self._record_error(
            category=ErrorCategory.VALIDATION,
            severity=severity,
            message=message,
            exception=exception,
            context=context or {}
        )
    
    def handle_authentication_error(
        self,
        platform: str,
        message: str,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle authentication errors.
        
        Args:
            platform: Platform where authentication failed
            message: Error message
            exception: Optional exception object
            context: Additional context information
        """
        self._record_error(
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.FATAL,
            message=message,
            platform=platform,
            exception=exception,
            context=context or {}
        )
    
    def handle_network_error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle network-related errors.
        
        Args:
            message: Error message
            exception: Optional exception object
            severity: Error severity level
            context: Additional context information
        """
        self._record_error(
            category=ErrorCategory.NETWORK,
            severity=severity,
            message=message,
            exception=exception,
            context=context or {}
        )
    
    def handle_file_system_error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Handle file system errors.
        
        Args:
            message: Error message
            exception: Optional exception object
            severity: Error severity level
            context: Additional context information
        """
        self._record_error(
            category=ErrorCategory.FILE_SYSTEM,
            severity=severity,
            message=message,
            exception=exception,
            context=context or {}
        )
    
    def _record_error(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        message: str,
        episode_number: Optional[str] = None,
        platform: Optional[str] = None,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Record an error and log it appropriately.
        
        Args:
            category: Error category
            severity: Error severity
            message: Error message
            episode_number: Optional episode number
            platform: Optional platform name
            exception: Optional exception object
            context: Optional context dictionary
        """
        error_record = ErrorRecord(
            category=category,
            severity=severity,
            message=message,
            episode_number=episode_number,
            platform=platform,
            exception=exception,
            context=context or {}
        )
        
        self.errors.append(error_record)
        
        # Mark fatal errors
        if severity == ErrorSeverity.FATAL:
            self._fatal_error_occurred = True
        
        # Log the error
        self._log_error(error_record)
    
    def _log_error(self, error: ErrorRecord):
        """Log an error record at the appropriate level."""
        log_message = self._format_log_message(error)
        
        if error.severity == ErrorSeverity.FATAL:
            self.logger.critical(log_message)
        elif error.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message)
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _format_log_message(self, error: ErrorRecord) -> str:
        """Format error record for logging."""
        parts = [f"[{error.category.value.upper()}]"]
        
        if error.episode_number:
            parts.append(f"Episode {error.episode_number}")
        
        if error.platform:
            parts.append(f"Platform: {error.platform}")
        
        parts.append(error.message)
        
        if error.exception:
            parts.append(f"Exception: {type(error.exception).__name__}: {str(error.exception)}")
        
        return " - ".join(parts)
    
    def has_errors(self) -> bool:
        """Check if any errors have been recorded."""
        return len(self.errors) > 0
    
    def has_fatal_errors(self) -> bool:
        """Check if any fatal errors have been recorded."""
        return self._fatal_error_occurred
    
    def get_error_count(self) -> int:
        """Get total number of errors."""
        return len(self.errors)
    
    def get_errors_by_category(self) -> Dict[str, List[ErrorRecord]]:
        """Group errors by category."""
        categorized = {}
        for error in self.errors:
            category = error.category.value
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(error)
        return categorized
    
    def get_errors_by_severity(self) -> Dict[str, List[ErrorRecord]]:
        """Group errors by severity."""
        by_severity = {}
        for error in self.errors:
            severity = error.severity.value
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(error)
        return by_severity
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive error summary.
        
        Returns:
            Dictionary containing error statistics and details
        """
        by_category = self.get_errors_by_category()
        by_severity = self.get_errors_by_severity()
        
        return {
            "total_errors": len(self.errors),
            "has_fatal_errors": self._fatal_error_occurred,
            "by_category": {
                category: len(errors)
                for category, errors in by_category.items()
            },
            "by_severity": {
                severity: len(errors)
                for severity, errors in by_severity.items()
            },
            "details": [error.to_dict() for error in self.errors]
        }
    
    def print_summary(self):
        """Print a human-readable error summary."""
        if not self.has_errors():
            self.logger.info("No errors occurred during execution.")
            return
        
        summary = self.get_summary()
        
        self.logger.info("=" * 60)
        self.logger.info("ERROR SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Errors: {summary['total_errors']}")
        
        if summary['has_fatal_errors']:
            self.logger.critical("FATAL ERRORS OCCURRED - Execution may be incomplete")
        
        self.logger.info("\nErrors by Category:")
        for category, count in summary['by_category'].items():
            self.logger.info(f"  {category}: {count}")
        
        self.logger.info("\nErrors by Severity:")
        for severity, count in summary['by_severity'].items():
            self.logger.info(f"  {severity}: {count}")
        
        self.logger.info("=" * 60)
    
    def clear_errors(self):
        """Clear all recorded errors."""
        self.errors.clear()
        self._fatal_error_occurred = False
