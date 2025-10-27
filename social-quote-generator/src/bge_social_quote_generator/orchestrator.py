"""Pipeline orchestrator for BGE Social Quote Generator."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .config import Config
from .extractors.base import EpisodeQuote
from .extractors.quote_extractor import QuoteExtractor
from .generators.base import GeneratedImage
from .generators.image_generator import ImageGenerator
from .publishers.base import BasePublisher, PublishResult


logger = logging.getLogger(__name__)


@dataclass
class EpisodeResult:
    """Result of processing a single episode."""
    
    episode_number: str
    success: bool
    generated_images: List[GeneratedImage] = field(default_factory=list)
    publish_results: List[PublishResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        """Check if there were any errors."""
        return len(self.errors) > 0
    
    @property
    def images_generated(self) -> int:
        """Count of successfully generated images."""
        return len(self.generated_images)
    
    @property
    def posts_published(self) -> int:
        """Count of successfully published posts."""
        return sum(1 for result in self.publish_results if result.success)


@dataclass
class PipelineResult:
    """
    Result of the complete pipeline execution.
    
    Attributes:
        total_episodes: Total number of episodes processed
        successful_images: Number of images successfully generated
        failed_images: Number of images that failed to generate
        successful_posts: Number of posts successfully published
        failed_posts: Number of posts that failed to publish
        results: List of per-episode results
        start_time: When the pipeline started
        end_time: When the pipeline completed
    """
    
    total_episodes: int
    successful_images: int
    failed_images: int
    successful_posts: int
    failed_posts: int
    results: List[EpisodeResult]
    start_time: datetime
    end_time: datetime
    
    @property
    def duration(self) -> float:
        """Get pipeline duration in seconds."""
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_episodes == 0:
            return 0.0
        successful = sum(1 for r in self.results if r.success and not r.has_errors)
        return (successful / self.total_episodes) * 100
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the pipeline execution."""
        lines = [
            "=" * 60,
            "Pipeline Execution Summary",
            "=" * 60,
            f"Duration: {self.duration:.2f} seconds",
            f"Episodes processed: {self.total_episodes}",
            f"Success rate: {self.success_rate:.1f}%",
            "",
            "Images:",
            f"  ✓ Generated: {self.successful_images}",
            f"  ✗ Failed: {self.failed_images}",
            "",
            "Publishing:",
            f"  ✓ Published: {self.successful_posts}",
            f"  ✗ Failed: {self.failed_posts}",
            "=" * 60
        ]
        
        # Add error details if any
        errors = []
        for result in self.results:
            if result.has_errors:
                errors.extend([
                    f"Episode {result.episode_number}: {error}"
                    for error in result.errors
                ])
        
        if errors:
            lines.extend(["", "Errors:", ""])
            lines.extend([f"  • {error}" for error in errors])
            lines.append("=" * 60)
        
        return "\n".join(lines)


class PipelineOrchestrator:
    """
    Orchestrates the complete workflow from extraction to publishing.
    
    Coordinates:
    - Quote extraction from episode files
    - Image generation for specified platforms
    - Publishing to enabled social media platforms
    - Error handling and result collection
    """
    
    def __init__(self, config: Config):
        """
        Initialize pipeline orchestrator with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize components
        self.extractor = QuoteExtractor(config)
        self.generator = ImageGenerator(config)
        self.publishers: Dict[str, BasePublisher] = {}
        
        logger.info("PipelineOrchestrator initialized")
    
    def run(
        self,
        episode_numbers: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        publish: bool = False,
        dry_run: bool = False
    ) -> PipelineResult:
        """
        Execute the full pipeline.
        
        Args:
            episode_numbers: List of episode numbers to process (None = all episodes)
            platforms: List of platforms to generate images for (None = all configured)
            publish: Whether to publish to social media
            dry_run: If True, generate images but don't publish
            
        Returns:
            PipelineResult with execution summary
        """
        start_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info("Starting pipeline execution")
        logger.info(f"Episodes: {episode_numbers or 'all'}")
        logger.info(f"Platforms: {platforms or 'all configured'}")
        logger.info(f"Publish: {publish}")
        logger.info(f"Dry run: {dry_run}")
        logger.info("=" * 60)
        
        # Initialize publishers if publishing is enabled
        if publish and not dry_run:
            self._init_publishers(platforms)
        
        # Extract episodes
        episodes = self._extract_episodes(episode_numbers)
        
        if not episodes:
            logger.warning("No episodes to process")
            return PipelineResult(
                total_episodes=0,
                successful_images=0,
                failed_images=0,
                successful_posts=0,
                failed_posts=0,
                results=[],
                start_time=start_time,
                end_time=datetime.now()
            )
        
        # Determine platforms to use
        target_platforms = self._determine_platforms(platforms)
        
        if not target_platforms:
            logger.error("No platforms configured or specified")
            return PipelineResult(
                total_episodes=len(episodes),
                successful_images=0,
                failed_images=0,
                successful_posts=0,
                failed_posts=0,
                results=[],
                start_time=start_time,
                end_time=datetime.now()
            )
        
        logger.info(f"Processing {len(episodes)} episodes for platforms: {', '.join(target_platforms)}")
        
        # Process each episode
        results = []
        for episode in episodes:
            result = self._process_episode(
                episode,
                target_platforms,
                publish,
                dry_run
            )
            results.append(result)
        
        # Calculate summary statistics
        total_episodes = len(results)
        successful_images = sum(r.images_generated for r in results)
        failed_images = sum(
            len(target_platforms) - r.images_generated 
            for r in results
        )
        successful_posts = sum(r.posts_published for r in results)
        failed_posts = sum(
            len(r.publish_results) - r.posts_published 
            for r in results
        )
        
        end_time = datetime.now()
        
        pipeline_result = PipelineResult(
            total_episodes=total_episodes,
            successful_images=successful_images,
            failed_images=failed_images,
            successful_posts=successful_posts,
            failed_posts=failed_posts,
            results=results,
            start_time=start_time,
            end_time=end_time
        )
        
        # Log summary
        logger.info("\n" + pipeline_result.get_summary())
        
        return pipeline_result
    
    def _init_publishers(self, platforms: Optional[List[str]] = None) -> None:
        """
        Initialize enabled publishers based on configuration.
        
        Args:
            platforms: List of platforms to initialize (None = all enabled)
        """
        logger.info("Initializing publishers...")
        
        # Determine which platforms to initialize
        enabled_platforms = self.config.social_media_settings.enabled_platforms
        
        if platforms:
            # Only initialize requested platforms that are also enabled
            platforms_to_init = [p for p in platforms if p in enabled_platforms]
        else:
            # Initialize all enabled platforms
            platforms_to_init = enabled_platforms
        
        # Import publisher classes dynamically to avoid circular imports
        for platform in platforms_to_init:
            try:
                publisher = self._create_publisher(platform)
                
                # Authenticate with the platform
                if publisher.authenticate():
                    self.publishers[platform] = publisher
                    logger.info(f"✓ Initialized {platform} publisher")
                else:
                    logger.error(f"✗ Failed to authenticate with {platform}")
                    
            except Exception as e:
                logger.error(f"✗ Failed to initialize {platform} publisher: {e}")
        
        if not self.publishers:
            logger.warning("No publishers initialized. Publishing will be skipped.")
    
    def _create_publisher(self, platform: str) -> BasePublisher:
        """
        Create a publisher instance for the specified platform.
        
        Args:
            platform: Platform name (twitter, instagram, facebook, linkedin)
            
        Returns:
            Publisher instance
            
        Raises:
            ValueError: If platform is not supported
        """
        if platform == "twitter":
            from .publishers.twitter_publisher import TwitterPublisher
            return TwitterPublisher(self.config)
        elif platform == "instagram":
            from .publishers.instagram_publisher import InstagramPublisher
            return InstagramPublisher(self.config)
        elif platform == "facebook":
            from .publishers.facebook_publisher import FacebookPublisher
            return FacebookPublisher(self.config)
        elif platform == "linkedin":
            from .publishers.linkedin_publisher import LinkedInPublisher
            return LinkedInPublisher(self.config)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def _extract_episodes(
        self, 
        episode_numbers: Optional[List[str]]
    ) -> List[EpisodeQuote]:
        """
        Extract episodes based on specified episode numbers.
        
        Args:
            episode_numbers: List of episode numbers (None = all episodes)
            
        Returns:
            List of EpisodeQuote objects
        """
        logger.info("Extracting episodes...")
        
        if episode_numbers:
            # Extract specific episodes
            episodes = []
            for episode_num in episode_numbers:
                logger.info(f"Extracting episode {episode_num}...")
                episode = self.extractor.extract_episode(episode_num)
                if episode:
                    episodes.append(episode)
                else:
                    logger.warning(f"Failed to extract episode {episode_num}")
        else:
            # Extract all episodes
            logger.info("Extracting all episodes...")
            episodes = self.extractor.extract_all_episodes()
        
        logger.info(f"Successfully extracted {len(episodes)} episodes")
        return episodes
    
    def _determine_platforms(
        self, 
        platforms: Optional[List[str]]
    ) -> List[str]:
        """
        Determine which platforms to generate images for.
        
        Args:
            platforms: Requested platforms (None = all configured)
            
        Returns:
            List of platform names
        """
        # Get all configured platforms from image settings
        configured_platforms = list(self.config.image_settings.platforms.keys())
        
        if platforms:
            # Validate requested platforms
            valid_platforms = []
            for platform in platforms:
                if platform in configured_platforms:
                    valid_platforms.append(platform)
                else:
                    logger.warning(
                        f"Platform '{platform}' not configured in image settings. "
                        f"Available: {', '.join(configured_platforms)}"
                    )
            return valid_platforms
        else:
            # Use all configured platforms
            return configured_platforms
    
    def _process_episode(
        self,
        quote_data: EpisodeQuote,
        platforms: List[str],
        publish: bool,
        dry_run: bool
    ) -> EpisodeResult:
        """
        Process a single episode through the pipeline.
        
        Args:
            quote_data: Episode quote data (can be a single quote or first of multiple)
            platforms: List of platforms to generate images for
            publish: Whether to publish to social media
            dry_run: If True, generate images but don't publish
            
        Returns:
            EpisodeResult with processing details
        """
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Processing Episode {quote_data.episode_number}: {quote_data.titolo}")
        logger.info(f"{'=' * 60}")
        
        result = EpisodeResult(
            episode_number=quote_data.episode_number,
            success=True
        )
        
        # Extract all quotes for this episode (all 4 sources)
        all_quotes = self.extractor.extract_all_quotes_for_episode(quote_data.episode_number)
        
        if not all_quotes:
            logger.warning(f"No quotes found for episode {quote_data.episode_number}")
            result.success = False
            result.errors.append("No quotes found for episode")
            return result
        
        logger.info(f"Found {len(all_quotes)} quotes for episode {quote_data.episode_number}")
        
        # Filter quotes based on preferred source if specified
        preferred_source = self.config.quote_settings.preferred_source
        if preferred_source and preferred_source != 'random':
            # Filter to only the preferred source
            filtered_quotes = [q for q in all_quotes if q.quote_source == preferred_source]
            if filtered_quotes:
                all_quotes = filtered_quotes
                logger.info(f"Filtered to {len(all_quotes)} quote(s) from source: {preferred_source}")
            else:
                logger.warning(f"No quotes found from preferred source '{preferred_source}', using all quotes")
        
        # Generate images for each quote × each platform
        for quote in all_quotes:
            for platform in platforms:
                try:
                    logger.info(f"Generating {quote.quote_source} image for {platform}...")
                    generated_image = self.generator.generate(quote, platform)
                    result.generated_images.append(generated_image)
                    logger.info(f"✓ Generated {quote.quote_source}/{platform} image: {generated_image.file_path}")
                    
                    # Publish if enabled
                    if publish:
                        if dry_run:
                            logger.info(f"[DRY RUN] Would publish {quote.quote_source} to {platform}")
                            # Create a mock publish result for dry run
                            publish_result = PublishResult(
                                success=True,
                                platform=platform,
                                post_url=f"[DRY RUN] {platform} post"
                            )
                            result.publish_results.append(publish_result)
                        else:
                            # Actually publish
                            publish_result = self._publish_image(
                                platform,
                                generated_image.file_path,
                                quote
                            )
                            result.publish_results.append(publish_result)
                            
                            if publish_result.success:
                                logger.info(f"✓ {publish_result}")
                            else:
                                logger.error(f"✗ {publish_result}")
                                result.errors.append(
                                    f"Failed to publish {quote.quote_source} to {platform}: {publish_result.error}"
                                )
                    
                except Exception as e:
                    error_msg = f"Failed to generate {quote.quote_source}/{platform} image: {e}"
                    logger.error(error_msg, exc_info=True)
                    result.errors.append(error_msg)
                    result.success = False
        
        # Overall success if at least one image was generated
        if not result.generated_images:
            result.success = False
            result.errors.append("No images were generated")
        
        return result
    
    def _publish_image(
        self,
        platform: str,
        image_path: str,
        quote_data: EpisodeQuote
    ) -> PublishResult:
        """
        Publish an image to a specific platform.
        
        Args:
            platform: Platform name
            image_path: Path to generated image
            quote_data: Episode quote data
            
        Returns:
            PublishResult with publish status
        """
        # Check if publisher is initialized
        if platform not in self.publishers:
            return PublishResult(
                success=False,
                platform=platform,
                error=f"Publisher not initialized for {platform}"
            )
        
        publisher = self.publishers[platform]
        
        try:
            logger.info(f"Publishing to {platform}...")
            return publisher.publish(image_path, quote_data, dry_run=False)
        except Exception as e:
            logger.error(f"Failed to publish to {platform}: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform=platform,
                error=str(e)
            )
