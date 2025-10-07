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
from .validators import ValidationError


def setup_pipeline_utilities(
    log_dir: str = "output/logs",
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True
) -> Tuple[logging.Logger, ErrorHandler, SummaryReporter]:
    """
    Set up all pipeline utilities in one call.
    
    This convenience function initializes logger, error handler,
    and summary reporter with consistent configuration.
    
    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        console_output: Enable console logging
        file_output: Enable file logging
        
    Returns:
        Tuple of (logger, error_handler, summary_reporter)
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
    
    logger.info("Pipeline utilities initialized")
    
    return logger, error_handler, summary_reporter


def validate_configuration(
    config: Dict[str, Any],
    error_handler: ErrorHandler
) -> bool:
    """
    Validate configuration with comprehensive error reporting.
    
    Note: This function is deprecated. Use Config.validate() instead.
    
    Args:
        config: Configuration dictionary to validate
        error_handler: Error handler instance
        
    Returns:
        True if configuration is valid, False otherwise
    """
    # This function is now deprecated as validation is handled by Config class
    # Keeping it for backward compatibility
    return True


def _deprecated_validate_configuration(
    config: Dict[str, Any],
    error_handler: ErrorHandler
) -> bool:
    """
    Legacy validation function (deprecated).
    
    Args:
        config: Configuration dictionary to validate
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
                        from .validators import PathValidator
                        PathValidator.validate_directory_path(general[dir_key], dir_key)
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
                    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
                    if general['log_level'] not in valid_levels:
                        raise ValidationError(f"Invalid log level: {general['log_level']}")
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
    error_handler: ErrorHandler
) -> bool:
    """
    Validate API credentials for a specific platform.
    
    Note: This function is deprecated. Use CredentialValidator directly.
    
    Args:
        platform: Platform name (twitter, instagram, facebook, linkedin)
        config: Platform configuration dictionary
        error_handler: Error handler instance
        
    Returns:
        True if credentials are valid, False otherwise
    """
    from .validators import CredentialValidator
    
    try:
        # Validate based on platform
        if platform == "twitter":
            CredentialValidator.validate_twitter_credentials(
                config.get("api_key", ""),
                config.get("api_secret", ""),
                config.get("access_token", ""),
                config.get("access_token_secret", "")
            )
        elif platform == "instagram":
            CredentialValidator.validate_instagram_credentials(
                config.get("username", ""),
                config.get("password", "")
            )
        else:
            # For other platforms, just check if credentials exist
            for key, value in config.items():
                CredentialValidator.validate_credential(value, f"{platform}.{key}")
        
        return True
        
    except ValidationError as e:
        error_handler.handle_authentication_error(
            platform=platform,
            message=str(e),
            context={'config_keys': list(config.keys())}
        )
        return False


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
