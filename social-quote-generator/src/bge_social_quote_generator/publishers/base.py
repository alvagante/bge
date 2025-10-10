"""Base publisher interface for social media platforms."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..config import Config
from ..extractors.base import EpisodeQuote


@dataclass
class PublishResult:
    """
    Result of a publish operation.
    
    Attributes:
        success: Whether the publish operation succeeded
        platform: Name of the platform (twitter, instagram, etc.)
        post_url: URL of the published post (if successful)
        error: Error message (if failed)
        timestamp: When the publish operation completed
    """
    
    success: bool
    platform: str
    post_url: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        """String representation of the publish result."""
        if self.success:
            return f"✓ Published to {self.platform}: {self.post_url}"
        else:
            return f"✗ Failed to publish to {self.platform}: {self.error}"


class BasePublisher(ABC):
    """
    Abstract base class for social media publishers.
    
    All platform-specific publishers should inherit from this class
    and implement the authenticate() and publish() methods.
    """
    
    def __init__(self, config: Config):
        """
        Initialize publisher with configuration.
        
        Args:
            config: Configuration object containing platform settings
        """
        self.config = config
        self.platform_name = self._get_platform_name()
        self.platform_settings = config.social_media_settings.get_platform(self.platform_name)
        
        if not self.platform_settings:
            raise ValueError(f"Platform {self.platform_name} not configured")
        
        if not self.platform_settings.enabled:
            raise ValueError(f"Platform {self.platform_name} is not enabled")
    
    @abstractmethod
    def _get_platform_name(self) -> str:
        """
        Get the platform name for this publisher.
        
        Returns:
            Platform name (e.g., 'twitter', 'instagram')
        """
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform API.
        
        Returns:
            True if authentication succeeded, False otherwise
            
        Raises:
            Exception: If authentication fails with an error
        """
        pass
    
    @abstractmethod
    def publish(
        self,
        image_path: str,
        quote_data: EpisodeQuote,
        dry_run: bool = False
    ) -> PublishResult:
        """
        Publish an image with caption to the platform.
        
        Args:
            image_path: Path to the image file to publish
            quote_data: Episode quote data for caption generation
            dry_run: If True, generate caption but don't actually publish
            
        Returns:
            PublishResult with success status and details
        """
        pass
    
    def _generate_caption(self, quote_data: EpisodeQuote) -> str:
        """
        Generate caption from template with episode data substitution.
        
        Args:
            quote_data: Episode quote data
            
        Returns:
            Formatted caption string
        """
        # Prepare data for template substitution
        caption_data = {
            "episode_number": quote_data.episode_number,
            "title": quote_data.titolo or quote_data.title,
            "quote": quote_data.quote,
            "guests": quote_data.formatted_guests,
            "date": quote_data.date,
            "youtube_url": quote_data.youtube_url,
            "youtube_id": quote_data.youtube_id,
            "host": quote_data.host,
            "hashtags": self._generate_hashtags(quote_data)
        }
        
        # Format caption using template
        try:
            caption = self.platform_settings.format_caption(**caption_data)
        except KeyError as e:
            # If a template variable is missing, provide a helpful error
            raise ValueError(
                f"Caption template references undefined variable: {e}. "
                f"Available variables: {', '.join(caption_data.keys())}"
            )
        
        return caption
    
    def _generate_hashtags(self, quote_data: EpisodeQuote) -> str:
        """
        Generate hashtags from episode tags and platform defaults.
        
        Args:
            quote_data: Episode quote data with tags
            
        Returns:
            Space-separated hashtags string
        """
        # Get episode-specific hashtags from tags
        episode_hashtags = [f"#{tag.replace(' ', '')}" for tag in quote_data.tags]
        
        # Combine with platform default hashtags
        all_hashtags = self.platform_settings.format_hashtags(episode_hashtags)
        
        return all_hashtags
    
    def _validate_image_path(self, image_path: str) -> bool:
        """
        Validate that the image file exists and is readable.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image is valid
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image file is not readable
        """
        import os
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not os.path.isfile(image_path):
            raise ValueError(f"Path is not a file: {image_path}")
        
        if not os.access(image_path, os.R_OK):
            raise ValueError(f"Image file is not readable: {image_path}")
        
        return True
