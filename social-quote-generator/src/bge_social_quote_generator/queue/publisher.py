"""Queue publisher for automated publishing."""

import logging
from datetime import datetime
from typing import List, Optional

from .queue_manager import QueueManager, QueueItem
from ..config import Config
from ..publishers.base import BasePublisher


logger = logging.getLogger(__name__)


class QueuePublisher:
    """Publishes items from the queue."""
    
    def __init__(self, config: Config):
        """
        Initialize queue publisher.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Get queue settings
        queue_config = config._raw_config.get("queue", {})
        queue_file = queue_config.get("queue_file", "social-quote-generator/output/publish_queue.json")
        history_file = queue_config.get("history_file", "social-quote-generator/output/published_history.json")
        lock_file = queue_config.get("lock_file", "social-quote-generator/output/.publish.lock")
        
        self.max_retries = queue_config.get("max_retries", 3)
        self.look_ahead_minutes = queue_config.get("look_ahead_minutes", 5)
        
        # Initialize queue manager
        self.queue_manager = QueueManager(queue_file, history_file, lock_file)
        
        # Publishers will be initialized on demand
        self.publishers = {}
    
    def publish_pending(self, dry_run: bool = False) -> dict:
        """
        Publish all pending items that are ready.
        
        Args:
            dry_run: If True, don't actually publish
            
        Returns:
            Dictionary with results
        """
        logger.info("=" * 60)
        logger.info("Queue Publisher - Checking for pending items")
        logger.info("=" * 60)
        
        # Get pending items
        pending_items = self.queue_manager.get_pending_items(self.look_ahead_minutes)
        
        if not pending_items:
            logger.info("No items ready for publishing")
            return {
                "total": 0,
                "published": 0,
                "failed": 0,
                "skipped": 0
            }
        
        logger.info(f"Found {len(pending_items)} items ready for publishing")
        
        results = {
            "total": len(pending_items),
            "published": 0,
            "failed": 0,
            "skipped": 0
        }
        
        # Process each item
        for item in pending_items:
            logger.info(f"\nProcessing: {item.id}")
            logger.info(f"  Episode: {item.episode_number}")
            logger.info(f"  Platform: {item.platform}")
            logger.info(f"  Scheduled: {item.scheduled_time}")
            
            if dry_run:
                logger.info(f"  [DRY RUN] Would publish to {item.platform}")
                results["published"] += 1
                continue
            
            # Publish item
            success = self._publish_item(item)
            
            if success:
                results["published"] += 1
            else:
                results["failed"] += 1
        
        # Log summary
        logger.info("\n" + "=" * 60)
        logger.info("Publishing Summary")
        logger.info("=" * 60)
        logger.info(f"Total items: {results['total']}")
        logger.info(f"✓ Published: {results['published']}")
        logger.info(f"✗ Failed: {results['failed']}")
        logger.info(f"⊘ Skipped: {results['skipped']}")
        logger.info("=" * 60)
        
        return results
    
    def publish_item_by_id(self, item_id: str, dry_run: bool = False) -> bool:
        """
        Publish a specific item by ID.
        
        Args:
            item_id: ID of the item to publish
            dry_run: If True, don't actually publish
            
        Returns:
            True if successful
        """
        item = self.queue_manager.get_item_by_id(item_id)
        
        if not item:
            logger.error(f"Item not found: {item_id}")
            return False
        
        logger.info(f"Publishing item: {item_id}")
        
        if dry_run:
            logger.info(f"[DRY RUN] Would publish to {item.platform}")
            return True
        
        return self._publish_item(item)
    
    def _publish_item(self, item: QueueItem) -> bool:
        """
        Publish a single queue item.
        
        Args:
            item: Queue item to publish
            
        Returns:
            True if successful
        """
        try:
            # Get or create publisher
            publisher = self._get_publisher(item.platform)
            
            if not publisher:
                error_msg = f"Failed to initialize publisher for {item.platform}"
                logger.error(error_msg)
                self.queue_manager.mark_failed(item.id, error_msg, self.max_retries)
                return False
            
            # Create a mock quote data object for the publisher
            from ..extractors.base import EpisodeQuote
            
            quote_data = EpisodeQuote(
                episode_number=item.episode_number,
                titolo=item.metadata.get("episode_title", ""),
                quote=item.texts.get("caption", ""),
                quote_source=item.metadata.get("quote_source", "unknown"),
                guests=item.metadata.get("guests", []),
                host="",
                date="",
                youtube_id=item.metadata.get("youtube_id", ""),
                duration=item.metadata.get("duration", 0),
                tags=[],
                summary=[]
            )
            
            # Publish
            logger.info(f"Publishing to {item.platform}...")
            result = publisher.publish(item.image_path, quote_data, dry_run=False)
            
            if result.success:
                logger.info(f"✓ Published successfully: {result.post_url}")
                self.queue_manager.mark_published(item.id, result.post_url or "")
                return True
            else:
                error_msg = result.error or "Unknown error"
                logger.error(f"✗ Publishing failed: {error_msg}")
                self.queue_manager.mark_failed(item.id, error_msg, self.max_retries)
                return False
                
        except Exception as e:
            error_msg = f"Exception during publishing: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.queue_manager.mark_failed(item.id, error_msg, self.max_retries)
            return False
    
    def _get_publisher(self, platform: str) -> Optional[BasePublisher]:
        """
        Get or create publisher for platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Publisher instance or None
        """
        # Return cached publisher if available
        if platform in self.publishers:
            return self.publishers[platform]
        
        # Create new publisher
        try:
            publisher = self._create_publisher(platform)
            
            # Authenticate
            if publisher.authenticate():
                self.publishers[platform] = publisher
                logger.info(f"✓ Initialized {platform} publisher")
                return publisher
            else:
                logger.error(f"✗ Failed to authenticate with {platform}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Failed to create {platform} publisher: {e}")
            return None
    
    def _create_publisher(self, platform: str) -> BasePublisher:
        """
        Create a publisher instance for the specified platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Publisher instance
            
        Raises:
            ValueError: If platform is not supported
        """
        if platform == "twitter":
            from ..publishers.twitter_publisher import TwitterPublisher
            return TwitterPublisher(self.config)
        elif platform == "instagram":
            from ..publishers.instagram_publisher import InstagramPublisher
            return InstagramPublisher(self.config)
        elif platform == "facebook":
            from ..publishers.facebook_publisher import FacebookPublisher
            return FacebookPublisher(self.config)
        elif platform == "linkedin":
            from ..publishers.linkedin_publisher import LinkedInPublisher
            return LinkedInPublisher(self.config)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
