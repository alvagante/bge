"""Configuration management for BGE Social Quote Generator."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from dotenv import load_dotenv


@dataclass
class ImageSettings:
    """Image generation settings."""
    
    templates_dir: str
    fonts_dir: str
    default_font: str
    platforms: Dict[str, Dict[str, Any]]
    branding: Dict[str, Any]
    text: Dict[str, Any]
    
    def get_platform_dimensions(self, platform: str) -> Tuple[int, int]:
        """Get dimensions for a specific platform."""
        if platform not in self.platforms:
            raise ValueError(f"Unknown platform: {platform}")
        dims = self.platforms[platform]["dimensions"]
        return tuple(dims)
    
    def get_platform_template(self, platform: str) -> Optional[str]:
        """Get template path for a specific platform."""
        if platform not in self.platforms:
            raise ValueError(f"Unknown platform: {platform}")
        template = self.platforms[platform].get("template")
        if template:
            return os.path.join(self.templates_dir, template)
        return None
    
    @property
    def logo_path(self) -> str:
        """Get logo file path."""
        return self.branding["logo_path"]
    
    @property
    def logo_position(self) -> str:
        """Get logo position."""
        return self.branding["logo_position"]
    
    @property
    def logo_size(self) -> Tuple[int, int]:
        """Get logo size."""
        return tuple(self.branding["logo_size"])
    
    @property
    def primary_color(self) -> str:
        """Get primary color."""
        return self.branding["primary_color"]
    
    @property
    def secondary_color(self) -> str:
        """Get secondary color."""
        return self.branding["secondary_color"]
    
    @property
    def background_color(self) -> str:
        """Get background color."""
        return self.branding["background_color"]
    
    @property
    def quote_font_size(self) -> int:
        """Get quote font size."""
        return self.text["quote_font_size"]
    
    @property
    def quote_color(self) -> str:
        """Get quote text color."""
        return self.text["quote_color"]
    
    @property
    def quote_max_width(self) -> int:
        """Get maximum width for quote text."""
        return self.text["quote_max_width"]
    
    @property
    def metadata_font_size(self) -> int:
        """Get metadata font size."""
        return self.text["metadata_font_size"]
    
    @property
    def metadata_color(self) -> str:
        """Get metadata text color."""
        return self.text["metadata_color"]


@dataclass
class PlatformSettings:
    """Settings for a specific social media platform."""
    
    enabled: bool
    caption_template: str
    hashtags: List[str]
    credentials: Dict[str, str] = field(default_factory=dict)
    
    def format_caption(self, **kwargs) -> str:
        """Format caption template with provided data."""
        return self.caption_template.format(**kwargs)
    
    def format_hashtags(self, additional_tags: Optional[List[str]] = None) -> str:
        """Format hashtags as a string."""
        tags = self.hashtags.copy()
        if additional_tags:
            tags.extend(additional_tags)
        return " ".join(tags)


@dataclass
class SocialMediaSettings:
    """Social media platform settings."""
    
    enabled_platforms: List[str]
    platforms: Dict[str, PlatformSettings]
    
    def get_platform(self, platform: str) -> Optional[PlatformSettings]:
        """Get settings for a specific platform."""
        return self.platforms.get(platform)
    
    def is_platform_enabled(self, platform: str) -> bool:
        """Check if a platform is enabled."""
        return platform in self.enabled_platforms and self.platforms.get(platform, PlatformSettings(False, "", [])).enabled


@dataclass
class QuoteSettings:
    """Quote extraction settings."""
    
    preferred_source: str
    fallback_sources: List[str]
    max_length: int
    
    def validate_source(self, source: str) -> bool:
        """Validate if a quote source is valid."""
        valid_sources = ["claude", "openai", "deepseek", "llama", "random"]
        return source in valid_sources


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """Main configuration class for BGE Social Quote Generator."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration YAML file
            
        Raises:
            ConfigurationError: If configuration is invalid or missing
        """
        self.config_path = config_path
        self._raw_config: Dict[str, Any] = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self._load_config()
        
        # Parse configuration sections
        self._parse_general_settings()
        self._parse_quote_settings()
        self._parse_image_settings()
        self._parse_social_media_settings()
        
        # Validate configuration
        self.validate()
    
    def _load_config(self) -> None:
        """Load YAML configuration file."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.example.yaml to {self.config_path} and configure it."
            )
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse configuration file: {e}")
        
        if not self._raw_config:
            raise ConfigurationError("Configuration file is empty")
        
        # Substitute environment variables
        self._substitute_env_vars(self._raw_config)
    
    def _substitute_env_vars(self, obj: Any) -> None:
        """
        Recursively substitute environment variables in configuration.
        
        Replaces ${VAR_NAME} with the value of environment variable VAR_NAME.
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    obj[key] = self._expand_env_var(value)
                elif isinstance(value, (dict, list)):
                    self._substitute_env_vars(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str):
                    obj[i] = self._expand_env_var(item)
                elif isinstance(item, (dict, list)):
                    self._substitute_env_vars(item)
    
    def _expand_env_var(self, value: str) -> str:
        """Expand environment variables in a string."""
        pattern = re.compile(r'\$\{([^}]+)\}')
        
        def replacer(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        return pattern.sub(replacer, value)
    
    def _validate_path(self, path: str, description: str = "path") -> str:
        """
        Validate path to prevent directory traversal attacks.
        
        Args:
            path: Path to validate
            description: Description of the path for error messages
            
        Returns:
            Validated path string
            
        Raises:
            ConfigurationError: If path contains directory traversal attempts
        """
        # Check for obvious directory traversal patterns
        if ".." in path or path.startswith("/"):
            raise ConfigurationError(
                f"Invalid {description}: {path} (absolute paths and '..' not allowed)"
            )
        
        return path
    
    def _parse_general_settings(self) -> None:
        """Parse general settings."""
        general = self._raw_config.get("general", {})
        
        self.episodes_dir = self._validate_path(
            general.get("episodes_dir", "_episodes"), "episodes_dir"
        )
        self.texts_dir = self._validate_path(
            general.get("texts_dir", "assets/texts"), "texts_dir"
        )
        self.output_dir = self._validate_path(
            general.get("output_dir", "output/images"), "output_dir"
        )
        self.log_dir = self._validate_path(
            general.get("log_dir", "output/logs"), "log_dir"
        )
        self.log_level = general.get("log_level", "INFO")
    
    def _parse_quote_settings(self) -> None:
        """Parse quote extraction settings."""
        quotes = self._raw_config.get("quotes", {})
        
        self._quote_settings = QuoteSettings(
            preferred_source=quotes.get("preferred_source", "claude"),
            fallback_sources=quotes.get("fallback_sources", ["openai", "deepseek", "llama"]),
            max_length=quotes.get("max_length", 280)
        )
    
    def _parse_image_settings(self) -> None:
        """Parse image generation settings."""
        images = self._raw_config.get("images", {})
        
        self._image_settings = ImageSettings(
            templates_dir=images.get("templates_dir", "templates"),
            fonts_dir=images.get("fonts_dir", "templates/fonts"),
            default_font=images.get("default_font", "OpenSans-Regular.ttf"),
            platforms=images.get("platforms", {}),
            branding=images.get("branding", {}),
            text=images.get("text", {})
        )
    
    def _parse_social_media_settings(self) -> None:
        """Parse social media platform settings."""
        social = self._raw_config.get("social_media", {})
        
        enabled_platforms = social.get("enabled_platforms", [])
        platforms = {}
        
        # Parse Twitter settings
        if "twitter" in social:
            twitter = social["twitter"]
            platforms["twitter"] = PlatformSettings(
                enabled=twitter.get("enabled", False),
                caption_template=twitter.get("caption_template", ""),
                hashtags=twitter.get("hashtags", []),
                credentials={
                    "api_key": twitter.get("api_key", ""),
                    "api_secret": twitter.get("api_secret", ""),
                    "access_token": twitter.get("access_token", ""),
                    "access_token_secret": twitter.get("access_token_secret", "")
                }
            )
        
        # Parse Instagram settings
        if "instagram" in social:
            instagram = social["instagram"]
            platforms["instagram"] = PlatformSettings(
                enabled=instagram.get("enabled", False),
                caption_template=instagram.get("caption_template", ""),
                hashtags=instagram.get("hashtags", []),
                credentials={
                    "username": instagram.get("username", ""),
                    "password": instagram.get("password", "")
                }
            )
        
        # Parse Facebook settings
        if "facebook" in social:
            facebook = social["facebook"]
            platforms["facebook"] = PlatformSettings(
                enabled=facebook.get("enabled", False),
                caption_template=facebook.get("caption_template", ""),
                hashtags=facebook.get("hashtags", []),
                credentials={
                    "access_token": facebook.get("access_token", ""),
                    "page_id": facebook.get("page_id", "")
                }
            )
        
        # Parse LinkedIn settings
        if "linkedin" in social:
            linkedin = social["linkedin"]
            platforms["linkedin"] = PlatformSettings(
                enabled=linkedin.get("enabled", False),
                caption_template=linkedin.get("caption_template", ""),
                hashtags=linkedin.get("hashtags", []),
                credentials={
                    "access_token": linkedin.get("access_token", ""),
                    "person_urn": linkedin.get("person_urn", "")
                }
            )
        
        self._social_media_settings = SocialMediaSettings(
            enabled_platforms=enabled_platforms,
            platforms=platforms
        )
    
    @property
    def image_settings(self) -> ImageSettings:
        """Get image generation settings."""
        return self._image_settings
    
    @property
    def social_media_settings(self) -> SocialMediaSettings:
        """Get social media platform settings."""
        return self._social_media_settings
    
    @property
    def quote_settings(self) -> QuoteSettings:
        """Get quote extraction settings."""
        return self._quote_settings
    
    def validate(self) -> bool:
        """
        Validate configuration completeness and correctness.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        errors = []
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if self.log_level not in valid_log_levels:
            errors.append(f"Invalid log_level: {self.log_level}. Must be one of {valid_log_levels}")
        
        # Validate quote source
        if not self.quote_settings.validate_source(self.quote_settings.preferred_source):
            errors.append(f"Invalid preferred_source: {self.quote_settings.preferred_source}")
        
        for source in self.quote_settings.fallback_sources:
            if not self.quote_settings.validate_source(source):
                errors.append(f"Invalid fallback source: {source}")
        
        # Validate quote max length
        if self.quote_settings.max_length <= 0:
            errors.append("max_length must be positive")
        
        # Validate image platforms
        if not self.image_settings.platforms:
            errors.append("No image platforms configured")
        
        for platform, settings in self.image_settings.platforms.items():
            if "dimensions" not in settings:
                errors.append(f"Platform {platform} missing dimensions")
            else:
                dims = settings["dimensions"]
                if not isinstance(dims, list) or len(dims) != 2:
                    errors.append(f"Platform {platform} dimensions must be [width, height]")
                elif dims[0] <= 0 or dims[1] <= 0:
                    errors.append(f"Platform {platform} dimensions must be positive")
        
        # Validate logo position
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
        if self.image_settings.logo_position not in valid_positions:
            errors.append(f"Invalid logo_position: {self.image_settings.logo_position}")
        
        # Validate colors (basic hex color check)
        color_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        colors_to_check = [
            ("primary_color", self.image_settings.primary_color),
            ("secondary_color", self.image_settings.secondary_color),
            ("background_color", self.image_settings.background_color),
            ("quote_color", self.image_settings.quote_color),
            ("metadata_color", self.image_settings.metadata_color)
        ]
        
        for color_name, color_value in colors_to_check:
            if not color_pattern.match(color_value):
                errors.append(f"Invalid {color_name}: {color_value}. Must be hex color (e.g., #FFFFFF)")
        
        # Validate font sizes
        if self.image_settings.quote_font_size <= 0:
            errors.append("quote_font_size must be positive")
        if self.image_settings.metadata_font_size <= 0:
            errors.append("metadata_font_size must be positive")
        
        # Validate social media settings
        for platform in self.social_media_settings.enabled_platforms:
            platform_settings = self.social_media_settings.get_platform(platform)
            if not platform_settings:
                errors.append(f"Platform {platform} is enabled but not configured")
            elif platform_settings.enabled:
                # Check for credentials (but don't fail if they're env var placeholders)
                if not platform_settings.caption_template:
                    errors.append(f"Platform {platform} missing caption_template")
        
        if errors:
            raise ConfigurationError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    def override_output_dir(self, output_dir: str) -> None:
        """Override output directory from CLI argument."""
        self.output_dir = output_dir
    
    def override_quote_source(self, source: str) -> None:
        """Override preferred quote source from CLI argument."""
        if not self.quote_settings.validate_source(source):
            raise ConfigurationError(f"Invalid quote source: {source}")
        self._quote_settings.preferred_source = source
    
    def validate_credentials(self) -> List[str]:
        """
        Validate that required credentials are present and not placeholders.
        
        Returns:
            List of warning messages for missing or placeholder credentials
        """
        warnings = []
        
        for platform in self.social_media_settings.enabled_platforms:
            settings = self.social_media_settings.get_platform(platform)
            if settings and settings.enabled:
                for key, value in settings.credentials.items():
                    # Check if credential is missing or still a placeholder
                    if not value or value.startswith("${") or value.startswith("your_"):
                        warnings.append(
                            f"⚠️  {platform}.{key} is not configured (still contains placeholder)"
                        )
        
        return warnings
