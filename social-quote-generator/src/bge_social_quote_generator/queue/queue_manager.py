"""Queue manager for scheduled social media posts."""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from filelock import FileLock


logger = logging.getLogger(__name__)


class QueueStatus(Enum):
    """Status of a queue item."""
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueueItem:
    """Represents a scheduled social media post."""
    
    id: str
    episode_number: str
    platform: str
    scheduled_time: str  # ISO format: YYYY-MM-DDTHH:MM:SS
    status: str
    image_path: str
    texts: Dict[str, Any]
    metadata: Dict[str, Any]
    
    # Optional fields for published/failed items
    published_at: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueItem':
        """Create from dictionary."""
        return cls(**data)
    
    def get_scheduled_datetime(self) -> datetime:
        """Parse scheduled time as datetime object."""
        return datetime.fromisoformat(self.scheduled_time)


@dataclass
class QueueFile:
    """Represents the queue file structure."""
    
    version: str = "1.0"
    queue: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "queue": self.queue
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueFile':
        """Create from dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            queue=data.get("queue", [])
        )


@dataclass
class HistoryFile:
    """Represents the published history file structure."""
    
    version: str = "1.0"
    published: List[Dict[str, Any]] = field(default_factory=list)
    failed: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "published": self.published,
            "failed": self.failed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryFile':
        """Create from dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            published=data.get("published", []),
            failed=data.get("failed", [])
        )


class QueueManager:
    """Manages the publishing queue and history."""
    
    def __init__(self, queue_file: str, history_file: str, lock_file: str):
        """
        Initialize queue manager.
        
        Args:
            queue_file: Path to queue JSON file
            history_file: Path to history JSON file
            lock_file: Path to lock file for concurrent access
        """
        self.queue_file = Path(queue_file)
        self.history_file = Path(history_file)
        self.lock_file = Path(lock_file)
        
        # Ensure parent directories exist
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self) -> None:
        """Initialize queue and history files if they don't exist."""
        if not self.queue_file.exists():
            self._save_queue(QueueFile())
            logger.info(f"Created queue file: {self.queue_file}")
        
        if not self.history_file.exists():
            self._save_history(HistoryFile())
            logger.info(f"Created history file: {self.history_file}")
    
    def _load_queue(self) -> QueueFile:
        """Load queue from file."""
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return QueueFile.from_dict(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse queue file: {e}")
            return QueueFile()
        except Exception as e:
            logger.error(f"Failed to load queue file: {e}")
            return QueueFile()
    
    def _save_queue(self, queue_data: QueueFile) -> None:
        """Save queue to file."""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_data.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save queue file: {e}")
            raise
    
    def _load_history(self) -> HistoryFile:
        """Load history from file."""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return HistoryFile.from_dict(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse history file: {e}")
            return HistoryFile()
        except Exception as e:
            logger.error(f"Failed to load history file: {e}")
            return HistoryFile()
    
    def _save_history(self, history_data: HistoryFile) -> None:
        """Save history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save history file: {e}")
            raise
    
    def add_to_queue(self, item: QueueItem) -> bool:
        """
        Add item to queue.
        
        Args:
            item: Queue item to add
            
        Returns:
            True if successful
        """
        lock = FileLock(self.lock_file, timeout=10)
        
        try:
            with lock:
                queue_data = self._load_queue()
                
                # Check for duplicate ID
                if any(q["id"] == item.id for q in queue_data.queue):
                    logger.warning(f"Item with ID {item.id} already exists in queue")
                    return False
                
                queue_data.queue.append(item.to_dict())
                self._save_queue(queue_data)
                
                logger.info(f"Added to queue: {item.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add item to queue: {e}")
            return False
    
    def get_pending_items(self, look_ahead_minutes: int = 5) -> List[QueueItem]:
        """
        Get items that are ready to be published.
        
        Args:
            look_ahead_minutes: Publish items within this many minutes of scheduled time
            
        Returns:
            List of queue items ready for publishing
        """
        lock = FileLock(self.lock_file, timeout=10)
        
        try:
            with lock:
                queue_data = self._load_queue()
                now = datetime.now()
                pending = []
                
                for item_dict in queue_data.queue:
                    item = QueueItem.from_dict(item_dict)
                    
                    if item.status != QueueStatus.PENDING.value:
                        continue
                    
                    scheduled = item.get_scheduled_datetime()
                    time_diff = (scheduled - now).total_seconds() / 60
                    
                    # Check if within look-ahead window
                    if -look_ahead_minutes <= time_diff <= look_ahead_minutes:
                        pending.append(item)
                
                return pending
                
        except Exception as e:
            logger.error(f"Failed to get pending items: {e}")
            return []
    
    def get_all_pending(self) -> List[QueueItem]:
        """Get all pending items regardless of schedule."""
        lock = FileLock(self.lock_file, timeout=10)
        
        try:
            with lock:
                queue_data = self._load_queue()
                return [
                    QueueItem.from_dict(item)
                    for item in queue_data.queue
                    if item["status"] == QueueStatus.PENDING.value
                ]
        except Exception as e:
            logger.error(f"Failed to get all pending items: {e}")
            return []
    
    def get_item_by_id(self, item_id: str) -> Optional[QueueItem]:
        """Get a specific queue item by ID."""
        lock = FileLock(self.lock_file, timeout=10)
        
        try:
            with lock:
                queue_data = self._load_queue()
                
                for item_dict in queue_data.queue:
                    if item_dict["id"] == item_id:
                        return QueueItem.from_dict(item_dict)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get item by ID: {e}")
            return None
    
    def mark_published(self, item_id: str, post_url: str) -> bool:
        """
        Mark item as published and move to history.
        
        Args:
            item_id: ID of the item
            post_url: URL of the published post
            
        Returns:
            True if successful
        """
        lock = FileLock(self.lock_file, timeout=10)
        
        try:
            with lock:
                # Load queue and history
                queue_data = self._load_queue()
                history_data = self._load_history()
                
                # Find and remove item from queue
                item_dict = None
                queue_data.queue = [
                    item for item in queue_data.queue
                    if item["id"] != item_id or (item_dict := item, False)[1]
                ]
                
                if not item_dict:
                    logger.warning(f"Item {item_id} not found in queue")
                    return False
                
                # Update item status
                item = QueueItem.from_dict(item_dict)
                item.status = QueueStatus.PUBLISHED.value
                item.published_at = datetime.now().isoformat()
                item.post_url = post_url
                
                # Add to history
                history_data.published.append(item.to_dict())
                
                # Save both files
                self._save_queue(queue_data)
                self._save_history(history_data)
                
                logger.info(f"Marked as published: {item_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to mark item as published: {e}")
            return False
    
    def mark_failed(self, item_id: str, error: str, max_retries: int = 3) -> bool:
        """
        Mark item as failed and optionally move to history.
        
        Args:
            item_id: ID of the item
            error: Error message
            max_retries: Maximum retry attempts before moving to failed history
            
        Returns:
            True if successful
        """
        lock = FileLock(self.lock_file, timeout=10)
        
        try:
            with lock:
                queue_data = self._load_queue()
                
                # Find item in queue
                for item_dict in queue_data.queue:
                    if item_dict["id"] == item_id:
                        item = QueueItem.from_dict(item_dict)
                        item.retry_count += 1
                        item.error = error
                        
                        if item.retry_count >= max_retries:
                            # Move to failed history
                            item.status = QueueStatus.FAILED.value
                            
                            history_data = self._load_history()
                            history_data.failed.append(item.to_dict())
                            self._save_history(history_data)
                            
                            # Remove from queue
                            queue_data.queue = [
                                q for q in queue_data.queue if q["id"] != item_id
                            ]
                            
                            logger.warning(f"Moved to failed history: {item_id} (max retries reached)")
                        else:
                            # Update in queue for retry
                            item_dict.update(item.to_dict())
                            logger.warning(f"Marked for retry: {item_id} (attempt {item.retry_count}/{max_retries})")
                        
                        self._save_queue(queue_data)
                        return True
                
                logger.warning(f"Item {item_id} not found in queue")
                return False
                
        except Exception as e:
            logger.error(f"Failed to mark item as failed: {e}")
            return False
    
    def remove_from_queue(self, item_id: str) -> bool:
        """
        Remove item from queue.
        
        Args:
            item_id: ID of the item to remove
            
        Returns:
            True if successful
        """
        lock = FileLock(self.lock_file, timeout=10)
        
        try:
            with lock:
                queue_data = self._load_queue()
                original_length = len(queue_data.queue)
                
                queue_data.queue = [
                    item for item in queue_data.queue if item["id"] != item_id
                ]
                
                if len(queue_data.queue) == original_length:
                    logger.warning(f"Item {item_id} not found in queue")
                    return False
                
                self._save_queue(queue_data)
                logger.info(f"Removed from queue: {item_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove item from queue: {e}")
            return False
    
    def get_published_history(self, limit: Optional[int] = None) -> List[QueueItem]:
        """
        Get published items from history.
        
        Args:
            limit: Maximum number of items to return (most recent first)
            
        Returns:
            List of published queue items
        """
        try:
            history_data = self._load_history()
            published = [QueueItem.from_dict(item) for item in history_data.published]
            
            # Sort by published_at descending
            published.sort(
                key=lambda x: x.published_at or "",
                reverse=True
            )
            
            if limit:
                return published[:limit]
            return published
            
        except Exception as e:
            logger.error(f"Failed to get published history: {e}")
            return []
    
    def get_failed_history(self, limit: Optional[int] = None) -> List[QueueItem]:
        """
        Get failed items from history.
        
        Args:
            limit: Maximum number of items to return (most recent first)
            
        Returns:
            List of failed queue items
        """
        try:
            history_data = self._load_history()
            failed = [QueueItem.from_dict(item) for item in history_data.failed]
            
            # Sort by retry_count descending (most retries first)
            failed.sort(key=lambda x: x.retry_count, reverse=True)
            
            if limit:
                return failed[:limit]
            return failed
            
        except Exception as e:
            logger.error(f"Failed to get failed history: {e}")
            return []
