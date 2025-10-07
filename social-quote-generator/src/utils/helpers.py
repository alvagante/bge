"""
Helper utilities for common operations.

This module provides convenience functions that combine multiple
utility components for common use cases.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from .logger import get_logger
from .error_handler import ErrorHandler, ErrorSeverity
from .summary_reporter import SummaryReporter, EpisodeResult
from .validators import Validator, ValidationError


def setup_pipeline_utilities(
    log_dir: str = "output/logs",
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True
) -> Tuple[logging.Logger, ErrorHandler, SummaryReporter, Validator]:
    """
    Set up all pipeline utilities in one call.
    
    This convenience function initializes logger, error handler,
    summary reporter, and validator with consistent configuration.
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        console_output: Enable console logging
        file_output: Enable file logging
        
    Returns:
        Tuple of (logger, error_handler, summary_reporter, validator)
    """
    # Set up logger
    logger = get_logger(
        log_dir=log_dir,
        log_level=log_level,
        console_output=console_output,
        file_output=file_output
    )
    
    # Initialize other utilities with the logger
    error_handler = ErrorHandler(logger)
    summary_reporter = SummaryReporter(logger)
    validator = Validator(logger)
    
    logger.info("Pipeline utilities initialized")
    
    return logger, error_handler, summary_reporter, validator


def validate_configuration(
    config: Dict[str, Any],
    validator: Validator,
    error_handler: ErrorHandler
) -> bool:
    """
    Validate configuration with comprehensive error reporting.
    
    Args:
        config: Configuration dictionary to validate
        validator: Validator instance
        error_handler: Error handler instance
        
    Returns:
        True if configuration is valid, False otherwise
    """
    is_valid = True
    
    # Validate general settings
    try:
        if 'general' in config:
            general = config['general']
            
            # Validate directories
            for dir_key in ['episodes_dir', 'texts_dir', 'output_dir', 'log_dir']:
                if dir_key in general:
                    try:
                        validator.validate_directory_path(
                            general[dir_key],
                            create_if_missing=(dir_key in ['output_dir', 'log_dir'])
                        )
                    except ValidationError as e:
                        error_handler.handle_configuration_error(
                            f"Invalid {dir_key}: {e}",
                            exception=e,
                            severity=ErrorSeverity.ERROR
                        )
                        is_valid = False
            
            # Validate log level
            if 'log_level' in general:
                try:
                    validator.validate_log_level(general['log_level'])
                except ValidationError as e:
                    error_handler.handle_configuration_error(
                        f"Invalid log level: {e}",
                        exception=e,
                        severity=ErrorSeverity.WARNING
                    )
    except Exception as e:
        error_handler.handle_configuration_error(
            f"Error validating general configuration: {e}",
            exception=e
        )
        is_valid = False
    
    # Validate image settings
    try:
        if 'images' in config and 'platforms' in config['images']:
            platforms = config['images']['platforms']
            for platform_name, platform_config in platforms.items():
                if 'dimensions' in platform_config:
                    dims = platform_config['dimensions']
                    if len(dims) == 2:
                        try:
                            validator.validate_image_dimensions(dims[0], dims[1])
                        except ValidationError as e:
                            error_handler.handle_configuration_error(
                                f"Invalid dimensions for {platform_name}: {e}",
                                exception=e,
                                severity=ErrorSeverity.WARNING
                            )
        
        # Validate colors
        if 'images' in config and 'branding' in config['images']:
            branding = config['images']['branding']
            for color_key in ['primary_color', 'secondary_color', 'background_color']:
                if color_key in branding:
                    try:
                        validator.validate_color(branding[color_key])
                    except ValidationError as e:
                        error_handler.handle_configuration_error(
                            f"Invalid {color_key}: {e}",
                            exception=e,
                            severity=ErrorSeverity.WARNING
                        )
    except Exception as e:
        error_handler.handle_configuration_error(
            f"Error validating image configuration: {e}",
            exception=e
        )
        is_valid = False
    
    return is_valid


def validate_platform_credentials(
    platform: str,
    config: Dict[str, Any],
    validator: Validator,
    error_handler: ErrorHandler
) -> bool:
    """
    Validate API credentials for a specific platform.
    
    Args:
        platform: Platform name (twitter, instagram, facebook, linkedin)
        config: Platform configuration dictionary
        validator: Validator instance
        error_handler: Error handler instance
        
    Returns:
        True if credentials are valid, False otherwise
    """
    is_valid, error_message = validator.validate_api_credentials(platform, config)
    
    if not is_valid:
        error_handler.handle_authentication_error(
            platform=platform,
            message=error_message or f"Invalid credentials for {platform}",
            context={'config_keys': list(config.keys())}
        )
    
    return is_valid


def create_episode_result(
    episode_number: str,
    success: bool,
    images_generated: int = 0,
    images_failed: int = 0,
    posts_published: int = 0,
    posts_failed: int = 0,
    platforms: Optional[list] = None,
    errors: Optional[list] = None
) -> EpisodeResult:
    """
    Create an episode result with default values.
    
    Args:
        episode_number: Episode number
        success: Whether processing was successful
        images_generated: Number of images generated
        images_failed: Number of failed image generations
        posts_published: Number of posts published
        posts_failed: Number of failed posts
        platforms: List of platforms processed
        errors: List of error messages
        
    Returns:
        EpisodeResult instance
    """
    return EpisodeResult(
        episode_number=episode_number,
        success=success,
        images_generated=images_generated,
        images_failed=images_failed,
        posts_published=posts_published,
        posts_failed=posts_failed,
        platforms=platforms or [],
        errors=errors or []
    )


def ensure_output_directories(
    output_dir: str,
    log_dir: str,
    logger: Optional[logging.Logger] = None
) -> bool:
    """
    Ensure output and log directories exist.
    
    Args:
        output_dir: Output directory path
        log_dir: Log directory path
        logger: Optional logger instance
        
    Returns:
        True if directories exist or were created successfully
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directories ensured: {output_dir}, {log_dir}")
        return True
    except OSError as e:
        logger.error(f"Failed to create output directories: {e}")
        return False


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
