"""Text generator for social media captions and posts."""

import logging
from typing import Dict, List, Optional, Any

from ..extractors.base import EpisodeQuote


logger = logging.getLogger(__name__)


class TextGenerator:
    """Generates platform-specific text content for social media posts."""
    
    def __init__(self, config):
        """
        Initialize text generator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.episode_url_template = config._raw_config.get("queue", {}).get(
            "episode_url_template",
            "https://labrigatadeigeekestinti.com/ep/{episode_number}/"
        )
    
    def generate_texts(
        self,
        quote_data: EpisodeQuote,
        platform: str
    ) -> Dict[str, Any]:
        """
        Generate all text content for a post.
        
        Args:
            quote_data: Episode quote data
            platform: Target platform
            
        Returns:
            Dictionary with caption, hook, link, and hashtags
        """
        # Get platform settings
        platform_settings = self.config.social_media_settings.get_platform(platform)
        if not platform_settings:
            logger.warning(f"No settings found for platform: {platform}")
            platform_settings = self._get_default_platform_settings(platform)
        
        # Get template from queue config or fall back to platform settings
        template = self._get_caption_template(platform)
        
        # Generate episode URL
        episode_url = self.episode_url_template.format(
            episode_number=quote_data.episode_number
        )
        
        # Prepare template variables
        template_vars = {
            "episode_number": quote_data.episode_number,
            "title": quote_data.titolo,
            "quote": quote_data.quote,
            "guests": ", ".join(quote_data.guests) if quote_data.guests else "N/A",
            "date": quote_data.date,
            "youtube_url": f"https://www.youtube.com/watch?v={quote_data.youtube_id}",
            "youtube_id": quote_data.youtube_id,
            "host": quote_data.host,
            "link": episode_url,
            "topics": ", ".join(quote_data.summary[:3]) if quote_data.summary else "vari argomenti"
        }
        
        # Generate hashtags
        hashtags = self._generate_hashtags(quote_data, platform_settings)
        template_vars["hashtags"] = " ".join(hashtags)
        
        # Generate caption from template
        caption = self._format_caption(template, template_vars, platform)
        
        # Generate hook
        hook = self._generate_hook(platform, quote_data)
        
        return {
            "caption": caption,
            "hook": hook,
            "link": episode_url,
            "hashtags": hashtags
        }
    
    def _get_caption_template(self, platform: str) -> str:
        """Get caption template for platform."""
        # Try queue config first
        queue_config = self.config._raw_config.get("queue", {})
        text_templates = queue_config.get("text_templates", {})
        
        if platform in text_templates:
            return text_templates[platform].get("caption", "")
        
        # Fall back to social media settings
        platform_settings = self.config.social_media_settings.get_platform(platform)
        if platform_settings:
            return platform_settings.caption_template
        
        # Default template
        return "🎙️ BGE Episodio {episode_number}: {title}\n\n\"{quote}\"\n\n{hashtags}"
    
    def _format_caption(
        self,
        template: str,
        variables: Dict[str, str],
        platform: str
    ) -> str:
        """
        Format caption from template with character limit handling.
        
        Args:
            template: Caption template
            variables: Template variables
            platform: Target platform
            
        Returns:
            Formatted caption
        """
        try:
            caption = template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            caption = template
        
        # Apply platform-specific character limits
        max_length = self._get_platform_char_limit(platform)
        if len(caption) > max_length:
            logger.warning(
                f"Caption exceeds {platform} limit ({len(caption)} > {max_length}), truncating"
            )
            caption = caption[:max_length-3] + "..."
        
        return caption
    
    def _get_platform_char_limit(self, platform: str) -> int:
        """Get character limit for platform."""
        limits = {
            "twitter": 280,
            "instagram": 2200,
            "facebook": 5000,
            "linkedin": 3000
        }
        return limits.get(platform, 1000)
    
    def _generate_hashtags(
        self,
        quote_data: EpisodeQuote,
        platform_settings
    ) -> List[str]:
        """
        Generate hashtags from episode tags and platform defaults.
        
        Args:
            quote_data: Episode quote data
            platform_settings: Platform settings
            
        Returns:
            List of hashtags with # prefix
        """
        hashtags = []
        
        # Add platform default hashtags
        if platform_settings and platform_settings.hashtags:
            hashtags.extend(platform_settings.hashtags)
        
        # Add episode-specific tags
        if quote_data.tags:
            for tag in quote_data.tags[:5]:  # Limit to 5 episode tags
                # Format tag as hashtag
                hashtag = self._format_hashtag(tag)
                if hashtag and hashtag not in hashtags:
                    hashtags.append(hashtag)
        
        return hashtags
    
    def _format_hashtag(self, tag: str) -> str:
        """
        Format a tag as a hashtag.
        
        Args:
            tag: Tag string
            
        Returns:
            Formatted hashtag with # prefix
        """
        # Remove spaces and special characters
        clean_tag = "".join(c for c in tag if c.isalnum() or c in ["_"])
        
        if not clean_tag:
            return ""
        
        # Add # prefix if not present
        if not clean_tag.startswith("#"):
            clean_tag = f"#{clean_tag}"
        
        return clean_tag
    
    def _generate_hook(self, platform: str, quote_data: EpisodeQuote) -> str:
        """
        Generate a hook/teaser text for the post.
        
        Args:
            platform: Target platform
            quote_data: Episode quote data
            
        Returns:
            Hook text
        """
        # Try queue config first
        queue_config = self.config._raw_config.get("queue", {})
        text_templates = queue_config.get("text_templates", {})
        
        if platform in text_templates:
            hook = text_templates[platform].get("hook", "")
            if hook:
                return hook
        
        # Default hooks by platform
        default_hooks = {
            "twitter": "Nuovo episodio disponibile!",
            "instagram": "Nuovo episodio del podcast!",
            "linkedin": "Nuovo episodio del podcast BGE",
            "facebook": "Ascolta il nuovo episodio!"
        }
        
        return default_hooks.get(platform, "Nuovo episodio!")
    
    def _get_default_platform_settings(self, platform: str):
        """Get default platform settings as fallback."""
        from ..config import PlatformSettings
        
        default_hashtags = {
            "twitter": ["#BGE", "#DevOps", "#IT"],
            "instagram": ["#BGE", "#DevOps", "#IT", "#Podcast"],
            "linkedin": ["#BGE", "#DevOps", "#IT", "#Tech"],
            "facebook": ["#BGE", "#DevOps", "#IT"]
        }
        
        return PlatformSettings(
            enabled=True,
            caption_template="🎙️ BGE Episodio {episode_number}: {title}\n\n\"{quote}\"\n\n{hashtags}",
            hashtags=default_hashtags.get(platform, ["#BGE"])
        )
