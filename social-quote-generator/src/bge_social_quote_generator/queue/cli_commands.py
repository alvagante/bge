"""CLI commands for queue management."""

import logging
from datetime import datetime
from typing import List, Optional

from ..config import Config
from ..extractors.quote_extractor import QuoteExtractor
from ..generators.image_generator import ImageGenerator
from .queue_manager import QueueManager
from .scheduler import Scheduler
from .publisher import QueuePublisher


logger = logging.getLogger(__name__)


class QueueCommands:
    """Handles queue-related CLI commands."""
    
    def __init__(self, config: Config):
        """
        Initialize queue commands.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Get queue settings
        queue_config = config._raw_config.get("queue", {})
        queue_file = queue_config.get("queue_file", "social-quote-generator/output/publish_queue.json")
        history_file = queue_config.get("history_file", "social-quote-generator/output/published_history.json")
        lock_file = queue_config.get("lock_file", "social-quote-generator/output/.publish.lock")
        
        # Initialize components
        self.queue_manager = QueueManager(queue_file, history_file, lock_file)
        self.scheduler = Scheduler(config)
        self.extractor = QuoteExtractor(config)
        self.generator = ImageGenerator(config)
    
    def add_to_queue(
        self,
        episode_number: str,
        platforms: Optional[List[str]] = None,
        schedule: Optional[str] = None,
        stagger: Optional[str] = None
    ) -> bool:
        """
        Generate images and add to queue.
        
        Args:
            episode_number: Episode number
            platforms: List of platforms (None = all configured)
            schedule: Custom schedule time
            stagger: Stagger interval (e.g., "6h")
            
        Returns:
            True if successful
        """
        logger.info(f"Adding episode {episode_number} to queue...")
        
        # Extract episode
        quote_data = self.extractor.extract_episode(episode_number)
        if not quote_data:
            logger.error(f"Failed to extract episode {episode_number}")
            return False
        
        # Determine platforms
        if not platforms:
            platforms = list(self.config.image_settings.platforms.keys())
        
        # Generate images
        image_paths = {}
        for platform in platforms:
            try:
                logger.info(f"Generating image for {platform}...")
                generated_image = self.generator.generate(quote_data, platform)
                image_paths[platform] = generated_image.file_path
                logger.info(f"✓ Generated: {generated_image.file_path}")
            except Exception as e:
                logger.error(f"✗ Failed to generate {platform} image: {e}")
                return False
        
        # Create queue items
        if stagger:
            # Staggered scheduling
            items = self.scheduler.create_staggered_items(
                quote_data,
                platforms,
                image_paths
            )
        else:
            # Single schedule time for all platforms
            items = []
            for platform in platforms:
                scheduled_time = None
                if schedule:
                    scheduled_time = self.scheduler.parse_schedule_time(schedule)
                
                item = self.scheduler.create_queue_item(
                    quote_data,
                    platform,
                    image_paths[platform],
                    scheduled_time
                )
                items.append(item)
        
        # Add to queue
        success_count = 0
        for item in items:
            if self.queue_manager.add_to_queue(item):
                logger.info(f"✓ Added to queue: {item.id} (scheduled: {item.scheduled_time})")
                success_count += 1
            else:
                logger.error(f"✗ Failed to add to queue: {item.id}")
        
        logger.info(f"\nAdded {success_count}/{len(items)} items to queue")
        return success_count > 0
    
    def list_queue(self) -> None:
        """List all pending items in queue."""
        items = self.queue_manager.get_all_pending()
        
        if not items:
            print("\nQueue is empty")
            return
        
        print(f"\n{'=' * 80}")
        print(f"Pending Queue Items ({len(items)} total)")
        print(f"{'=' * 80}\n")
        
        for item in items:
            scheduled_dt = item.get_scheduled_datetime()
            time_until = scheduled_dt - datetime.now()
            
            print(f"ID: {item.id}")
            print(f"  Episode: {item.episode_number} | Platform: {item.platform}")
            print(f"  Scheduled: {item.scheduled_time}")
            print(f"  Time until: {self._format_timedelta(time_until)}")
            print(f"  Image: {item.image_path}")
            print(f"  Caption: {item.texts.get('caption', '')[:100]}...")
            print(f"  Status: {item.status}")
            if item.retry_count > 0:
                print(f"  Retries: {item.retry_count}")
            print()
    
    def list_history(self, limit: int = 10) -> None:
        """List published items from history."""
        items = self.queue_manager.get_published_history(limit)
        
        if not items:
            print("\nNo published items in history")
            return
        
        print(f"\n{'=' * 80}")
        print(f"Published History (showing last {min(limit, len(items))} items)")
        print(f"{'=' * 80}\n")
        
        for item in items:
            print(f"ID: {item.id}")
            print(f"  Episode: {item.episode_number} | Platform: {item.platform}")
            print(f"  Scheduled: {item.scheduled_time}")
            print(f"  Published: {item.published_at}")
            print(f"  URL: {item.post_url}")
            print()
    
    def list_failed(self) -> None:
        """List failed items from history."""
        items = self.queue_manager.get_failed_history()
        
        if not items:
            print("\nNo failed items in history")
            return
        
        print(f"\n{'=' * 80}")
        print(f"Failed Items ({len(items)} total)")
        print(f"{'=' * 80}\n")
        
        for item in items:
            print(f"ID: {item.id}")
            print(f"  Episode: {item.episode_number} | Platform: {item.platform}")
            print(f"  Scheduled: {item.scheduled_time}")
            print(f"  Retries: {item.retry_count}")
            print(f"  Error: {item.error}")
            print()
    
    def remove_from_queue(self, item_id: str) -> bool:
        """Remove item from queue."""
        if self.queue_manager.remove_from_queue(item_id):
            logger.info(f"✓ Removed from queue: {item_id}")
            return True
        else:
            logger.error(f"✗ Failed to remove from queue: {item_id}")
            return False
    
    def publish_queue(self, dry_run: bool = False) -> dict:
        """Publish pending items from queue."""
        publisher = QueuePublisher(self.config)
        return publisher.publish_pending(dry_run)
    
    def publish_now(self, item_id: str, dry_run: bool = False) -> bool:
        """Publish specific item immediately."""
        publisher = QueuePublisher(self.config)
        return publisher.publish_item_by_id(item_id, dry_run)
    
    def _format_timedelta(self, td) -> str:
        """Format timedelta as human-readable string."""
        total_seconds = int(td.total_seconds())
        
        if total_seconds < 0:
            return f"{abs(total_seconds // 3600)}h {abs(total_seconds % 3600 // 60)}m ago"
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or not parts:
            parts.append(f"{minutes}m")
        
        return " ".join(parts)
