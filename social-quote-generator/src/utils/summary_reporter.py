"""
Summary reporting utilities for the Social Quote Generator.

This module provides comprehensive reporting of pipeline execution results,
including processed episodes, generated images, and published posts.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class EpisodeResult:
    """Result of processing a single episode."""
    episode_number: str
    success: bool
    images_generated: int = 0
    images_failed: int = 0
    posts_published: int = 0
    posts_failed: int = 0
    platforms: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "episode_number": self.episode_number,
            "success": self.success,
            "images_generated": self.images_generated,
            "images_failed": self.images_failed,
            "posts_published": self.posts_published,
            "posts_failed": self.posts_failed,
            "platforms": self.platforms,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PipelineSummary:
    """Summary of entire pipeline execution."""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_episodes_processed: int = 0
    successful_episodes: int = 0
    failed_episodes: int = 0
    total_images_generated: int = 0
    total_images_failed: int = 0
    total_posts_published: int = 0
    total_posts_failed: int = 0
    episode_results: List[EpisodeResult] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "total_episodes_processed": self.total_episodes_processed,
            "successful_episodes": self.successful_episodes,
            "failed_episodes": self.failed_episodes,
            "total_images_generated": self.total_images_generated,
            "total_images_failed": self.total_images_failed,
            "total_posts_published": self.total_posts_published,
            "total_posts_failed": self.total_posts_failed,
            "episode_results": [result.to_dict() for result in self.episode_results]
        }


class SummaryReporter:
    """
    Generate and display comprehensive summaries of pipeline execution.
    
    This class tracks all operations and provides detailed reporting
    of successes, failures, and overall statistics.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize summary reporter.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger or logging.getLogger(__name__)
        self.summary = PipelineSummary(start_time=datetime.now())
    
    def start_execution(self):
        """Mark the start of pipeline execution."""
        self.summary.start_time = datetime.now()
        self.logger.info("Pipeline execution started")
    
    def end_execution(self):
        """Mark the end of pipeline execution."""
        self.summary.end_time = datetime.now()
        self.logger.info(f"Pipeline execution completed in {self.summary.duration_seconds:.2f} seconds")
    
    def add_episode_result(self, result: EpisodeResult):
        """
        Add result for a processed episode.
        
        Args:
            result: Episode processing result
        """
        self.summary.episode_results.append(result)
        self.summary.total_episodes_processed += 1
        
        if result.success:
            self.summary.successful_episodes += 1
        else:
            self.summary.failed_episodes += 1
        
        self.summary.total_images_generated += result.images_generated
        self.summary.total_images_failed += result.images_failed
        self.summary.total_posts_published += result.posts_published
        self.summary.total_posts_failed += result.posts_failed
    
    def record_image_generated(self, episode_number: str, platform: str):
        """
        Record successful image generation.
        
        Args:
            episode_number: Episode number
            platform: Target platform
        """
        self.logger.info(f"Generated image for episode {episode_number} ({platform})")
    
    def record_image_failed(self, episode_number: str, platform: str, error: str):
        """
        Record failed image generation.
        
        Args:
            episode_number: Episode number
            platform: Target platform
            error: Error message
        """
        self.logger.error(f"Failed to generate image for episode {episode_number} ({platform}): {error}")
    
    def record_post_published(self, episode_number: str, platform: str, post_url: Optional[str] = None):
        """
        Record successful post publication.
        
        Args:
            episode_number: Episode number
            platform: Target platform
            post_url: Optional URL of published post
        """
        if post_url:
            self.logger.info(f"Published episode {episode_number} to {platform}: {post_url}")
        else:
            self.logger.info(f"Published episode {episode_number} to {platform}")
    
    def record_post_failed(self, episode_number: str, platform: str, error: str):
        """
        Record failed post publication.
        
        Args:
            episode_number: Episode number
            platform: Target platform
            error: Error message
        """
        self.logger.error(f"Failed to publish episode {episode_number} to {platform}: {error}")
    
    def get_summary(self) -> PipelineSummary:
        """Get the current pipeline summary."""
        return self.summary
    
    def print_summary(self):
        """Print a comprehensive human-readable summary."""
        if not self.summary.end_time:
            self.summary.end_time = datetime.now()
        
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("PIPELINE EXECUTION SUMMARY")
        self.logger.info("=" * 70)
        
        # Execution time
        self.logger.info(f"Start Time: {self.summary.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"End Time: {self.summary.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Duration: {self.summary.duration_seconds:.2f} seconds")
        self.logger.info("")
        
        # Episode statistics
        self.logger.info("EPISODE PROCESSING:")
        self.logger.info(f"  Total Episodes Processed: {self.summary.total_episodes_processed}")
        self.logger.info(f"  Successful: {self.summary.successful_episodes}")
        self.logger.info(f"  Failed: {self.summary.failed_episodes}")
        
        if self.summary.total_episodes_processed > 0:
            success_rate = (self.summary.successful_episodes / self.summary.total_episodes_processed) * 100
            self.logger.info(f"  Success Rate: {success_rate:.1f}%")
        self.logger.info("")
        
        # Image generation statistics
        self.logger.info("IMAGE GENERATION:")
        self.logger.info(f"  Images Generated: {self.summary.total_images_generated}")
        self.logger.info(f"  Images Failed: {self.summary.total_images_failed}")
        
        total_image_attempts = self.summary.total_images_generated + self.summary.total_images_failed
        if total_image_attempts > 0:
            image_success_rate = (self.summary.total_images_generated / total_image_attempts) * 100
            self.logger.info(f"  Success Rate: {image_success_rate:.1f}%")
        self.logger.info("")
        
        # Publishing statistics
        self.logger.info("SOCIAL MEDIA PUBLISHING:")
        self.logger.info(f"  Posts Published: {self.summary.total_posts_published}")
        self.logger.info(f"  Posts Failed: {self.summary.total_posts_failed}")
        
        total_post_attempts = self.summary.total_posts_published + self.summary.total_posts_failed
        if total_post_attempts > 0:
            post_success_rate = (self.summary.total_posts_published / total_post_attempts) * 100
            self.logger.info(f"  Success Rate: {post_success_rate:.1f}%")
        self.logger.info("")
        
        # Episode details
        if self.summary.episode_results:
            self.logger.info("EPISODE DETAILS:")
            for result in self.summary.episode_results:
                status = "✓" if result.success else "✗"
                self.logger.info(f"  {status} Episode {result.episode_number}:")
                self.logger.info(f"      Images: {result.images_generated} generated, {result.images_failed} failed")
                self.logger.info(f"      Posts: {result.posts_published} published, {result.posts_failed} failed")
                if result.platforms:
                    self.logger.info(f"      Platforms: {', '.join(result.platforms)}")
                if result.errors:
                    self.logger.info(f"      Errors: {len(result.errors)}")
                    for error in result.errors[:3]:  # Show first 3 errors
                        self.logger.info(f"        - {error}")
                    if len(result.errors) > 3:
                        self.logger.info(f"        ... and {len(result.errors) - 3} more")
        
        self.logger.info("=" * 70)
    
    def print_quick_summary(self):
        """Print a brief summary suitable for console output."""
        if not self.summary.end_time:
            self.summary.end_time = datetime.now()
        
        self.logger.info("")
        self.logger.info("Summary:")
        self.logger.info(f"  Episodes: {self.summary.successful_episodes}/{self.summary.total_episodes_processed} successful")
        self.logger.info(f"  Images: {self.summary.total_images_generated} generated, {self.summary.total_images_failed} failed")
        self.logger.info(f"  Posts: {self.summary.total_posts_published} published, {self.summary.total_posts_failed} failed")
        self.logger.info(f"  Duration: {self.summary.duration_seconds:.2f}s")
