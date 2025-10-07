"""
Input validation and credential verification utilities.

This module provides validation functions for configuration values,
API credentials, file paths, and other inputs to catch errors early.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import logging


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class Validator:
    """
    Validate inputs and configuration values.
    
    Provides early validation to catch configuration and input errors
    before pipeline execution begins.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize validator.
        
        Args:
            logger: Logger instance for validation messages
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_episode_number(self, episode_number: str) -> bool:
        """
        Validate episode number format.
        
        Args:
            episode_number: Episode number to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If episode number is invalid
        """
        if not episode_number:
            raise ValidationError("Episode number cannot be empty")
        
        if not episode_number.isdigit():
            raise ValidationError(f"Episode number must be numeric: {episode_number}")
        
        episode_int = int(episode_number)
        if episode_int <= 0:
            raise ValidationError(f"Episode number must be positive: {episode_number}")
        
        if episode_int > 10000:  # Reasonable upper limit
            raise ValidationError(f"Episode number seems unreasonably large: {episode_number}")
        
        return True
    
    def validate_file_path(self, file_path: str, must_exist: bool = False) -> bool:
        """
        Validate file path and check for directory traversal.
        
        Args:
            file_path: File path to validate
            must_exist: Whether file must exist
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If path is invalid or unsafe
        """
        if not file_path:
            raise ValidationError("File path cannot be empty")
        
        path = Path(file_path)
        
        # Check for directory traversal attempts
        try:
            path.resolve()
        except (ValueError, OSError) as e:
            raise ValidationError(f"Invalid file path: {file_path} - {e}")
        
        # Check if path contains suspicious patterns
        suspicious_patterns = ['..', '~', '$']
        path_str = str(path)
        for pattern in suspicious_patterns:
            if pattern in path_str and pattern != path_str:  # Allow ~ as root
                self.logger.warning(f"File path contains suspicious pattern '{pattern}': {file_path}")
        
        # Check existence if required
        if must_exist and not path.exists():
            raise ValidationError(f"File does not exist: {file_path}")
        
        return True
    
    def validate_directory_path(self, dir_path: str, create_if_missing: bool = False) -> bool:
        """
        Validate directory path.
        
        Args:
            dir_path: Directory path to validate
            create_if_missing: Whether to create directory if it doesn't exist
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If path is invalid
        """
        if not dir_path:
            raise ValidationError("Directory path cannot be empty")
        
        path = Path(dir_path)
        
        if path.exists() and not path.is_dir():
            raise ValidationError(f"Path exists but is not a directory: {dir_path}")
        
        if not path.exists():
            if create_if_missing:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created directory: {dir_path}")
                except OSError as e:
                    raise ValidationError(f"Failed to create directory {dir_path}: {e}")
            else:
                raise ValidationError(f"Directory does not exist: {dir_path}")
        
        return True
    
    def validate_image_dimensions(self, width: int, height: int) -> bool:
        """
        Validate image dimensions.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If dimensions are invalid
        """
        if width <= 0 or height <= 0:
            raise ValidationError(f"Image dimensions must be positive: {width}x{height}")
        
        if width > 10000 or height > 10000:
            raise ValidationError(f"Image dimensions too large: {width}x{height}")
        
        if width < 100 or height < 100:
            self.logger.warning(f"Image dimensions seem small: {width}x{height}")
        
        return True
    
    def validate_color(self, color: str) -> bool:
        """
        Validate color format (hex color code).
        
        Args:
            color: Color string to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If color format is invalid
        """
        if not color:
            raise ValidationError("Color cannot be empty")
        
        # Check hex color format (#RGB or #RRGGBB)
        hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        if not re.match(hex_pattern, color):
            raise ValidationError(f"Invalid color format (expected #RGB or #RRGGBB): {color}")
        
        return True
    
    def validate_platform(self, platform: str, supported_platforms: List[str]) -> bool:
        """
        Validate platform name.
        
        Args:
            platform: Platform name to validate
            supported_platforms: List of supported platform names
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If platform is not supported
        """
        if not platform:
            raise ValidationError("Platform cannot be empty")
        
        if platform not in supported_platforms:
            raise ValidationError(
                f"Unsupported platform: {platform}. "
                f"Supported platforms: {', '.join(supported_platforms)}"
            )
        
        return True
    
    def validate_log_level(self, log_level: str) -> bool:
        """
        Validate log level.
        
        Args:
            log_level: Log level to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If log level is invalid
        """
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        if not log_level:
            raise ValidationError("Log level cannot be empty")
        
        if log_level.upper() not in valid_levels:
            raise ValidationError(
                f"Invalid log level: {log_level}. "
                f"Valid levels: {', '.join(valid_levels)}"
            )
        
        return True
    
    def validate_twitter_credentials(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate Twitter API credentials.
        
        Args:
            config: Configuration dictionary with Twitter credentials
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = [
            'api_key',
            'api_secret',
            'access_token',
            'access_token_secret'
        ]
        
        missing_fields = []
        for field in required_fields:
            value = config.get(field, '').strip()
            if not value or value.startswith('${'):
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = (
                f"Missing or invalid Twitter credentials: {', '.join(missing_fields)}. "
                "Please set the following environment variables: "
                f"{', '.join([f'TWITTER_{f.upper()}' for f in missing_fields])}"
            )
            return False, error_msg
        
        return True, None
    
    def validate_instagram_credentials(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate Instagram credentials.
        
        Args:
            config: Configuration dictionary with Instagram credentials
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['username', 'password']
        
        missing_fields = []
        for field in required_fields:
            value = config.get(field, '').strip()
            if not value or value.startswith('${'):
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = (
                f"Missing or invalid Instagram credentials: {', '.join(missing_fields)}. "
                "Please set the following environment variables: "
                f"{', '.join([f'INSTAGRAM_{f.upper()}' for f in missing_fields])}"
            )
            return False, error_msg
        
        return True, None
    
    def validate_facebook_credentials(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate Facebook credentials.
        
        Args:
            config: Configuration dictionary with Facebook credentials
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['access_token']
        
        missing_fields = []
        for field in required_fields:
            value = config.get(field, '').strip()
            if not value or value.startswith('${'):
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = (
                f"Missing or invalid Facebook credentials: {', '.join(missing_fields)}. "
                "Please set FACEBOOK_ACCESS_TOKEN environment variable"
            )
            return False, error_msg
        
        return True, None
    
    def validate_api_credentials(
        self,
        platform: str,
        config: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate API credentials for a specific platform.
        
        Args:
            platform: Platform name (twitter, instagram, facebook, linkedin)
            config: Configuration dictionary with credentials
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        validators = {
            'twitter': self.validate_twitter_credentials,
            'instagram': self.validate_instagram_credentials,
            'facebook': self.validate_facebook_credentials,
        }
        
        validator_func = validators.get(platform)
        if not validator_func:
            return True, None  # No validator for this platform
        
        return validator_func(config)
    
    def validate_text_length(self, text: str, max_length: int, field_name: str = "text") -> bool:
        """
        Validate text length.
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            field_name: Name of field for error messages
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If text is too long
        """
        if len(text) > max_length:
            raise ValidationError(
                f"{field_name} exceeds maximum length of {max_length} characters "
                f"(current: {len(text)})"
            )
        
        return True
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text for safe rendering.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
