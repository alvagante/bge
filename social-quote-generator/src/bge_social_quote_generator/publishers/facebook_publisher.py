"""Facebook publisher implementation."""

import logging
from typing import Optional

import facebook
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


class FacebookPublisher(BasePublisher):
    """
    Publisher for Facebook platform.
    
    Uses facebook-sdk library to authenticate and post photos with captions.
    Implements retry logic with exponential backoff for transient errors.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Facebook publisher.
        
        Args:
            config: Configuration object with Facebook credentials
            
        Raises:
            ValueError: If Facebook is not configured or enabled
        """
        super().__init__(config)
        
        self.graph: Optional[facebook.GraphAPI] = None
        self._authenticated = False
        self._page_id: Optional[str] = None
    
    def _get_platform_name(self) -> str:
        """Get platform name."""
        return "facebook"
    
    def authenticate(self) -> bool:
        """
        Authenticate with Facebook Graph API.
        
        Uses access token authentication. Requires a Page Access Token
        to post to a Facebook Page.
        
        Returns:
            True if authentication succeeded
            
        Raises:
            facebook.GraphAPIError: If authentication fails
            ValueError: If credentials are missing or invalid
        """
        credentials = self.platform_settings.credentials
        
        # Validate credentials are present
        required_creds = ["access_token"]
        missing_creds = []
        
        for cred in required_creds:
            value = credentials.get(cred, "")
            if not value or value.startswith("${") or value.startswith("your_"):
                missing_creds.append(cred)
        
        if missing_creds:
            raise ValueError(
                f"Facebook credentials missing or not configured: {', '.join(missing_creds)}. "
                f"Please set them in your configuration file or environment variables. "
                f"You need a Page Access Token to post to Facebook."
            )
        
        try:
            # Create Facebook Graph API client
            access_token = credentials["access_token"]
            self.graph = facebook.GraphAPI(access_token=access_token)
            
            # Get page ID (required for posting)
            self._page_id = credentials.get("page_id")
            
            if not self._page_id or self._page_id.startswith("${") or self._page_id.startswith("your_"):
                # Try to get page ID from token
                try:
                    me = self.graph.get_object("me")
                    self._page_id = me.get("id")
                    logger.debug(f"Retrieved page ID from token: {self._page_id}")
                except Exception as e:
                    raise ValueError(
                        f"Facebook page_id not configured and could not be retrieved from token. "
                        f"Please set page_id in your configuration."
                    ) from e
            
            # Verify authentication by getting page info
            try:
                page_info = self.graph.get_object(self._page_id)
                page_name = page_info.get("name", "Unknown")
                logger.info(f"✓ Authenticated with Facebook Page: {page_name} (ID: {self._page_id})")
            except facebook.GraphAPIError as e:
                raise ValueError(
                    f"Failed to access Facebook Page (ID: {self._page_id}). "
                    f"Please check your access token has the required permissions."
                ) from e
            
            self._authenticated = True
            return True
            
        except facebook.GraphAPIError as e:
            logger.error(f"Facebook authentication failed: {e}")
            raise ValueError(
                f"Facebook authentication failed: {e}. "
                f"Please check your access token and permissions."
            ) from e
            
        except Exception as e:
            logger.error(f"Facebook authentication failed: {e}")
            raise
    
    @retry(
        retry=retry_if_exception_type(facebook.GraphAPIError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _upload_photo_with_retry(self, image_path: str, caption: str) -> dict:
        """
        Upload photo to Facebook with retry logic.
        
        Args:
            image_path: Path to image file
            caption: Photo caption/message
            
        Returns:
            Response dict with post information
            
        Raises:
            facebook.GraphAPIError: If upload fails after retries
        """
        logger.debug(f"Uploading photo to Facebook Page {self._page_id}: {image_path}")
        
        # Open image file
        with open(image_path, "rb") as image_file:
            # Post photo to page
            response = self.graph.put_photo(
                image=image_file,
                message=caption
            )
        
        logger.debug(f"Photo uploaded successfully: {response.get('id')}")
        return response
    
    def publish(
        self,
        image_path: str,
        quote_data: EpisodeQuote,
        dry_run: bool = False
    ) -> PublishResult:
        """
        Publish image with caption to Facebook.
        
        Workflow:
        1. Generate caption from template
        2. (Dry-run mode: skip remaining steps)
        3. Validate image file exists
        4. Authenticate if not already authenticated
        5. Upload photo with caption to Facebook Page
        6. Return result with post URL
        
        Args:
            image_path: Path to image file to publish
            quote_data: Episode quote data for caption generation
            dry_run: If True, generate caption but don't actually publish
            
        Returns:
            PublishResult with success status and post URL or error
        """
        try:
            # Generate caption
            caption = self._generate_caption(quote_data)
            logger.info(f"Generated caption ({len(caption)} chars): {caption[:100]}...")
            
            # Check caption length (Facebook limit is 63,206 characters, but keep it reasonable)
            if len(caption) > 5000:
                logger.warning(
                    f"Caption is very long ({len(caption)} chars). "
                    f"Consider shortening for better engagement."
                )
            
            # Dry run mode - don't actually publish
            if dry_run:
                logger.info(f"[DRY RUN] Would publish to Facebook:")
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
            
            # Upload photo with caption
            try:
                response = self._upload_photo_with_retry(image_path, caption)
                
                # Construct post URL
                post_id = response.get("post_id") or response.get("id")
                if post_id:
                    # Facebook post URL format: https://www.facebook.com/{page_id}/posts/{post_id}
                    post_url = f"https://www.facebook.com/{post_id}"
                else:
                    post_url = f"https://www.facebook.com/{self._page_id}"
                
                logger.info(f"✓ Successfully published to Facebook: {post_url}")
                
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    post_url=post_url
                )
                
            except facebook.GraphAPIError as e:
                error_msg = f"Failed to upload photo: {e}"
                logger.error(error_msg)
                
                # Provide helpful error messages for common issues
                if "permissions" in str(e).lower():
                    error_msg += " (Check that your access token has 'pages_manage_posts' permission)"
                elif "token" in str(e).lower():
                    error_msg += " (Your access token may have expired)"
                
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
