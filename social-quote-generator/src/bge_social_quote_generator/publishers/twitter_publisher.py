"""Twitter/X publisher implementation."""

import logging
from typing import Optional

import tweepy
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from ..config import Config
from ..extractors.base import EpisodeQuote
from .base import BasePublisher, PublishResult


logger = logging.getLogger(__name__)


class TwitterPublisher(BasePublisher):
    """
    Publisher for Twitter/X platform.
    
    Uses tweepy library to authenticate and post images with captions.
    Implements retry logic with exponential backoff for transient errors.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Twitter publisher.
        
        Args:
            config: Configuration object with Twitter credentials
            
        Raises:
            ValueError: If Twitter is not configured or enabled
        """
        super().__init__(config)
        
        self.api_v1: Optional[tweepy.API] = None
        self.client: Optional[tweepy.Client] = None
        self._authenticated = False
    
    def _get_platform_name(self) -> str:
        """Get platform name."""
        return "twitter"
    
    def authenticate(self) -> bool:
        """
        Authenticate with Twitter API.
        
        Uses OAuth 1.0a authentication with API keys and access tokens.
        Creates both API v1.1 client (for media upload) and v2 client (for tweeting).
        
        Returns:
            True if authentication succeeded
            
        Raises:
            tweepy.TweepyException: If authentication fails
            ValueError: If credentials are missing or invalid
        """
        credentials = self.platform_settings.credentials
        
        # Validate credentials are present
        required_creds = ["api_key", "api_secret", "access_token", "access_token_secret"]
        missing_creds = []
        
        for cred in required_creds:
            value = credentials.get(cred, "")
            if not value or value.startswith("${") or value.startswith("your_"):
                missing_creds.append(cred)
        
        if missing_creds:
            raise ValueError(
                f"Twitter credentials missing or not configured: {', '.join(missing_creds)}. "
                f"Please set them in your configuration file or environment variables."
            )
        
        try:
            # Create OAuth 1.0a handler for API v1.1 (media upload)
            auth = tweepy.OAuth1UserHandler(
                consumer_key=credentials["api_key"],
                consumer_secret=credentials["api_secret"],
                access_token=credentials["access_token"],
                access_token_secret=credentials["access_token_secret"]
            )
            
            # Create API v1.1 client for media upload
            self.api_v1 = tweepy.API(auth)
            
            # Create API v2 client for tweeting
            self.client = tweepy.Client(
                consumer_key=credentials["api_key"],
                consumer_secret=credentials["api_secret"],
                access_token=credentials["access_token"],
                access_token_secret=credentials["access_token_secret"]
            )
            
            # Verify credentials by getting authenticated user
            user = self.api_v1.verify_credentials()
            logger.info(f"✓ Authenticated with Twitter as @{user.screen_name}")
            
            self._authenticated = True
            return True
            
        except tweepy.Unauthorized as e:
            logger.error(f"Twitter authentication failed: Invalid credentials")
            raise ValueError(
                f"Twitter authentication failed: Invalid credentials. "
                f"Please check your API keys and access tokens."
            ) from e
            
        except tweepy.TweepyException as e:
            logger.error(f"Twitter authentication failed: {e}")
            raise
    
    @retry(
        retry=retry_if_exception_type((tweepy.TooManyRequests, tweepy.TwitterServerError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _upload_media_with_retry(self, image_path: str) -> tweepy.Media:
        """
        Upload media to Twitter with retry logic.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Media object with media_id
            
        Raises:
            tweepy.TweepyException: If upload fails after retries
        """
        logger.debug(f"Uploading media: {image_path}")
        media = self.api_v1.media_upload(filename=image_path)
        logger.debug(f"Media uploaded successfully: {media.media_id}")
        return media
    
    @retry(
        retry=retry_if_exception_type((tweepy.TooManyRequests, tweepy.TwitterServerError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _create_tweet_with_retry(self, text: str, media_ids: list) -> tweepy.Response:
        """
        Create tweet with retry logic.
        
        Args:
            text: Tweet text/caption
            media_ids: List of media IDs to attach
            
        Returns:
            Response object with tweet data
            
        Raises:
            tweepy.TweepyException: If tweet creation fails after retries
        """
        logger.debug(f"Creating tweet with {len(media_ids)} media attachment(s)")
        response = self.client.create_tweet(text=text, media_ids=media_ids)
        logger.debug(f"Tweet created successfully: {response.data}")
        return response
    
    def publish(
        self,
        image_path: str,
        quote_data: EpisodeQuote,
        dry_run: bool = False
    ) -> PublishResult:
        """
        Publish image with caption to Twitter.
        
        Workflow:
        1. Generate caption from template
        2. (Dry-run mode: skip remaining steps)
        3. Validate image file exists
        4. Authenticate if not already authenticated
        5. Upload image (API v1.1)
        6. Create tweet with image (API v2)
        7. Return result with tweet URL
        
        Args:
            image_path: Path to image file to publish
            quote_data: Episode quote data for caption generation
            dry_run: If True, generate caption but don't actually publish
            
        Returns:
            PublishResult with success status and tweet URL or error
        """
        try:
            # Generate caption
            caption = self._generate_caption(quote_data)
            logger.info(f"Generated caption ({len(caption)} chars): {caption[:100]}...")
            
            # Check caption length (Twitter limit is 280 characters)
            if len(caption) > 280:
                logger.warning(
                    f"Caption exceeds Twitter's 280 character limit ({len(caption)} chars). "
                    f"It will be truncated."
                )
                caption = caption[:277] + "..."
            
            # Dry run mode - don't actually publish
            if dry_run:
                logger.info(f"[DRY RUN] Would publish to Twitter:")
                logger.info(f"  Image: {image_path}")
                logger.info(f"  Caption: {caption}")
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    post_url="[DRY RUN - not published]"
                )
            
            # Validate image file (only when actually publishing)
            self._validate_image_path(image_path)
            
            # Authenticate if not already authenticated
            if not self._authenticated:
                self.authenticate()
            
            # Upload media
            try:
                media = self._upload_media_with_retry(image_path)
            except tweepy.TweepyException as e:
                error_msg = f"Failed to upload media: {e}"
                logger.error(error_msg)
                return PublishResult(
                    success=False,
                    platform=self.platform_name,
                    error=error_msg
                )
            
            # Create tweet with media
            try:
                response = self._create_tweet_with_retry(caption, [media.media_id])
                tweet_id = response.data["id"]
                
                # Get authenticated user for tweet URL
                user = self.api_v1.verify_credentials()
                tweet_url = f"https://twitter.com/{user.screen_name}/status/{tweet_id}"
                
                logger.info(f"✓ Successfully published to Twitter: {tweet_url}")
                
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    post_url=tweet_url
                )
                
            except tweepy.TweepyException as e:
                error_msg = f"Failed to create tweet: {e}"
                logger.error(error_msg)
                return PublishResult(
                    success=False,
                    platform=self.platform_name,
                    error=error_msg
                )
        
        except FileNotFoundError as e:
            error_msg = f"Image file not found: {e}"
            logger.error(error_msg)
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error=error_msg
            )
        
        except ValueError as e:
            error_msg = f"Configuration or validation error: {e}"
            logger.error(error_msg)
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg, exc_info=True)
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error=error_msg
            )
