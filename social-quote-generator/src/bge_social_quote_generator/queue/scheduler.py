"""Scheduler for queue items."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from .queue_manager import QueueItem, QueueStatus
from .text_generator import TextGenerator
from ..extractors.base import EpisodeQuote


logger = logging.getLogger(__name__)


class Scheduler:
    """Handles scheduling logic for queue items."""
    
    def __init__(self, config):
        """
        Initialize scheduler.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.text_generator = TextGenerator(config)
        
        # Get queue settings
        queue_config = config._raw_config.get("queue", {})
        self.default_schedule = queue_config.get("default_schedule", {})
        self.stagger_interval = queue_config.get("stagger_interval", "6h")
        self.stagger_order = queue_config.get("stagger_order", [
            "twitter", "instagram", "linkedin", "facebook"
        ])
    
    def create_queue_item(
        self,
        quote_data: EpisodeQuote,
        platform: str,
        image_path: str,
        scheduled_time: Optional[str] = None
    ) -> QueueItem:
        """
        Create a queue item for an episode and platform.
        
        Args:
            quote_data: Episode quote data
            platform: Target platform
            image_path: Path to generated image
            scheduled_time: ISO format datetime string (optional)
            
        Returns:
            QueueItem ready to be added to queue
        """
        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        item_id = f"ep{quote_data.episode_number}_{platform}_{timestamp}_{uuid.uuid4().hex[:6]}"
        
        # Determine scheduled time
        if not scheduled_time:
            scheduled_time = self._get_default_schedule_time(platform)
        
        # Generate texts
        texts = self.text_generator.generate_texts(quote_data, platform)
        
        # Create metadata
        metadata = {
            "quote_source": quote_data.quote_source,
            "generated_at": datetime.now().isoformat(),
            "episode_title": quote_data.titolo,
            "guests": quote_data.guests,
            "duration": quote_data.duration,
            "youtube_id": quote_data.youtube_id
        }
        
        return QueueItem(
            id=item_id,
            episode_number=quote_data.episode_number,
            platform=platform,
            scheduled_time=scheduled_time,
            status=QueueStatus.PENDING.value,
            image_path=image_path,
            texts=texts,
            metadata=metadata
        )
    
    def create_staggered_items(
        self,
        quote_data: EpisodeQuote,
        platforms: List[str],
        image_paths: dict,
        start_time: Optional[datetime] = None
    ) -> List[QueueItem]:
        """
        Create staggered queue items for multiple platforms.
        
        Args:
            quote_data: Episode quote data
            platforms: List of platforms
            image_paths: Dictionary mapping platform to image path
            start_time: Starting datetime (defaults to tomorrow at first platform's time)
            
        Returns:
            List of queue items with staggered schedules
        """
        items = []
        
        # Parse stagger interval
        interval_hours = self._parse_interval(self.stagger_interval)
        
        # Determine start time
        if not start_time:
            # Default to tomorrow at first platform's default time
            first_platform = platforms[0]
            start_time = self._get_default_schedule_datetime(first_platform)
        
        # Create items with staggered times
        current_time = start_time
        for platform in platforms:
            if platform not in image_paths:
                logger.warning(f"No image path for platform: {platform}")
                continue
            
            item = self.create_queue_item(
                quote_data,
                platform,
                image_paths[platform],
                scheduled_time=current_time.isoformat()
            )
            items.append(item)
            
            # Increment time for next platform
            current_time += timedelta(hours=interval_hours)
        
        return items
    
    def _get_default_schedule_time(self, platform: str) -> str:
        """
        Get default schedule time for platform (tomorrow at configured time).
        
        Args:
            platform: Platform name
            
        Returns:
            ISO format datetime string
        """
        dt = self._get_default_schedule_datetime(platform)
        return dt.isoformat()
    
    def _get_default_schedule_datetime(self, platform: str) -> datetime:
        """
        Get default schedule datetime for platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Datetime object
        """
        # Get default time for platform
        default_time = self.default_schedule.get(platform, "09:00")
        
        # Parse time
        try:
            hour, minute = map(int, default_time.split(":"))
        except ValueError:
            logger.warning(f"Invalid default time for {platform}: {default_time}, using 09:00")
            hour, minute = 9, 0
        
        # Create datetime for tomorrow at specified time
        tomorrow = datetime.now() + timedelta(days=1)
        scheduled = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return scheduled
    
    def _parse_interval(self, interval_str: str) -> float:
        """
        Parse interval string to hours.
        
        Args:
            interval_str: Interval string (e.g., "6h", "30m", "1d")
            
        Returns:
            Hours as float
        """
        interval_str = interval_str.strip().lower()
        
        try:
            if interval_str.endswith("h"):
                return float(interval_str[:-1])
            elif interval_str.endswith("m"):
                return float(interval_str[:-1]) / 60
            elif interval_str.endswith("d"):
                return float(interval_str[:-1]) * 24
            else:
                # Assume hours if no unit
                return float(interval_str)
        except ValueError:
            logger.warning(f"Invalid interval: {interval_str}, using 6 hours")
            return 6.0
    
    def parse_schedule_time(self, schedule_str: str) -> str:
        """
        Parse user-provided schedule string to ISO format.
        
        Args:
            schedule_str: Schedule string (e.g., "2025-10-13 09:00", "tomorrow 9am", "+2d")
            
        Returns:
            ISO format datetime string
        """
        schedule_str = schedule_str.strip()
        
        # Try ISO format first
        try:
            dt = datetime.fromisoformat(schedule_str)
            return dt.isoformat()
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d-%m-%Y %H:%M"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(schedule_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        # Try relative times
        if schedule_str.startswith("+"):
            return self._parse_relative_time(schedule_str)
        
        # If all else fails, use default
        logger.warning(f"Could not parse schedule time: {schedule_str}, using default")
        return self._get_default_schedule_time("twitter")
    
    def _parse_relative_time(self, relative_str: str) -> str:
        """
        Parse relative time string (e.g., "+2d", "+6h").
        
        Args:
            relative_str: Relative time string
            
        Returns:
            ISO format datetime string
        """
        relative_str = relative_str.strip().lower()
        
        if not relative_str.startswith("+"):
            raise ValueError("Relative time must start with +")
        
        value_str = relative_str[1:]
        
        try:
            if value_str.endswith("d"):
                days = int(value_str[:-1])
                dt = datetime.now() + timedelta(days=days)
            elif value_str.endswith("h"):
                hours = int(value_str[:-1])
                dt = datetime.now() + timedelta(hours=hours)
            elif value_str.endswith("m"):
                minutes = int(value_str[:-1])
                dt = datetime.now() + timedelta(minutes=minutes)
            else:
                raise ValueError("Invalid relative time unit")
            
            return dt.isoformat()
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to parse relative time: {relative_str}, error: {e}")
            return datetime.now().isoformat()
