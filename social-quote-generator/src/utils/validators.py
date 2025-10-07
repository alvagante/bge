"""Input validation and security utilities for BGE Social Quote Generator."""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

import html


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class EpisodeValidator:
    """Validates episode numbers and episode-related inputs."""
    
    @staticmethod
    def validate_episode_number(episode_number: str) -> str:
        """
        Validate episode number format and value.
        
        Args:
            episode_number: Episode number to validate
            
        Returns:
            Validated episode number as string
            
        Raises:
            ValidationError: If episode number is invalid
        """
        # Check if empty
        if not episode_number or not episode_number.strip():
            raise ValidationError("Episode number cannot be empty")
        
        episode_number = episode_number.strip()
        
        # Check if numeric
        if not episode_number.isdigit():
            raise ValidationError(
                f"Episode number must be numeric, got: {episode_number}"
            )
        
        # Convert to int to check range
        episode_int = int(episode_number)
        
        # Check if positive
        if episode_int <= 0:
            raise ValidationError(
                f"Episode number must be positive, got: {episode_int}"
            )
        
        # Check reasonable upper bound (prevent DoS with huge numbers)
        if episode_int > 10000:
            raise ValidationError(
                f"Episode number too large (max 10000), got: {episode_int}"
            )
        
        return episode_number
    
    @staticmethod
    def validate_episode_list(episode_numbers: List[str]) -> List[str]:
        """
        Validate a list of episode numbers.
        
        Args:
            episode_numbers: List of episode numbers to validate
            
        Returns:
            List of validated episode numbers
            
        Raises:
            ValidationError: If any episode number is invalid
        """
        if not episode_numbers:
            raise ValidationError("Episode list cannot be empty")
        
        validated = []
        for episode_num in episode_numbers:
            validated.append(EpisodeValidator.validate_episode_number(episode_num))
        
        return validated
    
    @staticmethod
    def check_episode_exists(episode_number: str, episodes_dir: str) -> bool:
        """
        Check if an episode file exists.
        
        Args:
            episode_number: Episode number to check
            episodes_dir: Directory containing episode files
            
        Returns:
            True if episode file exists, False otherwise
        """
        # Validate episode number first
        episode_number = EpisodeValidator.validate_episode_number(episode_number)
        
        # Validate directory path
        episodes_path = PathValidator.validate_directory_path(episodes_dir)
        
        # Check if episode file exists
        episode_file = episodes_path / f"{episode_number}.md"
        return episode_file.exists()


class PathValidator:
    """Validates file and directory paths to prevent security issues."""
    
    @staticmethod
    def validate_path(path: str, description: str = "path") -> Path:
        """
        Validate a file or directory path to prevent directory traversal attacks.
        
        Args:
            path: Path to validate
            description: Description of the path for error messages
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If path is invalid or contains security issues
        """
        if not path or not path.strip():
            raise ValidationError(f"{description} cannot be empty")
        
        path = path.strip()
        
        # Check for directory traversal attempts
        if ".." in path:
            raise ValidationError(
                f"Invalid {description}: {path} (contains '..' - directory traversal not allowed)"
            )
        
        # Check for absolute paths (we want relative paths only)
        if os.path.isabs(path):
            raise ValidationError(
                f"Invalid {description}: {path} (absolute paths not allowed, use relative paths)"
            )
        
        # Check for null bytes (security issue)
        if "\x00" in path:
            raise ValidationError(
                f"Invalid {description}: path contains null bytes"
            )
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r"\.\.[\\/]",  # ../ or ..\
            r"[\\/]\.\.[\\/]",  # /../ or \..\
            r"[\\/]\.\.$",  # /.. or \..
            r"^\.\.[\\/]",  # ../ or ..\ at start
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, path):
                raise ValidationError(
                    f"Invalid {description}: {path} (suspicious path pattern detected)"
                )
        
        # Convert to Path object
        try:
            path_obj = Path(path)
        except Exception as e:
            raise ValidationError(f"Invalid {description}: {path} ({e})")
        
        # Resolve to absolute path and check it's within allowed boundaries
        # This prevents symlink attacks
        try:
            resolved = path_obj.resolve()
            cwd = Path.cwd().resolve()
            
            # Check if resolved path is within current working directory
            try:
                resolved.relative_to(cwd)
            except ValueError:
                raise ValidationError(
                    f"Invalid {description}: {path} (resolves outside working directory)"
                )
        except Exception as e:
            # If we can't resolve, that's okay - file might not exist yet
            pass
        
        return path_obj
    
    @staticmethod
    def validate_file_path(path: str, description: str = "file") -> Path:
        """
        Validate a file path.
        
        Args:
            path: File path to validate
            description: Description of the file for error messages
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If path is invalid
        """
        path_obj = PathValidator.validate_path(path, description)
        
        # Additional file-specific validation
        if path_obj.exists() and not path_obj.is_file():
            raise ValidationError(
                f"Invalid {description}: {path} (exists but is not a file)"
            )
        
        return path_obj
    
    @staticmethod
    def validate_directory_path(path: str, description: str = "directory") -> Path:
        """
        Validate a directory path.
        
        Args:
            path: Directory path to validate
            description: Description of the directory for error messages
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If path is invalid
        """
        path_obj = PathValidator.validate_path(path, description)
        
        # Additional directory-specific validation
        if path_obj.exists() and not path_obj.is_dir():
            raise ValidationError(
                f"Invalid {description}: {path} (exists but is not a directory)"
            )
        
        return path_obj
    
    @staticmethod
    def validate_output_path(path: str, description: str = "output file") -> Path:
        """
        Validate an output file path (file that will be created).
        
        Args:
            path: Output file path to validate
            description: Description of the output file for error messages
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If path is invalid
        """
        path_obj = PathValidator.validate_path(path, description)
        
        # Check parent directory exists or can be created
        parent = path_obj.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValidationError(
                    f"Cannot create parent directory for {description}: {parent} ({e})"
                )
        
        return path_obj


class ConfigValidator:
    """Validates configuration values."""
    
    @staticmethod
    def validate_dimensions(dimensions: Tuple[int, int], description: str = "dimensions") -> Tuple[int, int]:
        """
        Validate image dimensions.
        
        Args:
            dimensions: Tuple of (width, height)
            description: Description for error messages
            
        Returns:
            Validated dimensions tuple
            
        Raises:
            ValidationError: If dimensions are invalid
        """
        if not isinstance(dimensions, (tuple, list)) or len(dimensions) != 2:
            raise ValidationError(
                f"Invalid {description}: must be a tuple/list of [width, height]"
            )
        
        width, height = dimensions
        
        # Check if numeric
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValidationError(
                f"Invalid {description}: width and height must be integers"
            )
        
        # Check if positive
        if width <= 0 or height <= 0:
            raise ValidationError(
                f"Invalid {description}: width and height must be positive"
            )
        
        # Check reasonable bounds (prevent memory exhaustion)
        max_dimension = 10000
        if width > max_dimension or height > max_dimension:
            raise ValidationError(
                f"Invalid {description}: dimensions too large (max {max_dimension}x{max_dimension})"
            )
        
        # Check minimum size
        min_dimension = 100
        if width < min_dimension or height < min_dimension:
            raise ValidationError(
                f"Invalid {description}: dimensions too small (min {min_dimension}x{min_dimension})"
            )
        
        return (width, height)
    
    @staticmethod
    def validate_color(color: str, description: str = "color") -> str:
        """
        Validate hex color code.
        
        Args:
            color: Hex color code (e.g., #FFFFFF)
            description: Description for error messages
            
        Returns:
            Validated color string
            
        Raises:
            ValidationError: If color is invalid
        """
        if not color or not isinstance(color, str):
            raise ValidationError(f"Invalid {description}: must be a non-empty string")
        
        color = color.strip()
        
        # Check hex color format
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        if not hex_pattern.match(color):
            raise ValidationError(
                f"Invalid {description}: {color} (must be hex color like #FFFFFF)"
            )
        
        return color
    
    @staticmethod
    def validate_font_size(size: int, description: str = "font size") -> int:
        """
        Validate font size.
        
        Args:
            size: Font size in points
            description: Description for error messages
            
        Returns:
            Validated font size
            
        Raises:
            ValidationError: If font size is invalid
        """
        if not isinstance(size, int):
            raise ValidationError(f"Invalid {description}: must be an integer")
        
        if size <= 0:
            raise ValidationError(f"Invalid {description}: must be positive")
        
        # Check reasonable bounds
        if size > 500:
            raise ValidationError(
                f"Invalid {description}: too large (max 500)"
            )
        
        if size < 8:
            raise ValidationError(
                f"Invalid {description}: too small (min 8)"
            )
        
        return size
    
    @staticmethod
    def validate_platform(platform: str) -> str:
        """
        Validate social media platform name.
        
        Args:
            platform: Platform name
            
        Returns:
            Validated platform name
            
        Raises:
            ValidationError: If platform is invalid
        """
        if not platform or not isinstance(platform, str):
            raise ValidationError("Platform name must be a non-empty string")
        
        platform = platform.strip().lower()
        
        valid_platforms = ["twitter", "instagram", "facebook", "linkedin"]
        if platform not in valid_platforms:
            raise ValidationError(
                f"Invalid platform: {platform}. Must be one of: {', '.join(valid_platforms)}"
            )
        
        return platform
    
    @staticmethod
    def validate_quote_source(source: str) -> str:
        """
        Validate quote source name.
        
        Args:
            source: Quote source name
            
        Returns:
            Validated source name
            
        Raises:
            ValidationError: If source is invalid
        """
        if not source or not isinstance(source, str):
            raise ValidationError("Quote source must be a non-empty string")
        
        source = source.strip().lower()
        
        valid_sources = ["claude", "openai", "deepseek", "llama", "random"]
        if source not in valid_sources:
            raise ValidationError(
                f"Invalid quote source: {source}. Must be one of: {', '.join(valid_sources)}"
            )
        
        return source


class TextValidator:
    """Validates and sanitizes text content."""
    
    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text for safe rendering.
        
        Removes potentially dangerous characters and HTML entities.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length (None = no limit)
            
        Returns:
            Sanitized text
            
        Raises:
            ValidationError: If text is invalid
        """
        if not isinstance(text, str):
            raise ValidationError("Text must be a string")
        
        # Remove null bytes
        text = text.replace("\x00", "")
        
        # Escape HTML entities to prevent injection
        text = html.escape(text)
        
        # Remove control characters except newlines and tabs
        text = "".join(
            char for char in text 
            if char == "\n" or char == "\t" or (ord(char) >= 32 and ord(char) != 127)
        )
        
        # Normalize whitespace
        text = " ".join(text.split())
        
        # Check length
        if max_length and len(text) > max_length:
            raise ValidationError(
                f"Text too long: {len(text)} characters (max {max_length})"
            )
        
        return text
    
    @staticmethod
    def validate_quote(quote: str, max_length: int = 500) -> str:
        """
        Validate and sanitize a quote.
        
        Args:
            quote: Quote text to validate
            max_length: Maximum allowed length
            
        Returns:
            Validated and sanitized quote
            
        Raises:
            ValidationError: If quote is invalid
        """
        if not quote or not quote.strip():
            raise ValidationError("Quote cannot be empty")
        
        # Sanitize
        quote = TextValidator.sanitize_text(quote, max_length)
        
        # Check minimum length
        if len(quote) < 10:
            raise ValidationError("Quote too short (minimum 10 characters)")
        
        return quote
    
    @staticmethod
    def validate_caption(caption: str, max_length: int = 2200) -> str:
        """
        Validate and sanitize a social media caption.
        
        Args:
            caption: Caption text to validate
            max_length: Maximum allowed length (Twitter: 280, Instagram: 2200)
            
        Returns:
            Validated and sanitized caption
            
        Raises:
            ValidationError: If caption is invalid
        """
        if not caption or not caption.strip():
            raise ValidationError("Caption cannot be empty")
        
        # Sanitize (but preserve newlines for formatting)
        caption = caption.strip()
        
        # Remove null bytes
        caption = caption.replace("\x00", "")
        
        # Check length
        if len(caption) > max_length:
            raise ValidationError(
                f"Caption too long: {len(caption)} characters (max {max_length})"
            )
        
        return caption


class CredentialValidator:
    """Validates API credentials."""
    
    @staticmethod
    def validate_credential(
        credential: str, 
        name: str, 
        allow_empty: bool = False
    ) -> Optional[str]:
        """
        Validate an API credential.
        
        Args:
            credential: Credential value
            name: Credential name for error messages
            allow_empty: Whether empty credentials are allowed
            
        Returns:
            Validated credential or None if empty and allowed
            
        Raises:
            ValidationError: If credential is invalid
        """
        if not credential or not credential.strip():
            if allow_empty:
                return None
            raise ValidationError(f"{name} cannot be empty")
        
        credential = credential.strip()
        
        # Check for placeholder values
        placeholder_patterns = [
            r'^\$\{.*\}$',  # ${VAR_NAME}
            r'^your_',  # your_api_key
            r'^<.*>$',  # <your_key>
            r'^\[.*\]$',  # [your_key]
            r'^xxx',  # xxx...
            r'^placeholder',  # placeholder
            r'^example',  # example
        ]
        
        for pattern in placeholder_patterns:
            if re.match(pattern, credential, re.IGNORECASE):
                raise ValidationError(
                    f"{name} appears to be a placeholder: {credential}"
                )
        
        # Check for suspicious characters
        if "\x00" in credential:
            raise ValidationError(f"{name} contains null bytes")
        
        # Check minimum length (most API keys are at least 10 chars)
        if len(credential) < 10:
            raise ValidationError(
                f"{name} too short (minimum 10 characters)"
            )
        
        return credential
    
    @staticmethod
    def validate_twitter_credentials(
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str
    ) -> Tuple[str, str, str, str]:
        """
        Validate Twitter API credentials.
        
        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
            
        Returns:
            Tuple of validated credentials
            
        Raises:
            ValidationError: If any credential is invalid
        """
        return (
            CredentialValidator.validate_credential(api_key, "Twitter API key"),
            CredentialValidator.validate_credential(api_secret, "Twitter API secret"),
            CredentialValidator.validate_credential(access_token, "Twitter access token"),
            CredentialValidator.validate_credential(access_token_secret, "Twitter access token secret")
        )
    
    @staticmethod
    def validate_instagram_credentials(
        username: str,
        password: str
    ) -> Tuple[str, str]:
        """
        Validate Instagram credentials.
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            Tuple of validated credentials
            
        Raises:
            ValidationError: If any credential is invalid
        """
        if not username or not username.strip():
            raise ValidationError("Instagram username cannot be empty")
        
        username = username.strip()
        
        # Basic username validation
        if not re.match(r'^[a-zA-Z0-9._]+$', username):
            raise ValidationError(
                "Instagram username can only contain letters, numbers, dots, and underscores"
            )
        
        if len(username) > 30:
            raise ValidationError("Instagram username too long (max 30 characters)")
        
        password = CredentialValidator.validate_credential(password, "Instagram password")
        
        return (username, password)


class RateLimitValidator:
    """Validates rate limiting constraints."""
    
    @staticmethod
    def check_rate_limit(
        platform: str,
        posts_count: int,
        time_window_hours: int = 24
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if posting would exceed platform rate limits.
        
        Args:
            platform: Platform name
            posts_count: Number of posts in the time window
            time_window_hours: Time window in hours
            
        Returns:
            Tuple of (is_allowed, warning_message)
        """
        # Platform-specific rate limits (conservative estimates)
        rate_limits = {
            "twitter": 300,  # 300 tweets per 3 hours
            "instagram": 100,  # ~100 posts per day
            "facebook": 200,  # 200 posts per day
            "linkedin": 100,  # 100 posts per day
        }
        
        limit = rate_limits.get(platform, 100)
        
        # Adjust limit based on time window
        if time_window_hours != 24:
            limit = int(limit * (time_window_hours / 24))
        
        if posts_count >= limit:
            return (
                False,
                f"Rate limit exceeded for {platform}: {posts_count}/{limit} posts in {time_window_hours}h"
            )
        
        # Warn if approaching limit (80%)
        if posts_count >= limit * 0.8:
            return (
                True,
                f"Approaching rate limit for {platform}: {posts_count}/{limit} posts in {time_window_hours}h"
            )
        
        return (True, None)
