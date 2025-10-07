"""
Utility modules for the Social Quote Generator.

This package provides logging, error handling, validation, and reporting utilities.
"""

from .logger import LoggerConfig, get_logger
from .error_handler import (
    ErrorHandler,
    ErrorCategory,
    ErrorSeverity,
    ErrorRecord
)
from .summary_reporter import (
    SummaryReporter,
    PipelineSummary,
    EpisodeResult
)
from .validators import (
    EpisodeValidator,
    PathValidator,
    ConfigValidator,
    TextValidator,
    CredentialValidator,
    RateLimitValidator,
    ValidationError
)
from .helpers import (
    setup_pipeline_utilities,
    validate_configuration,
    validate_platform_credentials,
    create_episode_result,
    ensure_output_directories,
    format_duration
)

__all__ = [
    # Logger
    'LoggerConfig',
    'get_logger',
    
    # Error handling
    'ErrorHandler',
    'ErrorCategory',
    'ErrorSeverity',
    'ErrorRecord',
    
    # Summary reporting
    'SummaryReporter',
    'PipelineSummary',
    'EpisodeResult',
    
    # Validation
    'EpisodeValidator',
    'PathValidator',
    'ConfigValidator',
    'TextValidator',
    'CredentialValidator',
    'RateLimitValidator',
    'ValidationError',
    
    # Helpers
    'setup_pipeline_utilities',
    'validate_configuration',
    'validate_platform_credentials',
    'create_episode_result',
    'ensure_output_directories',
    'format_duration',
]
